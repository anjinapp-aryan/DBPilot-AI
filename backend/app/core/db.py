"""Minimal async SQLAlchemy engine/session plumbing.

Scope note: this is intentionally thin. Schema Discovery (Phase 2) owns
the actual ORM models, Alembic migrations, and repository layer — this
module exists now only because dependency injection, application
lifecycle, and health checks (this remediation pass) all need *some*
concrete way to obtain a session / probe connectivity. Nothing here
assumes a database is actually reachable; ``check_db_connectivity`` is a
best-effort probe, not a hard requirement.
"""

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)


@lru_cache
def get_engine() -> AsyncEngine:
    """Process-wide async engine singleton. Creating an engine does not
    open a connection — that only happens on first actual use — so this
    is safe to call even when no database is provisioned yet."""
    settings = get_settings()
    return create_async_engine(settings.database_url, pool_pre_ping=True, future=True)


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yields a request-scoped AsyncSession."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def check_db_connectivity() -> bool:
    """Best-effort connectivity probe for lifespan/health checks.

    Never raises — a missing/unreachable database is an expected state in
    local dev before Phase 2 provisions one, not a startup failure.
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # noqa: BLE001 - connectivity probe, any failure means "down"
        log.warning("db_connectivity_check_failed", error=str(exc))
        return False


async def dispose_engine() -> None:
    engine = get_engine()
    await engine.dispose()
    get_engine.cache_clear()
