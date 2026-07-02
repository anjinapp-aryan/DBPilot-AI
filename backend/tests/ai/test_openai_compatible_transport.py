import httpx
import pytest

from app.ai.chat_message import ChatMessage
from app.ai.exceptions import QuotaExceededError
from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.ai.settings import ProviderConfig


def _provider(handler) -> OpenAICompatibleProvider:
    cfg = ProviderConfig(
        key="x", display_name="X", api_key="secret", model="gpt", base_url="https://x.test"
    )
    provider = OpenAICompatibleProvider(cfg)
    provider._client = lambda: httpx.AsyncClient(  # type: ignore[method-assign]
        base_url=cfg.base_url or "", transport=httpx.MockTransport(handler)
    )
    return provider


@pytest.mark.asyncio
async def test_chat_parses_message_content() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": " hi there "}}]})

    provider = _provider(handler)
    result = await provider.chat([ChatMessage.user("hi")], system=None, temperature=0.4)
    assert result == "hi there"


@pytest.mark.asyncio
async def test_chat_raises_quota_exceeded_on_429() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limited"})

    provider = _provider(handler)
    with pytest.raises(QuotaExceededError):
        await provider.chat([ChatMessage.user("hi")], system=None, temperature=0.4)


@pytest.mark.asyncio
async def test_chat_returns_empty_string_when_no_choices() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": []})

    provider = _provider(handler)
    result = await provider.chat([ChatMessage.user("hi")], system=None, temperature=0.4)
    assert result == ""


@pytest.mark.asyncio
async def test_chat_raises_for_server_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    provider = _provider(handler)
    with pytest.raises(httpx.HTTPStatusError):
        await provider.chat([ChatMessage.user("hi")], system=None, temperature=0.4)


@pytest.mark.asyncio
async def test_stream_chat_yields_deltas() -> None:
    sse_body = (
        b'data: {"choices":[{"delta":{"content":"Hel"}}]}\n\n'
        b'data: {"choices":[{"delta":{"content":"lo"}}]}\n\n'
        b"data: [DONE]\n\n"
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


@pytest.mark.asyncio
async def test_stream_chat_ignores_malformed_json_chunk() -> None:
    sse_body = b"data: not-json\n\n" b'data: {"choices":[{"delta":{"content":"ok"}}]}\n\n'

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=sse_body, headers={"content-type": "text/event-stream"})

    provider = _provider(handler)
    tokens = [
        t
        async for t in provider.stream_chat([ChatMessage.user("hi")], system=None, temperature=0.4)
    ]
    assert "".join(tokens) == "ok"
