import pytest

from app.core.cache import InMemoryCache


@pytest.mark.asyncio
async def test_set_then_get_returns_value() -> None:
    cache = InMemoryCache()
    await cache.set("key", {"a": 1}, ttl_seconds=60)
    assert await cache.get("key") == {"a": 1}


@pytest.mark.asyncio
async def test_get_missing_key_returns_none() -> None:
    cache = InMemoryCache()
    assert await cache.get("missing") is None


@pytest.mark.asyncio
async def test_expired_entry_returns_none_and_is_evicted() -> None:
    # Inject an already-expired entry directly rather than racing a real
    # sleep against time.monotonic() — avoids CI/clock-resolution flakiness.
    cache = InMemoryCache()
    await cache.set("key", "value", ttl_seconds=60)
    expires_at, value = cache._store["key"]
    cache._store["key"] = (expires_at - 120, value)

    assert await cache.get("key") is None
    assert "key" not in cache._store


@pytest.mark.asyncio
async def test_delete_removes_key() -> None:
    cache = InMemoryCache()
    await cache.set("key", "value")
    await cache.delete("key")
    assert await cache.get("key") is None


@pytest.mark.asyncio
async def test_delete_missing_key_is_a_no_op() -> None:
    cache = InMemoryCache()
    await cache.delete("missing")  # must not raise
