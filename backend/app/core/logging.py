"""Structured logging configuration (structlog + stdlib logging).

Call ``configure_logging(settings)`` exactly once, at process startup,
before any other module logs anything. Everywhere else in the codebase,
get a logger via ``get_logger(__name__)`` and log with short event names
plus keyword arguments — e.g. ``log.info("ai_gateway_call", provider=...,
depth=...)`` — never %-style message strings, so fields stay queryable in
the JSON output.
"""

import logging
import sys
from collections.abc import Callable

import structlog
from structlog.types import EventDict

from app.core.config import Settings

Processor = Callable[[object, str, EventDict], EventDict]


def _add_app_context(settings: Settings) -> Processor:
    def processor(_logger: object, _method_name: str, event_dict: EventDict) -> EventDict:
        event_dict.setdefault("service", settings.app_name)
        event_dict.setdefault("env", settings.backend_env)
        return event_dict

    return processor


def configure_logging(settings: Settings) -> None:
    """Configure structlog + stdlib logging for the whole process.

    - JSON output in staging/production (log-aggregator friendly).
    - Readable colored console output in development.
    - request_id/trace_id are injected automatically for any log call made
      while RequestIDMiddleware has bound them via structlog.contextvars —
      no need to pass them explicitly at each call site.
    """
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        timestamper,
        _add_app_context(settings),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: structlog.types.Processor
    if settings.backend_env == "development":
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.DEBUG if settings.backend_env == "development" else logging.INFO)

    # Uvicorn's own access logger is deliberately left alone (it has useful
    # per-request lines); third-party libraries default to WARNING so they
    # don't drown out application events.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
