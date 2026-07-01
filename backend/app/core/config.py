from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, populated from environment variables.

    See ../../.env.example at the repo root for the full variable list.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DBPilot AI"
    app_version: str = "0.1.0"
    backend_env: str = "development"

    database_url: str = "postgresql+psycopg://user:password@localhost:5432/dbpilot"
    deepseek_api_key: str = ""
    deepseek_api_base: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    allowed_origins: str = "http://localhost:3000"
    secret_key: str = "change-me-in-production"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
