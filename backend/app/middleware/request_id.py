"""Request ID / trace ID correlation.

Binds a per-request ID (and a trace ID) into structlog's contextvars so
every log line emitted while handling a request — from any module, at any
call depth — automatically carries both, with no need to thread them
through function signatures. IDs are also echoed back as response headers
and exposed on ``request.state`` for handlers that want them directly
(e.g. to include in an error response).

Trace ID propagation here is intentionally simple (accept-or-generate a
header value) rather than a full distributed-tracing SDK. If/when
DBPilot AI adopts OpenTelemetry, this middleware's trace_id can be
replaced by the OTel span context without touching call sites, since
downstream code only ever reads ``structlog.contextvars`` / logger output,
never this middleware directly.
"""

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"
TRACE_ID_HEADER = "X-Trace-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        trace_id = request.headers.get(TRACE_ID_HEADER) or request_id

        request.state.request_id = request_id
        request.state.trace_id = trace_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, trace_id=trace_id)
        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.clear_contextvars()

        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[TRACE_ID_HEADER] = trace_id
        return response
