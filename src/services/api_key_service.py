"""API Key service for authentication and key management."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthenticationError
from src.core.logging_config import get_logger
from src.models.database import APIKey
from src.repositories.api_key_repo import APIKeyRepository

logger = get_logger(__name__)


class APIKeyService:
    """
    Service for managing API keys.

    Features:
    - Secure key generation
    - Hash-based storage (never store raw keys)
    - Key validation and authentication
    - Key lifecycle management (create, revoke, expire)
    """

    KEY_PREFIX = "sp_"  # Structured Prompt
    KEY_LENGTH = 32  # 32 bytes = 256 bits
    HASH_ALGORITHM = "sha256"

    def __init__(self, db: AsyncSession):
        """
        Initialize the API key service.

        Args:
            db: Database session
        """
        self.db = db
        self.repo = APIKeyRepository(db)

    @staticmethod
    def generate_key() -> str:
        """
        Generate a secure random API key.

        Format: sp_<32_random_hex_characters>
        Example: sp_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

        Returns:
            Generated API key string
        """
        random_bytes = secrets.token_bytes(APIKeyService.KEY_LENGTH)
        key_body = random_bytes.hex()
        return f"{APIKeyService.KEY_PREFIX}{key_body}"

    @staticmethod
    def hash_key(key: str) -> str:
        """
        Hash an API key for secure storage.

        Args:
            key: Raw API key

        Returns:
            SHA256 hash of the key
        """
        return hashlib.sha256(key.encode()).hexdigest()

    async def create_key(
        self,
        name: str,
        team: Optional[str] = None,
        rate_limit_per_hour: int = 1000,
        expires_in_days: Optional[int] = None,
    ) -> Tuple[APIKey, str]:
        """
        Create a new API key.

        Args:
            name: Descriptive name for the key
            team: Team name (optional)
            rate_limit_per_hour: Hourly rate limit (default 1000)
            expires_in_days: Days until expiration (None = no expiration)

        Returns:
            Tuple of (APIKey instance, raw_key_string)

        Note:
            The raw key is only returned ONCE during creation.
            It cannot be retrieved later.
        """
        # Generate key
        raw_key = self.generate_key()
        key_hash = self.hash_key(raw_key)

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Create API key instance
        api_key = APIKey(
            key_hash=key_hash,
            name=name,
            team=team,
            rate_limit_per_hour=rate_limit_per_hour,
            is_active=True,
            expires_at=expires_at,
        )

        # Save to database
        created_key = await self.repo.create(api_key)
        await self.db.commit()

        logger.info(
            "API key created",
            extra={
                "key_id": str(created_key.id),
                "key_name": name,
                "team": team,
                "rate_limit": rate_limit_per_hour,
            },
        )

        return created_key, raw_key

    async def validate_key(self, raw_key: str) -> APIKey:
        """
        Validate an API key and return the associated API key record.

        Args:
            raw_key: Raw API key string

        Returns:
            APIKey instance if valid

        Raises:
            AuthenticationError: If key is invalid, inactive, or expired
        """
        # Check format
        if not raw_key.startswith(self.KEY_PREFIX):
            raise AuthenticationError("Invalid API key format")

        # Hash and lookup
        key_hash = self.hash_key(raw_key)
        api_key = await self.repo.get_by_hash(key_hash)

        if not api_key:
            logger.warning("API key not found", extra={"key_hash": key_hash[:8]})
            raise AuthenticationError("Invalid API key")

        # Check if active
        if not api_key.is_active:
            logger.warning(
                "Inactive API key used",
                extra={"key_id": str(api_key.id), "key_name": api_key.name},
            )
            raise AuthenticationError("API key is inactive")

        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            logger.warning(
                "Expired API key used",
                extra={
                    "key_id": str(api_key.id),
                    "key_name": api_key.name,
                    "expired_at": api_key.expires_at.isoformat(),
                },
            )
            raise AuthenticationError("API key has expired")

        logger.debug("API key validated", extra={"key_id": str(api_key.id)})
        return api_key

    async def revoke_key(self, api_key_id: UUID) -> bool:
        """
        Revoke (deactivate) an API key.

        Args:
            api_key_id: UUID of the API key

        Returns:
            True if revoked, False if not found
        """
        success = await self.repo.deactivate(api_key_id)
        if success:
            await self.db.commit()
            logger.info("API key revoked", extra={"key_id": str(api_key_id)})
        return success

    async def delete_key(self, api_key_id: UUID) -> bool:
        """
        Permanently delete an API key.

        Args:
            api_key_id: UUID of the API key

        Returns:
            True if deleted, False if not found
        """
        success = await self.repo.delete(api_key_id)
        if success:
            await self.db.commit()
            logger.info("API key deleted", extra={"key_id": str(api_key_id)})
        return success

    async def get_key(self, api_key_id: UUID) -> Optional[APIKey]:
        """
        Get API key by ID.

        Args:
            api_key_id: UUID of the API key

        Returns:
            APIKey if found, None otherwise
        """
        return await self.repo.get_by_id(api_key_id)

    async def list_keys(self, skip: int = 0, limit: int = 100) -> list[APIKey]:
        """
        List all API keys with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of APIKey instances
        """
        return await self.repo.list_all(skip, limit)
