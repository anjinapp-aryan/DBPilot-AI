"""FastAPI dependency-injection providers.

Routes should depend on these via ``Depends(...)`` rather than importing
and calling singleton factories directly — that's what makes
``app.dependency_overrides`` usable in tests and keeps the DI graph
visible in the OpenAPI schema. Each provider wraps an underlying
process-wide singleton (still cached exactly once), so injecting it costs
nothing beyond a function call.
"""

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_ai_gateway
from app.ai.service import AIGatewayService
from app.core.cache import CacheProvider, InMemoryCache
from app.core.config import Settings, get_settings
from app.core.db import get_db_session
from app.services.schema_service import SchemaService


def get_config() -> Settings:
    """Injectable wrapper around the Settings singleton."""
    return get_settings()


def get_llm_gateway() -> AIGatewayService:
    """Injectable wrapper around the AI gateway singleton."""
    return get_ai_gateway()


@lru_cache
def _cache_singleton() -> InMemoryCache:
    return InMemoryCache()


def get_cache() -> CacheProvider:
    return _cache_singleton()


@lru_cache
def _schema_service_singleton() -> SchemaService:
    return SchemaService()


def get_schema_service() -> SchemaService:
    return _schema_service_singleton()


async def get_db() -> AsyncIterator[AsyncSession]:
    """Request-scoped database session. Re-exported here (rather than
    imported directly from app.core.db) so every provider a route needs
    has one consistent import surface: app.core.dependencies."""
    async for session in get_db_session():
        yield session
