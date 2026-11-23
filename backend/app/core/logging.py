"""
Structured logging configuration using structlog.

Provides JSON-formatted structured logging with request context,
a logging middleware for automatic request/response logging, and
a convenience logger factory.
"""

import time
import uuid
from typing import Any

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


def setup_logging(log_level: str = "DEBUG") -> None:
    """
    Configure structlog for the application.

    Sets up JSON-formatted structured logging with timestamps,
    log levels, and caller information.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            _log_level_to_int(log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _log_level_to_int(level: str) -> int:
    """Convert a string log level to its integer equivalent."""
    levels = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }
    return levels.get(level.upper(), 20)


def get_logger(name: str = __name__) -> Any:
    """
    Return a structured logger instance bound with a module name.

    Args:
        name: The module name to bind to the logger (typically __name__).
    """
    return structlog.get_logger(module=name)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs incoming HTTP requests and outgoing responses.

    Captures request method, URL, status code, duration, and assigns
    a unique request ID for tracing.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process the request and log request/response details."""
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger = get_logger("http")

        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            query_params=str(request.query_params),
            client_ip=request.client.host if request.client else "unknown",
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=str(request.url.path),
                duration_ms=duration_ms,
                error=str(exc),
            )
            raise

        duration_ms = round((time.time() - start_time) * 1000, 2)

        log_method = logger.info if response.status_code < 400 else logger.warning
        if response.status_code >= 500:
            log_method = logger.error

        log_method(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        return response
