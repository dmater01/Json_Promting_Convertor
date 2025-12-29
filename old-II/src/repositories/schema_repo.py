"""Schema repository for managing JSON schemas."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Schema


class SchemaRepository:
    """Repository for schema CRUD operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(self, schema: Schema) -> Schema:
        """
        Create a new schema.

        Args:
            schema: Schema instance to create

        Returns:
            Created Schema with ID populated
        """
        self.db.add(schema)
        await self.db.flush()
        await self.db.refresh(schema)
        return schema

    async def get_by_id(self, schema_id: UUID) -> Optional[Schema]:
        """Get schema by ID."""
        result = await self.db.execute(select(Schema).where(Schema.id == schema_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, version: Optional[int] = None) -> Optional[Schema]:
        """
        Get schema by name and optional version.

        Args:
            name: Schema name
            version: Schema version (defaults to latest if not specified)

        Returns:
            Schema if found, None otherwise
        """
        query = select(Schema).where(Schema.name == name)

        if version is not None:
            query = query.where(Schema.version == version)
        else:
            # Get latest version
            query = query.order_by(Schema.version.desc())

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self, public_only: bool = False, skip: int = 0, limit: int = 100
    ) -> list[Schema]:
        """
        List all schemas with optional filtering.

        Args:
            public_only: If True, only return public schemas
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Schema instances
        """
        query = select(Schema)

        if public_only:
            query = query.where(Schema.is_public == True)  # noqa: E712

        query = query.order_by(Schema.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, schema: Schema) -> Schema:
        """
        Update existing schema.

        Args:
            schema: Schema instance with updates

        Returns:
            Updated Schema
        """
        await self.db.flush()
        await self.db.refresh(schema)
        return schema

    async def delete(self, schema_id: UUID) -> bool:
        """
        Delete schema by ID.

        Args:
            schema_id: UUID of the schema

        Returns:
            True if deleted, False if not found
        """
        schema = await self.get_by_id(schema_id)
        if schema:
            await self.db.delete(schema)
            await self.db.flush()
            return True
        return False

    async def search_by_name(self, name_pattern: str, limit: int = 100) -> list[Schema]:
        """
        Search schemas by name pattern.

        Args:
            name_pattern: SQL LIKE pattern (e.g., "invoice%")
            limit: Maximum number of results

        Returns:
            List of matching schemas
        """
        result = await self.db.execute(
            select(Schema).where(Schema.name.like(name_pattern)).limit(limit)
        )
        return list(result.scalars().all())
