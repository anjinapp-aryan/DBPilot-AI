from app.ai.providers.openai_compatible import OpenAICompatibleProvider

KEY = "qwen"


class QwenProvider(OpenAICompatibleProvider):
    """NVIDIA-hosted Qwen (OpenAI-compatible Chat Completions).

    Shares the NVIDIA NIM base URL with :class:`DeepSeekProvider` but uses
    its own dedicated API key (``QWEN3_NVIDIA_API_KEY``) and model.
    """
