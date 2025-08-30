"""
Custom exceptions and error handlers.
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class FileUploadError(HTTPException):
    """Custom exception for file upload errors."""
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)


class UnsupportedFileTypeError(FileUploadError):
    """Exception for unsupported file types."""
    def __init__(self, detail: str = "Unsupported file type"):
        super().__init__(detail=detail, status_code=415)


class FileTooLargeError(FileUploadError):
    """Exception for files that are too large."""
    def __init__(self, detail: str = "File too large"):
        super().__init__(detail=detail, status_code=413)


class StorageError(FileUploadError):
    """Exception for storage-related errors."""
    def __init__(self, detail: str = "Storage error"):
        super().__init__(detail=detail, status_code=500)


def create_error_response(code: int, message: str) -> dict:
    """Create a standardized error response."""
    return {
        "error": {
            "code": code,
            "message": message
        }
    }


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.status_code, exc.detail)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions."""
    logger.warning(f"Validation error: {exc.errors()} - {request.url}")
    return JSONResponse(
        status_code=422,
        content=create_error_response(422, "Validation error")
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=create_error_response(500, "Internal server error")
    )
