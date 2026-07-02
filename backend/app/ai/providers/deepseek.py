from app.ai.providers.openai_compatible import OpenAICompatibleProvider

KEY = "deepseek"


class DeepSeekProvider(OpenAICompatibleProvider):
    """DeepSeek's OpenAI-compatible Chat Completions API.

    Thin subclass with no transport code of its own — everything comes from
    :class:`OpenAICompatibleProvider`. Kept as its own class (rather than a
    bare instance) so future providers follow the same one-class-per-vendor
    pattern.
    """
