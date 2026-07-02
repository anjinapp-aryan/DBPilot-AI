import httpx
import pytest

from app.ai.chat_message import ChatMessage
from app.ai.exceptions import QuotaExceededError
from app.ai.providers.gemini import GeminiProvider
from app.ai.settings import ProviderConfig


def _provider(handler) -> GeminiProvider:
    cfg = ProviderConfig(
        key="gemini",
        display_name="Gemini",
        api_key="secret",
        model="gemini-2.5-flash",
        base_url="https://gemini.test",
    )
    provider = GeminiProvider(cfg)
    provider._client = lambda: httpx.AsyncClient(  # type: ignore[method-assign]
        base_url=cfg.base_url or "", transport=httpx.MockTransport(handler)
    )
    return provider


@pytest.mark.asyncio
async def test_chat_parses_candidate_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {"content": {"parts": [{"text": "hello "}, {"text": "world"}]}},
                ]
            },
        )

    provider = _provider(handler)
    result = await provider.chat([ChatMessage.user("hi")], system=None, temperature=0.4)
    assert result == "hello world"


@pytest.mark.asyncio
async def test_chat_raises_quota_exceeded_on_429() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limited"})

    provider = _provider(handler)
    with pytest.raises(QuotaExceededError):
        await provider.chat([ChatMessage.user("hi")], system=None, temperature=0.4)


@pytest.mark.asyncio
async def test_chat_returns_empty_string_when_no_candidates() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"candidates": []})

    provider = _provider(handler)
    result = await provider.chat([ChatMessage.user("hi")], system=None, temperature=0.4)
    assert result == ""


@pytest.mark.asyncio
async def test_stream_chat_yields_text_chunks() -> None:
    sse_body = (
        b'data: {"candidates":[{"content":{"parts":[{"text":"Hel"}]}}]}\n\n'
        b'data: {"candidates":[{"content":{"parts":[{"text":"lo"}]}}]}\n\n'
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=sse_body, headers={"content-type": "text/event-stream"})

    provider = _provider(handler)
    tokens = [
        t
        async for t in provider.stream_chat([ChatMessage.user("hi")], system=None, temperature=0.4)
    ]
    assert "".join(tokens) == "Hello"


@pytest.mark.asyncio
async def test_stream_chat_raises_quota_exceeded_on_429() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limited"})

    provider = _provider(handler)
    with pytest.raises(QuotaExceededError):
        async for _ in provider.stream_chat([ChatMessage.user("hi")], system=None, temperature=0.4):
            pass
