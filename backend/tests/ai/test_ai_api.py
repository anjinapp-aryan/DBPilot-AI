from fastapi.testclient import TestClient

from app.ai.factory import get_ai_gateway
from app.ai.service import AIGatewayService
from app.core.config import Settings
from app.core.dependencies import get_llm_gateway
from app.main import app
from tests.ai.conftest import FakeProvider

client = TestClient(app)


def setup_function() -> None:
    get_ai_gateway.cache_clear()
    app.dependency_overrides.pop(get_llm_gateway, None)


def test_ai_health_reports_not_configured_without_api_keys() -> None:
    response = client.get("/api/v1/ai/health")

    assert response.status_code == 200
    body = response.json()
    for key in ("deepseek", "gemini", "groq", "qwen", "openrouter"):
        assert body[key] == "NOT_CONFIGURED"
    assert body["primary"] == "deepseek"


def test_ai_providers_lists_full_failover_chain() -> None:
    response = client.get("/api/v1/ai/providers")

    assert response.status_code == 200
    names = [p["name"] for p in response.json()]
    assert names == ["deepseek", "gemini", "groq", "qwen", "openrouter"]


def test_ai_stats_returns_snapshot() -> None:
    response = client.get("/api/v1/ai/stats")

    assert response.status_code == 200
    assert "providers" in response.json()


def test_ai_chat_returns_503_when_no_provider_configured() -> None:
    response = client.post("/api/v1/ai/chat", json={"message": "hello"})

    assert response.status_code == 503
    assert "providerAttempts" in response.json()["detail"]


def test_dependency_override_swaps_the_gateway_used_by_routes() -> None:
    """Proves get_llm_gateway is real FastAPI DI, not a disguised direct call —
    overriding it must change what /api/v1/ai/chat actually does."""
    fake = FakeProvider("fake", response="overridden response")
    fake_gateway = AIGatewayService(
        providers={"fake": fake},
        settings=Settings(primary_provider="fake", ai_provider_order="fake"),
    )
    app.dependency_overrides[get_llm_gateway] = lambda: fake_gateway
    try:
        response = client.post("/api/v1/ai/chat", json={"message": "hello"})
    finally:
        app.dependency_overrides.pop(get_llm_gateway, None)

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "overridden response"
    assert body["provider"] == "fake"
