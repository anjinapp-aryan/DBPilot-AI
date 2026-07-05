"""Domain exception hierarchy.

Every route/service should raise one of these (or a subclass) instead of
a bare HTTPException — the handlers registered in
app/middleware/exceptions.py catch AppException and render a consistent
JSON envelope from it. Third-party exceptions that cross a service
boundary (e.g. AIGatewayError from app.ai) are mapped to the closest
AppException subclass at the handler layer, not by making app.ai depend
on this module — keeps app.ai usable outside a FastAPI context.
"""

from typing import Any


class AppException(Exception):
    """Base for all domain exceptions. Not meant to be raised directly —
    raise one of the subclasses below."""

    code: str = "internal_error"
    status_code: int = 500

    def __init__(self, message: str, *, details: list[Any] | None = None) -> None:
        self.message = message
        self.details = details or []
        super().__init__(message)


class ValidationException(AppException):
    code = "validation_error"
    status_code = 422


class DatabaseException(AppException):
    code = "database_error"
    status_code = 503


class AIProviderException(AppException):
    code = "ai_provider_error"
    status_code = 503


class SchemaDiscoveryException(AppException):
    code = "schema_discovery_error"
    status_code = 502


class AuthenticationException(AppException):
    code = "authentication_error"
    status_code = 401


class AuthorizationException(AppException):
    code = "authorization_error"
    status_code = 403


class GenericException(AppException):
    """Fallback for unexpected/unhandled errors — the client message stays
    generic on purpose; the real detail goes to logs only."""

    code = "internal_error"
    status_code = 500
