"""Global exception handling.

Registers FastAPI exception handlers (the mechanism FastAPI actually
routes validation errors and route-raised exceptions through) rather than
a raw ASGI/BaseHTTPMiddleware — a call_next-wrapping middleware does not
reliably observe exceptions that FastAPI's own routing/validation layer
raises and handles internally (e.g. RequestValidationError), so it's the
wrong tool for this job despite "middleware" being the conventional name
for this kind of cross-cutting concern.

Every response this module produces (success or not) uses the same
timestamped envelope shape as app/models/api_response.py.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.ai.exceptions import AIGatewayError
from app.core.exceptions import (
    AIProviderException,
    AppException,
    GenericException,
    ValidationException,
)
from app.core.logging import get_logger

log = get_logger(__name__)


def _error_response(
    status_code: int, code: str, message: str, details: list[Any] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {"code": code, "message": message, "details": details or []},
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        log.warning("app_exception", code=exc.code, message=exc.message, path=request.url.path)
        return _error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(AIGatewayError)
    async def handle_ai_gateway_error(request: Request, exc: AIGatewayError) -> JSONResponse:
        log.warning(
            "ai_gateway_error",
            message=str(exc),
            provider_attempts=exc.provider_attempts,
            path=request.url.path,
        )
        return _error_response(
            AIProviderException.status_code,
            AIProviderException.code,
            str(exc),
            details=[{"providerAttempts": exc.provider_attempts}],
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        log.info("validation_error", errors=exc.errors(), path=request.url.path)
        return _error_response(
            ValidationException.status_code,
            ValidationException.code,
            "Request validation failed",
            details=list(exc.errors()),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Normalizes FastAPI's/Starlette's own HTTPException (e.g. 404, or
        # a route that still raises HTTPException directly) into the
        # standard envelope while preserving the original status code.
        detail = exc.detail
        message = detail if isinstance(detail, str) else str(detail)
        details: list[Any] = [detail] if isinstance(detail, dict) else []
        return _error_response(exc.status_code, "http_error", message, details)

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
        # Full traceback goes to logs; the client only ever sees a generic
        # message so internals are never leaked in a response body.
        log.exception("unhandled_exception", path=request.url.path)
        return _error_response(
            GenericException.status_code, GenericException.code, "An unexpected error occurred"
        )
