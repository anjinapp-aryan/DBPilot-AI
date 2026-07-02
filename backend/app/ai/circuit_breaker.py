import time
from enum import Enum
from threading import Lock


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Minimal per-provider circuit breaker.

    Opens after ``failure_threshold`` consecutive failures and stays open for
    ``reset_timeout_seconds``, after which it allows exactly one trial
    request (half-open): success closes it, failure re-opens it for another
    cooldown. Mirrors the role Resilience4j's CircuitBreaker plays in the
    Java gateway, without the extra dependency.
    """

    def __init__(self, failure_threshold: int = 5, reset_timeout_seconds: float = 30.0) -> None:
        self._failure_threshold = failure_threshold
        self._reset_timeout_seconds = reset_timeout_seconds
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._opened_at: float | None = None
        self._lock = Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            self._maybe_half_open()
            return self._state

    def allow_request(self) -> bool:
        with self._lock:
            self._maybe_half_open()
            return self._state != CircuitState.OPEN

    def record_success(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            self._state = CircuitState.CLOSED
            self._opened_at = None

    def record_failure(self) -> None:
        with self._lock:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._failure_threshold:
                self._state = CircuitState.OPEN
                self._opened_at = time.monotonic()

    def _maybe_half_open(self) -> None:
        if self._state == CircuitState.OPEN and self._opened_at is not None:
            if time.monotonic() - self._opened_at >= self._reset_timeout_seconds:
                self._state = CircuitState.HALF_OPEN
