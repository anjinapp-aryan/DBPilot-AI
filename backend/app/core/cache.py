"""Cache abstraction.

``CacheProvider`` is the interface every call site depends on;
``InMemoryCache`` is the only implementation today. It is process-local
(not shared across workers/replicas) — acceptable for Phase 1/2 scale
(schema-discovery caching, single dev/staging process). Swap in a
Redis-backed implementation behind the same protocol once multi-worker
deployment needs a shared cache; no call site changes required.
"""

import time
from typing import Any, Protocol


class CacheProvider(Protocol):
    async def get(self, key: str) -> Any | None: ...

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None: ...

    async def delete(self, key: str) -> None: ...


class InMemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    async def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at < time.monotonic():
            del self._store[key]
            return None
        return value

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        self._store[key] = (time.monotonic() + ttl_seconds, value)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)
