import warnings
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production"]

_PLACEHOLDER_SECRET_KEY = "change-me-in-production"
_MIN_PRODUCTION_SECRET_KEY_LENGTH = 16
_SUSPICIOUS_PRODUCTION_ORIGINS = {"*", "http://localhost:3000"}


class Settings(BaseSettings):
    """Application configuration, populated from environment variables.

    See ../../.env.example at the repo root for the full variable list.
    Production safety checks (below) run once, at construction time —
    the app refuses to boot rather than run insecurely configured.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    app_name: str = "DBPilot AI"
    app_version: str = "0.1.0"
    backend_env: Environment = "development"

    database_url: str = "postgresql+psycopg://user:password@localhost:5432/dbpilot"

    allowed_origins: str = "http://localhost:3000"
    allowed_hosts: str = "*"
    secret_key: str = "change-me-in-production"
    rate_limit_default: str = "60/minute"

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
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]

    @property
    def ai_provider_order_list(self) -> list[str]:
        return [key.strip() for key in self.ai_provider_order.split(",") if key.strip()]

    @model_validator(mode="after")
    def _validate_production_safety(self) -> "Settings":
        if self.backend_env != "production":
            return self

        if self.secret_key == _PLACEHOLDER_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY is still the placeholder default — set a real secret "
                "before running with BACKEND_ENV=production."
            )
        if len(self.secret_key) < _MIN_PRODUCTION_SECRET_KEY_LENGTH:
            raise ValueError(
                f"SECRET_KEY must be at least {_MIN_PRODUCTION_SECRET_KEY_LENGTH} "
                "characters when BACKEND_ENV=production."
            )
        if not self.allowed_origins_list:
            raise ValueError(
                "ALLOWED_ORIGINS must be set when BACKEND_ENV=production "
                "(refusing to boot with no configured CORS origins)."
            )
        if _SUSPICIOUS_PRODUCTION_ORIGINS & set(self.allowed_origins_list):
            warnings.warn(
                "ALLOWED_ORIGINS includes a wildcard or localhost origin while "
                "BACKEND_ENV=production — verify this is intentional.",
                stacklevel=2,
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
