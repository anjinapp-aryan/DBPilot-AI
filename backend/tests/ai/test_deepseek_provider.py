from app.ai.chat_message import ChatMessage
from app.ai.providers.deepseek import DeepSeekProvider
from app.ai.settings import ProviderConfig


def _cfg(**overrides: object) -> ProviderConfig:
    defaults = {
        "key": "deepseek",
        "display_name": "DeepSeek",
        "api_key": "test-deepseek-key",
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
    }
    defaults.update(overrides)
    return ProviderConfig(**defaults)  # type: ignore[arg-type]


def test_is_configured_true_with_key_and_model() -> None:
    provider = DeepSeekProvider(_cfg())
    assert provider.is_configured() is True
    assert provider.name == "deepseek"
    assert provider.display_name == "DeepSeek"


def test_is_configured_false_without_api_key() -> None:
    provider = DeepSeekProvider(_cfg(api_key=None))
    assert provider.is_configured() is False


def test_is_configured_false_without_model() -> None:
    provider = DeepSeekProvider(_cfg(model=None))
    assert provider.is_configured() is False


def test_messages_payload_maps_model_role_to_assistant() -> None:
    provider = DeepSeekProvider(_cfg())
    messages = [ChatMessage.user("hi"), ChatMessage.model("hello")]

    payload = provider._messages_payload(messages, system="be nice")

    assert payload == [
        {"role": "system", "content": "be nice"},
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]


def test_messages_payload_omits_system_when_blank() -> None:
    provider = DeepSeekProvider(_cfg())
    payload = provider._messages_payload([ChatMessage.user("hi")], system=None)
    assert payload == [{"role": "user", "content": "hi"}]
