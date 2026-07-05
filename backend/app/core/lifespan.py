"""FastAPI application lifecycle (startup/shutdown).

Connectivity checks here are logged, never fatal — a missing database or
an unconfigured AI provider is an expected state in early local
development, not a reason to refuse to boot. The one thing that DOES
refuse to boot on unsafe config is Settings' own validation
(app/core/config.py's production safety checks), which get_settings()
triggers before anything else in this function runs.

Readiness (is the app currently able to serve traffic) is computed fresh
per-request by GET /health/ready, not cached from this one-time startup
check — a database that's reachable at boot and goes down later must be
reflected live, not frozen at the value observed here.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.ai.factory import get_ai_gateway
from app.core.config import get_settings
from app.core.db import check_db_connectivity, dispose_engine
from app.core.logging import get_logger

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()  # triggers Settings validation (see Task 6)
    log.info("app_startup_begin", env=settings.backend_env)

    # Eagerly initialize the AI gateway singleton at startup (rather than
    # lazily on first request) so its configured/health state is known
    # immediately and /health/ready has something meaningful to report
    # from the first request onward.
    gateway = get_ai_gateway()
    provider_health = gateway.health()
    log.info(
        "startup_ai_provider_status",
        deepseek=provider_health.get("deepseek"),
        qwen=provider_health.get("qwen"),
        all_providers=provider_health,
    )

    db_reachable = await check_db_connectivity()
    log.info("startup_db_connectivity", reachable=db_reachable)

    log.info("app_startup_complete")

    yield

    log.info("app_shutdown_begin")
    await dispose_engine()
    log.info("app_shutdown_complete")
