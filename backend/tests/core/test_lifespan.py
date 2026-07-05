import structlog
from fastapi.testclient import TestClient

from app.ai.factory import get_ai_gateway
from app.main import app


def setup_function() -> None:
    get_ai_gateway.cache_clear()


def test_lifespan_runs_startup_and_shutdown_events() -> None:
    # TestClient only runs the ASGI lifespan protocol (startup/shutdown)
    # when used as a context manager — plain TestClient(app).get(...)
    # never triggers app/core/lifespan.py at all.
    with structlog.testing.capture_logs() as captured:
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200

    events = [entry["event"] for entry in captured]
    assert "app_startup_begin" in events
    assert "startup_ai_provider_status" in events
    assert "startup_db_connectivity" in events
    assert "app_startup_complete" in events
    assert "app_shutdown_begin" in events
    assert "app_shutdown_complete" in events
    # Startup must complete fully before shutdown begins.
    assert events.index("app_startup_complete") < events.index("app_shutdown_begin")


def test_lifespan_logs_deepseek_and_qwen_status_explicitly() -> None:
    with structlog.testing.capture_logs() as captured:
        with TestClient(app):
            pass

    provider_status_entry = next(
        entry for entry in captured if entry["event"] == "startup_ai_provider_status"
    )
    assert provider_status_entry["deepseek"] == "NOT_CONFIGURED"
    assert provider_status_entry["qwen"] == "NOT_CONFIGURED"


def test_lifespan_reports_db_unreachable_without_a_real_database() -> None:
    with structlog.testing.capture_logs() as captured:
        with TestClient(app):
            pass

    db_entry = next(entry for entry in captured if entry["event"] == "startup_db_connectivity")
    assert db_entry["reachable"] is False
