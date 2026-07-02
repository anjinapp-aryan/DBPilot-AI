import json
from collections.abc import AsyncIterator

import httpx

from app.ai.chat_message import ChatMessage
from app.ai.exceptions import QuotaExceededError
from app.ai.providers.base import LlmProvider
from app.ai.settings import ProviderConfig


class OpenAICompatibleProvider(LlmProvider):
    """Base for any OpenAI-compatible Chat Completions API (``/chat/completions``).

    DeepSeek, Groq, OpenRouter, and NVIDIA-hosted models all speak this
    protocol, so a single base supports every one of them — a new provider
    is one subclass pointing at its own :class:`ProviderConfig`.
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
        return httpx.AsyncClient(
            base_url=self.cfg.base_url or "",
            headers={"Authorization": f"Bearer {self.cfg.api_key or ''}"},
            timeout=self.timeout_seconds,
        )

    def _messages_payload(
        self, messages: list[ChatMessage], system: str | None
    ) -> list[dict[str, str]]:
        payload: list[dict[str, str]] = []
        if system:
            payload.append({"role": "system", "content": system})
        for m in messages:
            role = "assistant" if m.role == "model" else "user"
            payload.append({"role": role, "content": m.content})
        return payload

    async def chat(
        self, messages: list[ChatMessage], system: str | None, temperature: float
    ) -> str:
        body = {
            "model": self.cfg.model,
            "messages": self._messages_payload(messages, system),
            "temperature": temperature,
            "stream": False,
        }
        async with self._client() as client:
            response = await client.post("/chat/completions", json=body)
        if response.status_code == 429:
            raise QuotaExceededError(f"{self.display_name} 429 quota/rate limit")
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            return ""
        return (choices[0].get("message", {}).get("content") or "").strip()

    async def stream_chat(
        self, messages: list[ChatMessage], system: str | None, temperature: float
    ) -> AsyncIterator[str]:
        body = {
            "model": self.cfg.model,
            "messages": self._messages_payload(messages, system),
            "temperature": temperature,
            "stream": True,
        }
        async with (
            self._client() as client,
            client.stream("POST", "/chat/completions", json=body) as response,
        ):
            if response.status_code == 429:
                raise QuotaExceededError(f"{self.display_name} 429 quota/rate limit")
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data_str = line[len("data:") :].strip()
                if data_str == "[DONE]":
                    break
                delta = self._extract_delta(data_str)
                if delta:
                    yield delta

    @staticmethod
    def _extract_delta(data_str: str) -> str:
        try:
            node = json.loads(data_str)
        except ValueError:
            return ""
        choices = node.get("choices") or []
        if not choices:
            return ""
        return choices[0].get("delta", {}).get("content", "") or ""
