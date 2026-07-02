import time

from app.ai.health import HealthStatus, ProviderHealthTracker


def test_unknown_provider_reports_unknown() -> None:
    tracker = ProviderHealthTracker()
    assert tracker.get_status("x") == HealthStatus.UNKNOWN


def test_record_success_sets_healthy() -> None:
    tracker = ProviderHealthTracker()
    tracker.record_success("x")
    assert tracker.get_status("x") == HealthStatus.HEALTHY


def test_record_failure_sets_degraded_with_reason() -> None:
    tracker = ProviderHealthTracker()
    tracker.record_failure("x", "boom")
    assert tracker.get_status("x") == HealthStatus.DEGRADED
    assert tracker.get_reason("x") == "boom"


def test_record_quota_exceeded() -> None:
    tracker = ProviderHealthTracker()
    tracker.record_quota_exceeded("x")
    assert tracker.get_status("x") == HealthStatus.QUOTA_EXCEEDED


def test_status_expires_after_cache_window(monkeypatch) -> None:
    tracker = ProviderHealthTracker()
    tracker.record_success("x")

    real_monotonic = time.monotonic
    monkeypatch.setattr("app.ai.health.time.monotonic", lambda: real_monotonic() + 301)

    assert tracker.get_status("x") == HealthStatus.UNKNOWN


def test_reset_clears_status() -> None:
    tracker = ProviderHealthTracker()
    tracker.record_failure("x", "boom")
    tracker.reset("x")
    assert tracker.get_status("x") == HealthStatus.UNKNOWN
