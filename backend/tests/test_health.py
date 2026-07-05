from fastapi.testclient import TestClient

from app.ai.factory import get_ai_gateway
from app.core.dependencies import check_db_ready, get_cache
from app.main import app

client = TestClient(app)


def setup_function() -> None:
    get_ai_gateway.cache_clear()
    app.dependency_overrides.pop(check_db_ready, None)
    app.dependency_overrides.pop(get_cache, None)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert body["data"]["service"] == "dbpilot-ai-backend"
    assert "version" in body["data"]
    assert "timestamp" in body
    assert body["metadata"] == {}


def test_liveness_always_returns_alive_with_no_dependency_checks() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == {"status": "alive"}


def test_readiness_returns_503_when_database_unreachable() -> None:
    # No real Postgres is configured in the test environment — this is the
    # real, unmocked check_db_connectivity() outcome, not a stub.
    response = client.get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "database_error"


def test_readiness_returns_200_and_full_status_when_database_reachable() -> None:
    app.dependency_overrides[check_db_ready] = lambda: True
    try:
        response = client.get("/health/ready")
    finally:
        app.dependency_overrides.pop(check_db_ready, None)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "ready"
    assert data["database"] == "up"
    assert data["cache"] == "up"
    assert data["ai_providers"]["primary"] == "deepseek"


def test_readiness_reports_cache_down_without_failing_the_request() -> None:
    class BrokenCache:
        async def set(self, key: str, value: object, ttl_seconds: int = 300) -> None:
            raise RuntimeError("cache backend unavailable")

        async def get(self, key: str) -> object:
            raise RuntimeError("cache backend unavailable")

        async def delete(self, key: str) -> None:
            raise RuntimeError("cache backend unavailable")

    app.dependency_overrides[check_db_ready] = lambda: True
    app.dependency_overrides[get_cache] = lambda: BrokenCache()
    try:
        response = client.get("/health/ready")
    finally:
        app.dependency_overrides.pop(check_db_ready, None)
        app.dependency_overrides.pop(get_cache, None)

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "ready"
    assert body["data"]["cache"] == "down"
