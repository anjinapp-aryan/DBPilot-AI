from dataclasses import dataclass

from app.core.config import Settings


@dataclass(frozen=True)
class ProviderConfig:
    """Settings for a single LLM provider — mirrors AiGatewayProperties.Provider."""

    key: str
    display_name: str
    api_key: str | None
    model: str | None
    base_url: str | None
    timeout_ms: int = 20_000

    @property
    def timeout_seconds(self) -> float:
        return self.timeout_ms / 1000


def build_provider_configs(settings: Settings) -> dict[str, ProviderConfig]:
    """Build the provider-config map from environment-backed settings.

    Failover order (see AI_PROVIDER_ORDER): DeepSeek (NVIDIA-hosted) → Gemini
    → Groq → Qwen (NVIDIA-hosted) → OpenRouter. Every provider is skipped by
    the gateway unless its api_key and model are both set — so this map can
    be built unconditionally even when most keys are blank.
    """
    return {
        "deepseek": ProviderConfig(
            key="deepseek",
            display_name=settings.deepseek_display_name,
            api_key=settings.deepseek_nvidia_api_key or None,
            model=settings.nvidia_deepseek_model or None,
            base_url=settings.nvidia_base_url or None,
            timeout_ms=settings.nvidia_timeout_ms,
        ),
        "qwen": ProviderConfig(
            key="qwen",
            display_name=settings.qwen_display_name,
            api_key=settings.qwen3_nvidia_api_key or None,
            model=settings.nvidia_qwen_model or None,
            base_url=settings.nvidia_base_url or None,
            timeout_ms=settings.nvidia_timeout_ms,
        ),
        "groq": ProviderConfig(
            key="groq",
            display_name=settings.groq_display_name,
            api_key=settings.groq_api_key or None,
            model=settings.groq_model or None,
            base_url=settings.groq_base_url or None,
            timeout_ms=settings.groq_timeout_ms,
        ),
        "gemini": ProviderConfig(
            key="gemini",
            display_name=settings.gemini_display_name,
            api_key=settings.gemini_api_key or None,
            model=settings.gemini_model or None,
            base_url=settings.gemini_base_url or None,
            timeout_ms=settings.gemini_timeout_ms,
        ),
        "openrouter": ProviderConfig(
            key="openrouter",
            display_name=settings.openrouter_display_name,
            api_key=settings.openrouter_api_key or None,
            model=settings.openrouter_model or None,
            base_url=settings.openrouter_base_url or None,
            timeout_ms=settings.openrouter_timeout_ms,
        ),
    }
