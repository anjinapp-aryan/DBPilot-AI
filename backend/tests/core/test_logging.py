import logging

import structlog

from app.core.config import Settings
from app.core.logging import configure_logging, get_logger


def test_configure_logging_sets_a_single_stdout_handler() -> None:
    configure_logging(Settings(backend_env="staging"))
    root = logging.getLogger()
    assert len(root.handlers) == 1


def test_configure_logging_development_uses_debug_level() -> None:
    configure_logging(Settings(backend_env="development"))
    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_non_development_uses_info_level() -> None:
    configure_logging(Settings(backend_env="staging"))
    assert logging.getLogger().level == logging.INFO


def test_get_logger_returns_bound_logger_and_captures_event_and_kwargs() -> None:
    configure_logging(Settings(backend_env="staging"))

    with structlog.testing.capture_logs() as captured:
        log = get_logger("test.logger")
        log.info("something_happened", provider="deepseek", depth=0)

    assert len(captured) == 1
    assert captured[0]["event"] == "something_happened"
    assert captured[0]["provider"] == "deepseek"
    assert captured[0]["depth"] == 0


def test_request_id_bound_via_contextvars_appears_in_log_output() -> None:
    configure_logging(Settings(backend_env="staging"))

    # capture_logs() replaces the configured processor chain entirely, so
    # merge_contextvars (normally supplied by configure_logging) must be
    # passed explicitly to exercise the same request-id-propagation behavior
    # RequestIDMiddleware relies on in production.
    with structlog.testing.capture_logs(
        processors=[structlog.contextvars.merge_contextvars]
    ) as captured:
        structlog.contextvars.bind_contextvars(request_id="req-123")
        try:
            get_logger("test.logger").info("event_with_request_id")
        finally:
            structlog.contextvars.clear_contextvars()

    assert captured[0]["request_id"] == "req-123"
