import time
from dataclasses import dataclass
from enum import Enum
from threading import Lock


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    UNKNOWN = "UNKNOWN"


@dataclass
class _ProviderHealth:
    status: HealthStatus
    reason: str | None
    recorded_at: float


class ProviderHealthTracker:
    """Tracks provider health to avoid repeatedly favoring failed providers.

    Caches health status for 5 minutes; a provider not queried again within
    that window reverts to UNKNOWN rather than staying stuck in a stale
    state forever.
    """

    _HEALTH_CACHE_SECONDS = 5 * 60

    def __init__(self) -> None:
        self._health: dict[str, _ProviderHealth] = {}
        self._lock = Lock()

    def record_success(self, provider_name: str) -> None:
        with self._lock:
            self._health[provider_name] = _ProviderHealth(
                HealthStatus.HEALTHY, None, time.monotonic()
            )

    def record_failure(self, provider_name: str, reason: str | None) -> None:
        with self._lock:
            self._health[provider_name] = _ProviderHealth(
                HealthStatus.DEGRADED, reason, time.monotonic()
            )

    def record_quota_exceeded(self, provider_name: str) -> None:
        with self._lock:
            self._health[provider_name] = _ProviderHealth(
                HealthStatus.QUOTA_EXCEEDED, "Quota exhausted", time.monotonic()
            )

    def get_status(self, provider_name: str) -> HealthStatus:
        with self._lock:
            h = self._health.get(provider_name)
            if h is None:
                return HealthStatus.UNKNOWN
            if time.monotonic() - h.recorded_at > self._HEALTH_CACHE_SECONDS:
                del self._health[provider_name]
                return HealthStatus.UNKNOWN
            return h.status

    def get_reason(self, provider_name: str) -> str | None:
        with self._lock:
            h = self._health.get(provider_name)
            return h.reason if h else None

    def reset(self, provider_name: str) -> None:
        with self._lock:
            self._health.pop(provider_name, None)
