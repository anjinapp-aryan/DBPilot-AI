from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app.api.ai import router as ai_router
from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.middleware.exceptions import register_exception_handlers
from app.middleware.rate_limit import limiter
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

settings = get_settings()
configure_logging(settings)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Your AI Copilot for Databases",
    lifespan=lifespan,
)

app.state.limiter = limiter

# Middleware order (each add_middleware call wraps the previous ones, so
# the LAST one added is OUTERMOST — processes the request first, the
# response last):
#   1. SlowAPIMiddleware       (innermost — rate-limit check closest to the route)
#   2. CORSMiddleware
#   3. SecurityHeadersMiddleware
#   4. TrustedHostMiddleware   (reject disallowed Host headers early)
#   5. RequestIDMiddleware     (outermost — request_id/trace_id bound before
#                               anything else runs, so even a rejected/
#                               rate-limited request is logged with one)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts_list)
app.add_middleware(RequestIDMiddleware)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(ai_router)
