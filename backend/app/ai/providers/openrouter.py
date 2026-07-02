from app.ai.providers.openai_compatible import OpenAICompatibleProvider

KEY = "openrouter"


class OpenRouterProvider(OpenAICompatibleProvider):
    """OpenRouter (OpenAI-compatible Chat Completions).

    Appended LAST in the default failover order — a broad-catalog final
    fallback, never a priority provider. Stays NOT_CONFIGURED (and is
    skipped) until both ``OPENROUTER_API_KEY`` and ``OPENROUTER_MODEL`` are
    set.
    """
