from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.ai.service import AIGatewayService
from app.core.cache import CacheProvider
from app.core.config import get_settings
from app.core.dependencies import check_db_ready, get_cache, get_llm_gateway
from app.core.exceptions import DatabaseException
from app.middleware.rate_limit import limiter
from app.models.api_response import ApiResponse

router = APIRouter(tags=["health"])

Gateway = Annotated[AIGatewayService, Depends(get_llm_gateway)]
Cache = Annotated[CacheProvider, Depends(get_cache)]
DbReady = Annotated[bool, Depends(check_db_ready)]

_CACHE_PROBE_KEY = "__readiness_probe__"


@router.get("/health", response_model=ApiResponse[dict[str, str]])
@limiter.exempt
def health_check() -> ApiResponse[dict[str, str]]:
    """Fast, dependency-free check — what Railway/Render/Docker's own
    HEALTHCHECK point at (see deployment/railway.json, render.yaml,
    backend/Dockerfile). Kept deliberately unchanged in shape/behavior so
    those existing infra configs don't need updating; /health/live and
    /health/ready below are the new, more granular probes."""
    settings = get_settings()
    data = {
        "status": "ok",
        "service": "dbpilot-ai-backend",
        "version": settings.app_version,
    }
    return ApiResponse(data=data)


@router.get("/health/live", response_model=ApiResponse[dict[str, str]])
@limiter.exempt
def liveness() -> ApiResponse[dict[str, str]]:
    """Liveness: is the process itself responsive — no dependency checks.
    If this can't respond, the process is hung/deadlocked and should be
    restarted. Use /health/ready to check whether it can serve real
    requests right now."""
    return ApiResponse(data={"status": "alive"})


@router.get("/health/ready", response_model=ApiResponse[dict[str, Any]])
@limiter.exempt
async def readiness(
    gateway: Gateway, cache: Cache, db_ready: DbReady
) -> ApiResponse[dict[str, Any]]:
    """Readiness: can this instance actually serve requests right now.

    Database unreachable -> not ready (503, raised as DatabaseException so
    it renders through the same global error envelope as everything else).
    AI provider outages do NOT fail readiness — the app can still serve
    non-AI requests; gateway.health() reports real per-provider status in
    the body for monitoring instead of gating the HTTP status code on it.
    """
    if not db_ready:
        raise DatabaseException("Database is not reachable")

    cache_ok = True
    try:
        await cache.set(_CACHE_PROBE_KEY, "ok", ttl_seconds=5)
        cache_ok = await cache.get(_CACHE_PROBE_KEY) == "ok"
    except Exception:  # noqa: BLE001 - any cache failure just marks it down, never fatal
        cache_ok = False

    return ApiResponse(
        data={
            "status": "ready",
            "database": "up",
            "cache": "up" if cache_ok else "down",
            "ai_providers": gateway.health(),
        }
    )
