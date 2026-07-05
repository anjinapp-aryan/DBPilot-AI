"""Security response headers.

Applies a conservative, broadly-compatible default set to every response.
HSTS is only set when the request actually arrived over HTTPS (checked
via the request's own scheme, falling back to X-Forwarded-Proto for
requests behind a reverse proxy/load balancer) — sending it over a plain
HTTP connection is meaningless and actively wrong for local development.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"

        is_https = (
            request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
        )
        if is_https:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"

        return response
