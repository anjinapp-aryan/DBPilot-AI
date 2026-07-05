from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai import router as ai_router
from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.middleware.exceptions import register_exception_handlers
from app.middleware.request_id import RequestIDMiddleware

settings = get_settings()
configure_logging(settings)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Your AI Copilot for Databases",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Added last so it's outermost: request_id/trace_id are bound before any
# other middleware or route code runs, and stay bound through the response.
app.add_middleware(RequestIDMiddleware)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(ai_router)
