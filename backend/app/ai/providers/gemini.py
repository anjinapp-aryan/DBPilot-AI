import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.ai.chat_message import ChatMessage
from app.ai.exceptions import QuotaExceededError
from app.ai.providers.base import LlmProvider
from app.ai.settings import ProviderConfig

KEY = "gemini"


class GeminiProvider(LlmProvider):
    """Google Gemini via its native v1beta REST API — not OpenAI-compatible.

    Implements ``:generateContent`` (chat) and ``:streamGenerateContent``
    (streaming, SSE-framed). ``ChatMessage.role`` already uses Gemini's own
    vocabulary ("user" / "model"), so no role remapping is needed here
    (contrast with :class:`OpenAICompatibleProvider`, which maps "model" to
    "assistant").
    """

    def __init__(self, cfg: ProviderConfig) -> None:
        self.cfg = cfg

    @property
    def name(self) -> str:
        return self.cfg.key

    @property
    def display_name(self) -> str:
        return self.cfg.display_name

    def is_configured(self) -> bool:
        return bool(self.cfg.api_key) and bool(self.cfg.model)

    @property
    def timeout_seconds(self) -> float:
        return self.cfg.timeout_seconds

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.cfg.base_url or "", timeout=self.timeout_seconds)

    def _build_body(
        self, messages: list[ChatMessage], system: str | None, temperature: float
    ) -> dict[str, Any]:
        contents = [{"role": m.role, "parts": [{"text": m.content}]} for m in messages]
        body: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature},
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        return body

    async def chat(
        self, messages: list[ChatMessage], system: str | None, temperature: float
    ) -> str:
        body = self._build_body(messages, system, temperature)
        async with self._client() as client:
            response = await client.post(
                f"/models/{self.cfg.model}:generateContent",
                params={"key": self.cfg.api_key},
                json=body,
            )
        if response.status_code == 429:
            raise QuotaExceededError(f"{self.display_name} 429 quota/rate limit")
        response.raise_for_status()
        return self._extract_text(response.json()).strip()

    async def stream_chat(
        self, messages: list[ChatMessage], system: str | None, temperature: float
    ) -> AsyncIterator[str]:
        body = self._build_body(messages, system, temperature)
        async with (
            self._client() as client,
            client.stream(
                "POST",
                f"/models/{self.cfg.model}:streamGenerateContent",
                params={"alt": "sse", "key": self.cfg.api_key},
                json=body,
            ) as response,
        ):
            if response.status_code == 429:
                raise QuotaExceededError(f"{self.display_name} 429 quota/rate limit")
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data_str = line[len("data:") :].strip()
                if not data_str:
                    continue
                text = self._extract_text_from_str(data_str)
                if text:
                    yield text

    def _extract_text_from_str(self, data_str: str) -> str:
        try:
            node = json.loads(data_str)
        except ValueError:
            return ""
        return self._extract_text(node)

    @staticmethod
    def _extract_text(resp: dict[str, Any]) -> str:
        candidates = resp.get("candidates") or []
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts") or []
        return "".join(p.get("text", "") for p in parts)
