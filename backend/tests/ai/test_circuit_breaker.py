import time

from app.ai.circuit_breaker import CircuitBreaker, CircuitState


def test_starts_closed_and_allows_requests() -> None:
    cb = CircuitBreaker()
    assert cb.state == CircuitState.CLOSED
    assert cb.allow_request() is True


def test_opens_after_threshold_failures() -> None:
    cb = CircuitBreaker(failure_threshold=3, reset_timeout_seconds=60)
    for _ in range(3):
        cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.allow_request() is False


def test_success_resets_consecutive_failure_count() -> None:
    cb = CircuitBreaker(failure_threshold=3, reset_timeout_seconds=60)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED


def test_half_opens_after_reset_timeout(monkeypatch) -> None:
    cb = CircuitBreaker(failure_threshold=1, reset_timeout_seconds=10)
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    real_monotonic = time.monotonic
    monkeypatch.setattr("app.ai.circuit_breaker.time.monotonic", lambda: real_monotonic() + 11)

    assert cb.allow_request() is True
    assert cb.state == CircuitState.HALF_OPEN


def test_half_open_failure_reopens_circuit(monkeypatch) -> None:
    cb = CircuitBreaker(failure_threshold=1, reset_timeout_seconds=10)
    cb.record_failure()

    real_monotonic = time.monotonic
    monkeypatch.setattr("app.ai.circuit_breaker.time.monotonic", lambda: real_monotonic() + 11)
    assert cb.allow_request() is True

    cb.record_failure()
    assert cb.state == CircuitState.OPEN
