import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.db import check_db_connectivity, get_db_session, get_engine, get_session_factory


def test_get_engine_returns_async_engine_and_is_cached() -> None:
    engine = get_engine()
    assert isinstance(engine, AsyncEngine)
    assert get_engine() is engine


def test_get_session_factory_builds_sessions_bound_to_the_engine() -> None:
    factory = get_session_factory()
    session = factory()
    assert isinstance(session, AsyncSession)


@pytest.mark.asyncio
async def test_get_db_session_yields_an_async_session() -> None:
    async for session in get_db_session():
        assert isinstance(session, AsyncSession)
        break


@pytest.mark.asyncio
async def test_check_db_connectivity_returns_false_without_a_reachable_database() -> None:
    # No real Postgres is configured in the test environment — this must
    # return False, not raise, since "no DB yet" is an expected dev state.
    assert await check_db_connectivity() is False
