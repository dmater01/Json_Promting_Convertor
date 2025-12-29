"""Rate limiting middleware for API endpoints."""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.adapters.cache_client import get_cache_client
from src.core.exceptions import RateLimitExceededError
from src.core.logging_config import get_logger
from src.services.rate_limiter import RateLimiter

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces rate limits for authenticated requests.

    Features:
    - Checks rate limits before processing requests
    - Adds rate limit headers to all responses
    - Handles rate limit exceeded errors
    """

    # Paths that don't require rate limiting
    EXCLUDED_PATHS = [
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/v1/health",
        "/v1/metrics",
        "/v1/api-keys/",  # Creating API keys doesn't require auth
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint

        Returns:
            Response with rate limit headers
        """
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return await call_next(request)

        # Skip rate limiting for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Get API key from request state (set by auth dependency)
        api_key = getattr(request.state, "api_key", None)

        if not api_key:
            # No API key in state, let request proceed
            # (auth dependency will handle authentication)
            return await call_next(request)

        # Check rate limit
        try:
            redis = await get_cache_client()
            rate_limiter = RateLimiter(redis.redis)

            # Check if request is allowed
            allowed, remaining, reset_timestamp = await rate_limiter.check_rate_limit(
                api_key_id=api_key.id,
                limit=api_key.rate_limit_per_hour,
            )

            # Record the request
            await rate_limiter.record_request(api_key.id)

            # Process the request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(api_key.rate_limit_per_hour)
            response.headers["X-RateLimit-Remaining"] = str(remaining - 1)  # -1 for current request
            response.headers["X-RateLimit-Reset"] = str(reset_timestamp)

            logger.debug(
                "Rate limit check passed",
                extra={
                    "api_key_id": str(api_key.id),
                    "remaining": remaining - 1,
                    "limit": api_key.rate_limit_per_hour,
                },
            )

            return response

        except RateLimitExceededError as e:
            # Rate limit exceeded - this will be caught by exception handler
            raise

        except Exception as e:
            # Log error but don't block request if rate limiting fails
            logger.error(
                "Rate limiting error - allowing request",
                extra={"error": str(e), "api_key_id": str(api_key.id)},
            )
            return await call_next(request)


async def add_api_key_to_state(request: Request, call_next: Callable) -> Response:
    """
    Middleware to add API key to request state for rate limiting.

    This should run AFTER authentication but BEFORE rate limiting.

    Args:
        request: FastAPI request
        call_next: Next middleware/endpoint

    Returns:
        Response
    """
    # The api_key will be set by the authentication dependency
    # This middleware just ensures it's available in request.state
    return await call_next(request)
