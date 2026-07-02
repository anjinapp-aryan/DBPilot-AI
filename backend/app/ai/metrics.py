from dataclasses import dataclass
from threading import Lock
from typing import Any


@dataclass
class _ProviderMetrics:
    calls: int = 0
    successes: int = 0
    failures: int = 0
    rate_limits: int = 0
    timeouts: int = 0
    circuit_opens: int = 0
    total_latency_ms: int = 0

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.successes if self.successes else 0.0


class AIMetrics:
    """In-memory call metrics per provider, plus a global fallback counter.

    Process-local, reset on restart — sufficient for the single-instance
    free-tier deployment this project targets today. Swap for a
    Prometheus/OpenTelemetry exporter later without touching call sites.
    """

    def __init__(self) -> None:
        self._by_provider: dict[str, _ProviderMetrics] = {}
        self._fallbacks_total = 0
        self._lock = Lock()

    def _bucket(self, provider_name: str) -> _ProviderMetrics:
        return self._by_provider.setdefault(provider_name, _ProviderMetrics())

    def record_call(self, provider_name: str) -> None:
        with self._lock:
            self._bucket(provider_name).calls += 1

    def record_success(self, provider_name: str) -> None:
        with self._lock:
            self._bucket(provider_name).successes += 1

    def record_failure(self, provider_name: str) -> None:
        with self._lock:
            self._bucket(provider_name).failures += 1

    def record_rate_limit(self, provider_name: str) -> None:
        with self._lock:
            self._bucket(provider_name).rate_limits += 1

    def record_timeout(self, provider_name: str) -> None:
        with self._lock:
            self._bucket(provider_name).timeouts += 1

    def record_circuit_open(self, provider_name: str) -> None:
        with self._lock:
            self._bucket(provider_name).circuit_opens += 1

    def record_fallback(self) -> None:
        with self._lock:
            self._fallbacks_total += 1

    def record_latency(self, provider_name: str, elapsed_ms: int) -> None:
        with self._lock:
            self._bucket(provider_name).total_latency_ms += elapsed_ms

    def snapshot(self, order: list[str]) -> dict[str, Any]:
        with self._lock:
            per_provider = {}
            for key in order:
                m = self._by_provider.get(key, _ProviderMetrics())
                per_provider[key] = {
                    "calls": m.calls,
                    "successes": m.successes,
                    "failures": m.failures,
                    "rateLimits": m.rate_limits,
                    "timeouts": m.timeouts,
                    "circuitOpens": m.circuit_opens,
                    "avgLatencyMs": round(m.avg_latency_ms, 1),
                }
            return {"providers": per_provider, "fallbacksTotal": self._fallbacks_total}
