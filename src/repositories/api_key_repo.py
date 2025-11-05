"""API Key repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import APIKey


class APIKeyRepository:
    """Repository for API key CRUD operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def get_by_id(self, api_key_id: UUID) -> Optional[APIKey]:
        """
        Get API key by ID.

        Args:
            api_key_id: UUID of the API key

        Returns:
            APIKey if found, None otherwise
        """
        result = await self.db.execute(select(APIKey).where(APIKey.id == api_key_id))
        return result.scalar_one_or_none()

    async def get_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """
        Get API key by hash.

        Args:
            key_hash: SHA256 hash of the API key

        Returns:
            APIKey if found, None otherwise
        """
        result = await self.db.execute(select(APIKey).where(APIKey.key_hash == key_hash))
        return result.scalar_one_or_none()

    async def create(self, api_key: APIKey) -> APIKey:
        """
        Create new API key.

        Args:
            api_key: APIKey instance to create

        Returns:
            Created APIKey with ID populated
        """
        self.db.add(api_key)
        await self.db.flush()
        await self.db.refresh(api_key)
        return api_key

    async def update(self, api_key: APIKey) -> APIKey:
        """
        Update existing API key.

        Args:
            api_key: APIKey instance with updates

        Returns:
            Updated APIKey
        """
        await self.db.flush()
        await self.db.refresh(api_key)
        return api_key

    async def delete(self, api_key_id: UUID) -> bool:
        """
        Delete API key by ID.

        Args:
            api_key_id: UUID of the API key

        Returns:
            True if deleted, False if not found
        """
        api_key = await self.get_by_id(api_key_id)
        if api_key:
            await self.db.delete(api_key)
            await self.db.flush()
            return True
        return False

    async def deactivate(self, api_key_id: UUID) -> bool:
        """
        Deactivate API key (soft delete).

        Args:
            api_key_id: UUID of the API key

        Returns:
            True if deactivated, False if not found
        """
        api_key = await self.get_by_id(api_key_id)
        if api_key:
            api_key.is_active = False
            await self.db.flush()
            return True
        return False

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[APIKey]:
        """
        List all API keys with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of APIKey instances
        """
        result = await self.db.execute(select(APIKey).offset(skip).limit(limit))
        return list(result.scalars().all())
