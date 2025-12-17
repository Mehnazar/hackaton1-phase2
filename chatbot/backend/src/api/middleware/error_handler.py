"""Error handling middleware for standardized error responses."""

import logging
import traceback
from typing import Callable

from fastapi import Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to catch and handle all exceptions with standardized responses.

    Args:
        request: Incoming request
        call_next: Next middleware/handler in chain

    Returns:
        Response with standardized error format
    """
    try:
        response = await call_next(request)
        return response

    except RequestValidationError as exc:
        # Pydantic validation errors (400 Bad Request)
        logger.warning(f"Validation error for {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "Request validation failed",
                "details": exc.errors(),
            },
        )

    except StarletteHTTPException as exc:
        # HTTP exceptions (404, 403, etc.)
        logger.warning(f"HTTP {exc.status_code} for {request.url}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "message": f"HTTP {exc.status_code}",
            },
        )

    except Exception as exc:
        # Unhandled exceptions (500 Internal Server Error)
        logger.error(
            f"Unhandled exception for {request.url}: {exc}\n{traceback.format_exc()}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later.",
            },
        )


def create_error_response(
    status_code: int,
    error: str,
    message: str,
    details: dict | None = None,
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        status_code: HTTP status code
        error: Short error identifier
        message: Human-readable error message
        details: Optional additional error details

    Returns:
        JSONResponse with standardized error format
    """
    content = {
        "error": error,
        "message": message,
    }
    if details:
        content["details"] = details

    return JSONResponse(status_code=status_code, content=content)
