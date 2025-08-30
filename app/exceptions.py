"""
Custom exceptions and exception handlers for the application.
"""
import logging
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class UnsupportedFileTypeError(HTTPException):
    """Raised when an unsupported file type is uploaded."""
    def __init__(self, detail: str):
        super().__init__(status_code=415, detail=detail)


class FileTooLargeError(HTTPException):
    """Raised when a file exceeds the maximum allowed size."""
    def __init__(self, detail: str):
        super().__init__(status_code=413, detail=detail)


class StorageError(HTTPException):
    """Raised when there's an error with file storage operations."""
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)


class ValidationError(HTTPException):
    """Raised when validation fails."""
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)


class NotFoundError(HTTPException):
    """Raised when a resource is not found."""
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedError(HTTPException):
    """Raised when user is not authorized."""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(HTTPException):
    """Raised when user is forbidden to access a resource."""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)


# Exception handlers
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions."""
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
