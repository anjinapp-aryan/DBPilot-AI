import httpx
import pytest

from app.ai.chat_message import ChatMessage
from app.ai.exceptions import AIGatewayError, QuotaExceededError
from app.ai.service import AIGatewayService
from app.core.config import Settings
from tests.ai.conftest import FakeProvider


def _settings(order: str = "a,b") -> Settings:
    return Settings(ai_provider_order=order, primary_provider="a")


@pytest.mark.asyncio
async def test_chat_falls_over_to_next_provider_on_error() -> None:
    a = FakeProvider("a", error=RuntimeError("boom"))
    b = FakeProvider("b", response="hello from b")
    gateway = AIGatewayService({"a": a, "b": b}, _settings())

    result = await gateway.chat([ChatMessage.user("hi")])

    assert result == "hello from b"
    assert gateway.last_used_provider == "b"


@pytest.mark.asyncio
async def test_chat_raises_when_all_providers_fail() -> None:
    a = FakeProvider("a", error=RuntimeError("boom a"))
    b = FakeProvider("b", error=RuntimeError("boom b"))
    gateway = AIGatewayService({"a": a, "b": b}, _settings())

    with pytest.raises(AIGatewayError) as exc_info:
        await gateway.chat([ChatMessage.user("hi")])

    assert exc_info.value.provider_attempts == ["A", "B"]


@pytest.mark.asyncio
async def test_chat_raises_when_no_provider_configured() -> None:
    a = FakeProvider("a", configured=False)
    gateway = AIGatewayService({"a": a}, _settings(order="a"))

    with pytest.raises(AIGatewayError):
        await gateway.chat([ChatMessage.user("hi")])


@pytest.mark.asyncio
async def test_chat_skips_unconfigured_providers() -> None:
    a = FakeProvider("a", configured=False)
    b = FakeProvider("b", response="ok")
    gateway = AIGatewayService({"a": a, "b": b}, _settings())

    result = await gateway.chat([ChatMessage.user("hi")])

    assert result == "ok"
    assert a.calls == 0


@pytest.mark.asyncio
async def test_quota_error_fails_over_without_retry() -> None:
    a = FakeProvider("a", error=QuotaExceededError("429 rate limited"))
    b = FakeProvider("b", response="ok")
    gateway = AIGatewayService({"a": a, "b": b}, _settings())

    result = await gateway.chat([ChatMessage.user("hi")])

    assert result == "ok"
    assert a.calls == 1  # no retry budget spent on quota errors


@pytest.mark.asyncio
async def test_transient_network_error_is_retried_before_failover() -> None:
    a = FakeProvider("a", error=httpx.ConnectError("connection reset"))
    b = FakeProvider("b", response="ok")
    gateway = AIGatewayService({"a": a, "b": b}, _settings())

    result = await gateway.chat([ChatMessage.user("hi")])

    assert result == "ok"
    assert a.calls == 2  # stop_after_attempt(2)


@pytest.mark.asyncio
async def test_empty_response_is_treated_as_failure() -> None:
    a = FakeProvider("a", response="   ")
    b = FakeProvider("b", response="real answer")
    gateway = AIGatewayService({"a": a, "b": b}, _settings())

    result = await gateway.chat([ChatMessage.user("hi")])

    assert result == "real answer"


@pytest.mark.asyncio
async def test_preferred_providers_take_priority() -> None:
    a = FakeProvider("a", response="from a")
    b = FakeProvider("b", response="from b")
    gateway = AIGatewayService({"a": a, "b": b}, _settings())

    result = await gateway.chat([ChatMessage.user("hi")], preferred_providers=["b"])

    assert result == "from b"


@pytest.mark.asyncio
async def test_stream_chat_yields_tokens_from_first_provider() -> None:
    a = FakeProvider("a", response="hello world")
    gateway = AIGatewayService({"a": a}, _settings(order="a"))

    tokens = [t async for t in gateway.stream_chat([ChatMessage.user("hi")])]

    assert "".join(tokens).strip() == "hello world"


@pytest.mark.asyncio
async def test_stream_chat_raises_when_no_provider_configured() -> None:
    gateway = AIGatewayService({}, _settings(order=""))

    with pytest.raises(AIGatewayError):
        async for _ in gateway.stream_chat([ChatMessage.user("hi")]):
            pass


@pytest.mark.asyncio
async def test_stream_chat_fails_over_before_first_token() -> None:
    a = FakeProvider("a", error=RuntimeError("boom"))
    b = FakeProvider("b", response="hello world")
    gateway = AIGatewayService({"a": a, "b": b}, _settings())

    tokens = [t async for t in gateway.stream_chat([ChatMessage.user("hi")])]

    assert "".join(tokens).strip() == "hello world"


@pytest.mark.asyncio
async def test_stream_chat_propagates_error_after_first_token_emitted() -> None:
    class MidStreamFailProvider(FakeProvider):
        async def stream_chat(self, messages: list, system: str | None, temperature: float):
            yield "partial "
            raise RuntimeError("boom mid stream")

    a = MidStreamFailProvider("a")
    b = FakeProvider("b", response="should not be used")
    gateway = AIGatewayService({"a": a, "b": b}, _settings())

    with pytest.raises(RuntimeError):
        async for _ in gateway.stream_chat([ChatMessage.user("hi")]):
            pass


@pytest.mark.asyncio
async def test_chat_skips_provider_with_open_circuit() -> None:
    a = FakeProvider("a", response="from a")
    b = FakeProvider("b", response="from b")
    gateway = AIGatewayService({"a": a, "b": b}, _settings())
    for _ in range(5):  # default failure_threshold
        gateway._breakers["a"].record_failure()

    result = await gateway.chat([ChatMessage.user("hi")])

    assert result == "from b"
    assert a.calls == 0


@pytest.mark.asyncio
async def test_stream_chat_skips_provider_with_open_circuit() -> None:
    a = FakeProvider("a", response="from a")
    b = FakeProvider("b", response="from b")
    gateway = AIGatewayService({"a": a, "b": b}, _settings())
    for _ in range(5):
        gateway._breakers["a"].record_failure()

    tokens = [t async for t in gateway.stream_chat([ChatMessage.user("hi")])]

    assert "".join(tokens).strip() == "from b"
    assert a.calls == 0


def test_health_reports_not_configured_and_up() -> None:
    a = FakeProvider("a", configured=False)
    b = FakeProvider("b", configured=True)
    gateway = AIGatewayService({"a": a, "b": b}, _settings())

    health = gateway.health()

    assert health["a"] == "NOT_CONFIGURED"
    assert health["b"] == "UP"
    assert health["primary"] == "a"


def test_provider_statuses_lists_all_order_entries() -> None:
    a = FakeProvider("a", configured=True)
    gateway = AIGatewayService({"a": a}, _settings(order="a"))

    statuses = gateway.provider_statuses()

    assert len(statuses) == 1
    assert statuses[0]["name"] == "a"
    assert statuses[0]["configured"] is True
    assert statuses[0]["status"] == "UP"
