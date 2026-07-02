from functools import lru_cache

from app.ai.providers.base import LlmProvider
from app.ai.providers.deepseek import DeepSeekProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.groq import GroqProvider
from app.ai.providers.openrouter import OpenRouterProvider
from app.ai.providers.qwen import QwenProvider
from app.ai.service import AIGatewayService
from app.ai.settings import build_provider_configs
from app.core.config import get_settings


@lru_cache
def get_ai_gateway() -> AIGatewayService:
    """Build the process-wide AIGatewayService singleton (FastAPI dependency).

    Adding a new provider: implement it under app/ai/providers/, add its env
    vars to app/core/config.py + build_provider_configs, and register it in
    the dict below — no other call site needs to change.
    """
    settings = get_settings()
    cfg = build_provider_configs(settings)
    providers: dict[str, LlmProvider] = {
        "deepseek": DeepSeekProvider(cfg["deepseek"]),
        "gemini": GeminiProvider(cfg["gemini"]),
        "groq": GroqProvider(cfg["groq"]),
        "qwen": QwenProvider(cfg["qwen"]),
        "openrouter": OpenRouterProvider(cfg["openrouter"]),
    }
    return AIGatewayService(providers=providers, settings=settings)
