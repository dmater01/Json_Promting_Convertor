"""Middleware to add rate limit headers to responses."""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds rate limit headers to responses.

    Reads rate limit info from request.state (set by auth dependency)
    and adds appropriate headers to the response.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add rate limit headers to response.

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint

        Returns:
            Response with rate limit headers added
        """
        # Process the request
        response = await call_next(request)

        # Add rate limit headers if available
        rate_limit_info = getattr(request.state, "rate_limit_info", None)

        if rate_limit_info:
            response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset"])

        return response
