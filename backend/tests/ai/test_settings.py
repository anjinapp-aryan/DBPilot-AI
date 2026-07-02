from app.ai.settings import build_provider_configs
from app.core.config import Settings


def test_build_provider_configs_reads_deepseek_nvidia_settings() -> None:
    settings = Settings(
        deepseek_nvidia_api_key="test-nvidia-key",
        nvidia_deepseek_model="deepseek-ai/deepseek-v4-flash",
        nvidia_base_url="https://integrate.api.nvidia.com/v1",
        nvidia_timeout_ms=15_000,
    )

    configs = build_provider_configs(settings)

    assert configs["deepseek"].api_key == "test-nvidia-key"
    assert configs["deepseek"].model == "deepseek-ai/deepseek-v4-flash"
    assert configs["deepseek"].base_url == "https://integrate.api.nvidia.com/v1"
    assert configs["deepseek"].timeout_seconds == 15.0


def test_deepseek_nvidia_api_key_reads_deep_sheek_alias(monkeypatch) -> None:
    monkeypatch.setenv("DEEP_SHEEK_NVIDIA_API_KEY", "test-nvidia-alias-key")
    settings = Settings()
    assert settings.deepseek_nvidia_api_key == "test-nvidia-alias-key"


def test_build_provider_configs_blank_api_key_becomes_none() -> None:
    settings = Settings(deepseek_nvidia_api_key="")
    configs = build_provider_configs(settings)
    assert configs["deepseek"].api_key is None


def test_build_provider_configs_covers_all_five_providers() -> None:
    settings = Settings()
    configs = build_provider_configs(settings)
    assert set(configs.keys()) == {"deepseek", "qwen", "groq", "gemini", "openrouter"}


def test_build_provider_configs_reads_groq_settings() -> None:
    settings = Settings(groq_api_key="test-groq-key", groq_model="llama-3.3-70b-versatile")
    configs = build_provider_configs(settings)
    assert configs["groq"].api_key == "test-groq-key"
    assert configs["groq"].model == "llama-3.3-70b-versatile"


def test_build_provider_configs_reads_gemini_settings() -> None:
    settings = Settings(gemini_api_key="gm-test", gemini_model="gemini-2.5-flash")
    configs = build_provider_configs(settings)
    assert configs["gemini"].api_key == "gm-test"
    assert configs["gemini"].model == "gemini-2.5-flash"


def test_build_provider_configs_openrouter_unconfigured_by_default() -> None:
    settings = Settings()
    configs = build_provider_configs(settings)
    assert configs["openrouter"].api_key is None
    assert configs["openrouter"].model is None


def test_ai_provider_order_list_parses_csv() -> None:
    settings = Settings(ai_provider_order="deepseek, groq ,gemini")
    assert settings.ai_provider_order_list == ["deepseek", "groq", "gemini"]


def test_default_ai_provider_order_matches_documented_chain() -> None:
    settings = Settings()
    assert settings.ai_provider_order_list == ["deepseek", "gemini", "groq", "qwen", "openrouter"]
