import pytest

from app.ai.providers.groq import GroqProvider
from app.ai.providers.openrouter import OpenRouterProvider
from app.ai.providers.qwen import QwenProvider
from app.ai.settings import ProviderConfig


@pytest.mark.parametrize(
    "provider_cls,key,display_name",
    [
        (GroqProvider, "groq", "Groq"),
        (QwenProvider, "qwen", "Qwen"),
        (OpenRouterProvider, "openrouter", "OpenRouter"),
    ],
)
def test_is_configured_true_with_key_and_model(provider_cls, key, display_name) -> None:
    cfg = ProviderConfig(
        key=key,
        display_name=display_name,
        api_key="secret",
        model="some-model",
        base_url="https://x",
    )
    provider = provider_cls(cfg)
    assert provider.is_configured() is True
    assert provider.name == key
    assert provider.display_name == display_name


@pytest.mark.parametrize("provider_cls", [GroqProvider, QwenProvider, OpenRouterProvider])
def test_is_configured_false_without_api_key(provider_cls) -> None:
    cfg = ProviderConfig(key="x", display_name="X", api_key=None, model="m", base_url="https://x")
    assert provider_cls(cfg).is_configured() is False


@pytest.mark.parametrize("provider_cls", [GroqProvider, QwenProvider, OpenRouterProvider])
def test_is_configured_false_without_model(provider_cls) -> None:
    cfg = ProviderConfig(
        key="x", display_name="X", api_key="secret", model=None, base_url="https://x"
    )
    assert provider_cls(cfg).is_configured() is False
