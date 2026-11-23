"""
Custom exception classes and exception handlers for BloodBridge.

Provides a hierarchy of domain-specific exceptions and FastAPI
exception handlers that convert them to proper JSON error responses.
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class BloodBridgeException(Exception):
    """Base exception for all BloodBridge application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(BloodBridgeException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        detail_msg = f"{resource} not found"
        if resource_id:
            detail_msg = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=detail_msg,
            status_code=404,
            details={"resource": resource, "resource_id": resource_id},
        )


class UnauthorizedError(BloodBridgeException):
    """Raised when authentication fails or token is invalid."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=401)


class ForbiddenError(BloodBridgeException):
    """Raised when user lacks permission for the requested action."""

    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message=message, status_code=403)


class ValidationError(BloodBridgeException):
    """Raised when input validation fails beyond Pydantic validation."""

    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=422, details=details or {})


class ConflictError(BloodBridgeException):
    """Raised when an operation conflicts with existing data."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=409)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI application."""

    @app.exception_handler(BloodBridgeException)
    async def bloodbridge_exception_handler(request: Request, exc: BloodBridgeException) -> JSONResponse:
        """Handle all BloodBridge domain exceptions."""
        logger.error(
            "application_error",
            error_type=type(exc).__name__,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            path=str(request.url),
            method=request.method,
        )
        response_body: Dict[str, Any] = {
            "error": True,
            "message": exc.message,
            "status_code": exc.status_code,
        }
        if exc.details:
            response_body["details"] = exc.details
        return JSONResponse(status_code=exc.status_code, content=response_body)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions with a generic error response."""
        logger.error(
            "unhandled_exception",
            error_type=type(exc).__name__,
            message=str(exc),
            path=str(request.url),
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "An internal server error occurred",
                "status_code": 500,
            },
        )
