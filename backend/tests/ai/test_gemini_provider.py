from app.ai.chat_message import ChatMessage
from app.ai.providers.gemini import GeminiProvider
from app.ai.settings import ProviderConfig


def _cfg(**overrides: object) -> ProviderConfig:
    defaults = {
        "key": "gemini",
        "display_name": "Gemini",
        "api_key": "gm-test",
        "model": "gemini-2.5-flash",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
    }
    defaults.update(overrides)
    return ProviderConfig(**defaults)  # type: ignore[arg-type]


def test_is_configured_true_with_key_and_model() -> None:
    provider = GeminiProvider(_cfg())
    assert provider.is_configured() is True
    assert provider.name == "gemini"
    assert provider.display_name == "Gemini"


def test_is_configured_false_without_api_key() -> None:
    assert GeminiProvider(_cfg(api_key=None)).is_configured() is False


def test_build_body_uses_gemini_role_vocabulary_directly() -> None:
    provider = GeminiProvider(_cfg())
    messages = [ChatMessage.user("hi"), ChatMessage.model("hello")]

    body = provider._build_body(messages, system="be nice", temperature=0.5)

    assert body["contents"] == [
        {"role": "user", "parts": [{"text": "hi"}]},
        {"role": "model", "parts": [{"text": "hello"}]},
    ]
    assert body["systemInstruction"] == {"parts": [{"text": "be nice"}]}
    assert body["generationConfig"] == {"temperature": 0.5}


def test_build_body_omits_system_instruction_when_blank() -> None:
    provider = GeminiProvider(_cfg())
    body = provider._build_body([ChatMessage.user("hi")], system=None, temperature=0.2)
    assert "systemInstruction" not in body


def test_extract_text_concatenates_parts() -> None:
    resp = {
        "candidates": [
            {"content": {"parts": [{"text": "hello "}, {"text": "world"}]}},
        ]
    }
    assert GeminiProvider._extract_text(resp) == "hello world"


def test_extract_text_returns_empty_when_no_candidates() -> None:
    assert GeminiProvider._extract_text({}) == ""
