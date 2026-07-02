from app.ai.providers.openai_compatible import OpenAICompatibleProvider

KEY = "groq"


class GroqProvider(OpenAICompatibleProvider):
    """Groq-hosted Llama (OpenAI-compatible Chat Completions).

    Groq speaks the same ``/chat/completions`` protocol as NVIDIA NIM and
    OpenRouter, so this is a thin subclass with no transport code of its
    own — it only joins the failover chain when ``GROQ_API_KEY`` is set.
    """
