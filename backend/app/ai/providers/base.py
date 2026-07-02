from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.ai.chat_message import ChatMessage


class LlmProvider(ABC):
    """Contract every LLM provider implements.

    Business code never depends on this directly — it goes through
    ``AIGatewayService``, which routes across providers with automatic
    failover. Adding a new provider (Groq, OpenRouter, Gemini, ...) means
    writing one new implementation and listing it in ``AI_PROVIDER_ORDER`` —
    no business-logic changes.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable key used in config/metrics/circuit-breaker names (e.g. "deepseek")."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-friendly name used in logs (e.g. "DeepSeek")."""

    @abstractmethod
    def is_configured(self) -> bool:
        """True when this provider has the credentials it needs to be called."""

    @property
    @abstractmethod
    def timeout_seconds(self) -> float:
        """Per-provider request timeout."""

    @abstractmethod
    async def chat(
        self, messages: list[ChatMessage], system: str | None, temperature: float
    ) -> str:
        """Multi-turn, non-streaming completion."""

    @abstractmethod
    def stream_chat(
        self, messages: list[ChatMessage], system: str | None, temperature: float
    ) -> AsyncIterator[str]:
        """Multi-turn, streaming completion (token deltas)."""
