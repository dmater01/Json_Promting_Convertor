"""Rate limiting service using Redis for distributed rate limiting."""

import time
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from redis.asyncio import Redis

from src.core.exceptions import RateLimitExceededError
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Redis-based rate limiter with sliding window algorithm.

    Features:
    - Per-API-key rate limiting
    - Sliding window for accurate rate limiting
    - Automatic cleanup of expired entries
    - Rate limit info for response headers
    """

    def __init__(self, redis: Redis):
        """
        Initialize the rate limiter.

        Args:
            redis: Redis client instance
        """
        self.redis = redis

    def _get_redis_key(self, api_key_id: UUID) -> str:
        """
        Generate Redis key for rate limit tracking.

        Args:
            api_key_id: API key UUID

        Returns:
            Redis key string
        """
        return f"ratelimit:{api_key_id}"

    def _get_window_start(self) -> int:
        """
        Get the start timestamp of the current hour window.

        Returns:
            Unix timestamp of current hour start
        """
        now = datetime.utcnow()
        window_start = now.replace(minute=0, second=0, microsecond=0)
        return int(window_start.timestamp())

    async def check_rate_limit(
        self,
        api_key_id: UUID,
        limit: int,
    ) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limit.

        Uses sliding window algorithm:
        1. Get current hour window
        2. Count requests in current window
        3. Allow if under limit, deny if over

        Args:
            api_key_id: API key UUID
            limit: Maximum requests per hour

        Returns:
            Tuple of (allowed, remaining, reset_timestamp)
            - allowed: True if request is allowed
            - remaining: Number of requests remaining in window
            - reset_timestamp: Unix timestamp when limit resets

        Raises:
            RateLimitExceededError: If rate limit exceeded
        """
        redis_key = self._get_redis_key(api_key_id)
        window_start = self._get_window_start()
        current_time = int(time.time())

        # Redis pipeline for atomic operations
        pipe = self.redis.pipeline()

        # Remove entries older than current hour
        pipe.zremrangebyscore(redis_key, 0, window_start - 1)

        # Count requests in current window
        pipe.zcard(redis_key)

        # Execute pipeline
        results = await pipe.execute()
        current_count = results[1]  # Result of zcard

        # Calculate remaining requests
        remaining = max(0, limit - current_count)

        # Calculate reset timestamp (start of next hour)
        reset_timestamp = window_start + 3600  # +1 hour

        # Check if limit exceeded
        if current_count >= limit:
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "api_key_id": str(api_key_id),
                    "limit": limit,
                    "current_count": current_count,
                    "window_start": window_start,
                },
            )

            raise RateLimitExceededError(
                message=f"Rate limit of {limit} requests per hour exceeded",
                limit=limit,
                remaining=0,
                reset_at=datetime.fromtimestamp(reset_timestamp).isoformat(),
            )

        # Request is allowed
        logger.debug(
            "Rate limit check passed",
            extra={
                "api_key_id": str(api_key_id),
                "current_count": current_count,
                "limit": limit,
                "remaining": remaining,
            },
        )

        return True, remaining, reset_timestamp

    async def record_request(self, api_key_id: UUID) -> None:
        """
        Record a request for rate limiting.

        Adds current timestamp to sorted set for the API key.

        Args:
            api_key_id: API key UUID
        """
        redis_key = self._get_redis_key(api_key_id)
        current_time = time.time()

        # Add current request timestamp to sorted set
        await self.redis.zadd(redis_key, {str(current_time): current_time})

        # Set expiration to 2 hours (to allow for cleanup)
        await self.redis.expire(redis_key, 7200)

        logger.debug(
            "Request recorded for rate limiting",
            extra={"api_key_id": str(api_key_id), "timestamp": current_time},
        )

    async def get_rate_limit_info(
        self,
        api_key_id: UUID,
        limit: int,
    ) -> dict:
        """
        Get rate limit information for an API key.

        Args:
            api_key_id: API key UUID
            limit: Maximum requests per hour

        Returns:
            Dictionary with rate limit info:
            - limit: Maximum requests per hour
            - remaining: Requests remaining in window
            - reset: Unix timestamp when limit resets
            - reset_iso: ISO formatted reset time
        """
        redis_key = self._get_redis_key(api_key_id)
        window_start = self._get_window_start()

        # Remove old entries and count current window
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(redis_key, 0, window_start - 1)
        pipe.zcard(redis_key)
        results = await pipe.execute()

        current_count = results[1]
        remaining = max(0, limit - current_count)
        reset_timestamp = window_start + 3600

        return {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_timestamp,
            "reset_iso": datetime.fromtimestamp(reset_timestamp).isoformat(),
            "current_count": current_count,
        }

    async def reset_rate_limit(self, api_key_id: UUID) -> bool:
        """
        Reset rate limit for an API key (admin function).

        Args:
            api_key_id: API key UUID

        Returns:
            True if reset successful
        """
        redis_key = self._get_redis_key(api_key_id)
        deleted = await self.redis.delete(redis_key)

        logger.info(
            "Rate limit reset",
            extra={"api_key_id": str(api_key_id), "deleted": deleted},
        )

        return deleted > 0
