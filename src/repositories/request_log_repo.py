"""Request Log repository for tracking API usage."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import RequestLog


class RequestLogRepository:
    """Repository for request log operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(
        self,
        request_id: UUID,
        api_key_id: Optional[UUID],
        prompt: str,
        provider: str,
        model: str,
        response_data: Optional[dict] = None,
        tokens_used: Optional[int] = None,
        latency_ms: int = 0,
        cached: bool = False,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> RequestLog:
        """
        Create a new request log entry.

        Args:
            request_id: Unique request identifier
            api_key_id: API key used for the request (optional)
            prompt: The prompt text
            provider: LLM provider used
            model: Model name
            response_data: Response data (optional)
            tokens_used: Number of tokens consumed
            latency_ms: Processing time in milliseconds
            cached: Whether response was served from cache
            error_message: Error message if request failed
            metadata: Additional metadata (optional)

        Returns:
            Created RequestLog instance
        """
        # Combine model info into request_params
        request_params = metadata or {}
        request_params["model"] = model

        log = RequestLog(
            request_id=request_id,
            api_key_id=api_key_id,
            prompt_text=prompt,
            prompt_length=len(prompt),
            request_params=request_params,
            response_data=response_data,
            validation_status="success" if response_data and not error_message else "failed",
            provider_used=provider,
            processing_time_ms=latency_ms,
            tokens_used=tokens_used,
            cached=cached,
            error_message=error_message,
        )
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def get_by_id(self, log_id: int) -> Optional[RequestLog]:
        """Get request log by ID."""
        result = await self.db.execute(select(RequestLog).where(RequestLog.id == log_id))
        return result.scalar_one_or_none()

    async def get_by_request_id(self, request_id: UUID) -> Optional[RequestLog]:
        """Get request log by request ID."""
        result = await self.db.execute(
            select(RequestLog).where(RequestLog.request_id == request_id)
        )
        return result.scalar_one_or_none()

    async def list_by_api_key(
        self, api_key_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[RequestLog]:
        """List request logs for a specific API key."""
        result = await self.db.execute(
            select(RequestLog)
            .where(RequestLog.api_key_id == api_key_id)
            .order_by(RequestLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_by_date_range(
        self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100
    ) -> list[RequestLog]:
        """List request logs within a date range."""
        result = await self.db.execute(
            select(RequestLog)
            .where(RequestLog.created_at >= start_date, RequestLog.created_at <= end_date)
            .order_by(RequestLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_api_key(self, api_key_id: UUID) -> int:
        """Count total requests for an API key."""
        result = await self.db.execute(
            select(RequestLog).where(RequestLog.api_key_id == api_key_id)
        )
        return len(list(result.scalars().all()))
