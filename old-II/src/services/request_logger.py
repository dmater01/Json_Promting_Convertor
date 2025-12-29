"""Request logging service for tracking API usage."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging_config import get_logger
from src.repositories.request_log_repo import RequestLogRepository

logger = get_logger(__name__)


class RequestLogger:
    """
    Logs API requests to the database for analytics and monitoring.

    Features:
    - Async database logging
    - Request/response tracking
    - Error logging
    - Performance metrics
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the request logger.

        Args:
            db: Database session
        """
        self.db = db
        self.repo = RequestLogRepository(db)

    async def log_request(
        self,
        request_id: str,
        api_key_id: Optional[uuid.UUID],
        prompt: str,
        provider: str,
        model: str,
        response_data: Optional[Dict[str, Any]],
        tokens_used: Optional[int],
        latency_ms: int,
        cached: bool,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> uuid.UUID:
        """
        Log an API request to the database.

        Args:
            request_id: Unique request identifier
            api_key_id: API key ID (if authenticated)
            prompt: User prompt
            provider: LLM provider used
            model: Model name
            response_data: Response data (if successful)
            tokens_used: Number of tokens consumed
            latency_ms: Request latency in milliseconds
            cached: Whether response was cached
            error: Error message (if failed)
            metadata: Additional request metadata

        Returns:
            UUID of the created log entry
        """
        try:
            log_entry = await self.repo.create(
                request_id=uuid.UUID(request_id),
                api_key_id=api_key_id,
                prompt=prompt,
                provider=provider,
                model=model,
                response_data=response_data,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                cached=cached,
                error_message=error,
                metadata=metadata,
            )

            logger.info(
                "Request logged",
                extra={
                    "request_id": request_id,
                    "log_id": str(log_entry.id),
                    "provider": provider,
                    "cached": cached,
                    "error": error is not None,
                },
            )

            return log_entry.id

        except Exception as e:
            # Don't fail the request if logging fails
            logger.error(
                "Failed to log request",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                },
            )
            # Re-raise to let caller decide how to handle
            raise

    async def log_success(
        self,
        request_id: str,
        api_key_id: Optional[uuid.UUID],
        prompt: str,
        provider: str,
        model: str,
        response_data: Dict[str, Any],
        tokens_used: Optional[int],
        latency_ms: int,
        cached: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> uuid.UUID:
        """
        Log a successful request.

        Args:
            request_id: Request ID
            api_key_id: API key ID
            prompt: User prompt
            provider: LLM provider
            model: Model name
            response_data: Response data
            tokens_used: Tokens consumed
            latency_ms: Latency in ms
            cached: Whether cached
            metadata: Additional metadata

        Returns:
            Log entry UUID
        """
        return await self.log_request(
            request_id=request_id,
            api_key_id=api_key_id,
            prompt=prompt,
            provider=provider,
            model=model,
            response_data=response_data,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            cached=cached,
            error=None,
            metadata=metadata,
        )

    async def log_error(
        self,
        request_id: str,
        api_key_id: Optional[uuid.UUID],
        prompt: str,
        provider: str,
        error: str,
        latency_ms: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> uuid.UUID:
        """
        Log a failed request.

        Args:
            request_id: Request ID
            api_key_id: API key ID
            prompt: User prompt
            provider: LLM provider attempted
            error: Error message
            latency_ms: Latency before failure
            metadata: Additional metadata

        Returns:
            Log entry UUID
        """
        return await self.log_request(
            request_id=request_id,
            api_key_id=api_key_id,
            prompt=prompt,
            provider=provider,
            model="unknown",
            response_data=None,
            tokens_used=None,
            latency_ms=latency_ms,
            cached=False,
            error=error,
            metadata=metadata,
        )

    async def get_usage_stats(
        self,
        api_key_id: Optional[uuid.UUID] = None,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Get usage statistics.

        Args:
            api_key_id: Filter by API key (None for all)
            hours: Time window in hours

        Returns:
            Usage statistics dictionary
        """
        try:
            stats = await self.repo.get_usage_stats(api_key_id, hours)
            return stats

        except Exception as e:
            logger.error(
                "Failed to get usage stats",
                extra={"error": str(e)},
            )
            return {}
