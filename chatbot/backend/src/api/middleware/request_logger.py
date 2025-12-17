"""Request logging middleware for tracking API usage."""

import logging
import time
from typing import Callable

from fastapi import Request, Response

logger = logging.getLogger(__name__)


async def request_logger_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to log all incoming requests and their responses.

    Logs:
    - Request method, path, client IP
    - Response status code
    - Request processing time

    Args:
        request: Incoming request
        call_next: Next middleware/handler in chain

    Returns:
        Response from handler
    """
    # Record start time
    start_time = time.time()

    # Get client IP
    client_ip = request.client.host if request.client else "unknown"

    # Log incoming request
    logger.info(f"→ {request.method} {request.url.path} from {client_ip}")

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time_ms = int((time.time() - start_time) * 1000)

    # Log response
    logger.info(
        f"← {request.method} {request.url.path} → {response.status_code} ({process_time_ms}ms)"
    )

    # Add processing time header
    response.headers["X-Process-Time-Ms"] = str(process_time_ms)

    return response
