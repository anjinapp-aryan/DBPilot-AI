from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, populated from environment variables.

    See ../../.env.example at the repo root for the full variable list.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    app_name: str = "DBPilot AI"
    app_version: str = "0.1.0"
    backend_env: str = "development"

    database_url: str = "postgresql+psycopg://user:password@localhost:5432/dbpilot"

    allowed_origins: str = "http://localhost:3000"
    secret_key: str = "change-me-in-production"

    # --- AI Gateway: routing ---
    primary_provider: str = "deepseek"
    ai_provider_order: str = "deepseek,gemini,groq,qwen,openrouter"
    ai_gateway_default_temperature: float = 0.4

    # --- NVIDIA-hosted models (DeepSeek + Qwen share base URL / timeout) ---
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_timeout_ms: int = 20_000

    # DEEP_SHEEK_NVIDIA_API_KEY matches the spelling already used in the
    # upstream (CareerPilot AI) project's env/config — kept identical here
    # so an existing .env can be reused without editing.
    deepseek_nvidia_api_key: str = Field(default="", validation_alias="DEEP_SHEEK_NVIDIA_API_KEY")
    nvidia_deepseek_model: str = "deepseek-ai/deepseek-v4-flash"
    deepseek_display_name: str = "DeepSeek"

    qwen3_nvidia_api_key: str = ""
    nvidia_qwen_model: str = "qwen/qwen3-next-80b-a3b-instruct"
    qwen_display_name: str = "Qwen"

    # --- Groq ---
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout_ms: int = 20_000
    groq_display_name: str = "Groq"

    # --- Gemini (native REST API, not OpenAI-compatible) ---
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    gemini_model: str = "gemini-2.5-flash"
    gemini_timeout_ms: int = 20_000
    gemini_display_name: str = "Gemini"

    # --- OpenRouter (final fallback) ---
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = ""
    openrouter_timeout_ms: int = 20_000
    openrouter_display_name: str = "OpenRouter"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def ai_provider_order_list(self) -> list[str]:
        return [key.strip() for key in self.ai_provider_order.split(",") if key.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
