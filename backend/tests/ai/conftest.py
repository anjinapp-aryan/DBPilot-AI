from collections.abc import AsyncIterator

from app.ai.providers.base import LlmProvider


class FakeProvider(LlmProvider):
    """In-memory LlmProvider for gateway failover tests — no network calls."""

    def __init__(
        self,
        key: str,
        response: str | None = None,
        error: Exception | None = None,
        configured: bool = True,
    ) -> None:
        self._key = key
        self._response = response
        self._error = error
        self._configured = configured
        self.calls = 0

    @property
    def name(self) -> str:
        return self._key

    @property
    def display_name(self) -> str:
        return self._key.capitalize()

    def is_configured(self) -> bool:
        return self._configured

    @property
    def timeout_seconds(self) -> float:
        return 5.0

    async def chat(self, messages: list, system: str | None, temperature: float) -> str:
        self.calls += 1
        if self._error is not None:
            raise self._error
        return self._response or ""

    async def stream_chat(
        self, messages: list, system: str | None, temperature: float
    ) -> AsyncIterator[str]:
        self.calls += 1
        if self._error is not None:
            raise self._error
        for chunk in (self._response or "").split():
            yield chunk + " "
