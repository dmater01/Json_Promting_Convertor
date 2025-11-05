"""Redis cache client for caching LLM responses."""

import hashlib
import json
from typing import Any, Dict, Optional

import redis.asyncio as redis

from src.core.config import settings
from src.core.exceptions import CacheError
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CacheClient:
    """
    Redis-based cache client for LLM responses.

    Features:
    - Automatic key generation from request parameters
    - TTL support
    - JSON serialization/deserialization
    - Error handling with graceful degradation
    """

    def __init__(self):
        """Initialize the cache client."""
        self._client: Optional[redis.Redis] = None
        self._initialized = False

    async def initialize(self):
        """Initialize Redis connection pool."""
        if self._initialized:
            return

        try:
            self._client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10,
            )

            # Test connection
            await self._client.ping()

            self._initialized = True
            logger.info("Cache client initialized", extra={"redis_url": settings.redis_url})

        except Exception as e:
            logger.error(
                "Failed to initialize cache client",
                extra={"error": str(e)},
            )
            self._client = None
            self._initialized = False

    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._initialized = False
            logger.info("Cache client closed")

    def _generate_cache_key(
        self,
        prompt: str,
        provider: str,
        temperature: float,
        schema_hash: Optional[str] = None,
    ) -> str:
        """
        Generate a cache key from request parameters.

        Args:
            prompt: The user prompt
            provider: LLM provider name
            temperature: Temperature parameter
            schema_hash: Optional hash of custom schema

        Returns:
            Cache key string
        """
        # Create a deterministic key from parameters
        key_components = [
            prompt,
            provider,
            f"{temperature:.2f}",
        ]

        if schema_hash:
            key_components.append(schema_hash)

        # Hash the components to create a fixed-length key
        key_string = "|".join(key_components)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()

        return f"prompt:v1:{key_hash}"

    def _hash_schema(self, schema: Dict[str, Any]) -> str:
        """
        Generate a hash for a JSON schema.

        Args:
            schema: JSON schema dictionary

        Returns:
            Hash string
        """
        # Sort keys for deterministic hashing
        schema_json = json.dumps(schema, sort_keys=True)
        return hashlib.md5(schema_json.encode()).hexdigest()

    async def get(
        self,
        prompt: str,
        provider: str,
        temperature: float,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a cached response.

        Args:
            prompt: The user prompt
            provider: LLM provider name
            temperature: Temperature parameter
            schema: Optional custom schema

        Returns:
            Cached response dict or None if not found
        """
        if not self._initialized or not self._client:
            logger.debug("Cache not initialized, skipping get")
            return None

        try:
            schema_hash = self._hash_schema(schema) if schema else None
            key = self._generate_cache_key(prompt, provider, temperature, schema_hash)

            value = await self._client.get(key)

            if value:
                logger.info(
                    "Cache hit",
                    extra={"key": key[:16] + "...", "provider": provider},
                )
                return json.loads(value)
            else:
                logger.debug("Cache miss", extra={"key": key[:16] + "..."})
                return None

        except Exception as e:
            logger.warning(
                "Cache get failed, continuing without cache",
                extra={"error": str(e)},
            )
            return None

    async def set(
        self,
        prompt: str,
        provider: str,
        temperature: float,
        response: Dict[str, Any],
        ttl: int = 3600,
        schema: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Set a cached response.

        Args:
            prompt: The user prompt
            provider: LLM provider name
            temperature: Temperature parameter
            response: Response data to cache
            ttl: Time to live in seconds
            schema: Optional custom schema

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized or not self._client:
            logger.debug("Cache not initialized, skipping set")
            return False

        if ttl <= 0:
            logger.debug("Caching disabled (TTL=0)")
            return False

        try:
            schema_hash = self._hash_schema(schema) if schema else None
            key = self._generate_cache_key(prompt, provider, temperature, schema_hash)

            value = json.dumps(response)
            await self._client.setex(key, ttl, value)

            logger.info(
                "Cache set",
                extra={
                    "key": key[:16] + "...",
                    "ttl": ttl,
                    "provider": provider,
                },
            )
            return True

        except Exception as e:
            logger.warning(
                "Cache set failed, continuing",
                extra={"error": str(e)},
            )
            return False

    async def delete(
        self,
        prompt: str,
        provider: str,
        temperature: float,
        schema: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Delete a cached response.

        Args:
            prompt: The user prompt
            provider: LLM provider name
            temperature: Temperature parameter
            schema: Optional custom schema

        Returns:
            True if deleted, False otherwise
        """
        if not self._initialized or not self._client:
            return False

        try:
            schema_hash = self._hash_schema(schema) if schema else None
            key = self._generate_cache_key(prompt, provider, temperature, schema_hash)

            deleted = await self._client.delete(key)

            logger.info(
                "Cache delete",
                extra={"key": key[:16] + "...", "deleted": bool(deleted)},
            )
            return bool(deleted)

        except Exception as e:
            logger.warning(
                "Cache delete failed",
                extra={"error": str(e)},
            )
            return False

    async def clear_all(self, pattern: str = "prompt:v1:*") -> int:
        """
        Clear all cached prompts matching a pattern.

        Args:
            pattern: Redis key pattern to match

        Returns:
            Number of keys deleted
        """
        if not self._initialized or not self._client:
            return 0

        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self._client.delete(*keys)
                logger.info(
                    "Cache cleared",
                    extra={"pattern": pattern, "deleted": deleted},
                )
                return deleted
            return 0

        except Exception as e:
            logger.error(
                "Cache clear failed",
                extra={"error": str(e)},
            )
            raise CacheError(f"Failed to clear cache: {e}", operation="clear_all")

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        if not self._initialized or not self._client:
            return {"available": False}

        try:
            info = await self._client.info("stats")
            keyspace = await self._client.info("keyspace")

            # Count prompt cache keys
            prompt_key_count = 0
            async for _ in self._client.scan_iter(match="prompt:v1:*", count=100):
                prompt_key_count += 1

            return {
                "available": True,
                "total_keys": keyspace.get("db0", {}).get("keys", 0) if keyspace else 0,
                "prompt_cache_keys": prompt_key_count,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0),
                ),
            }

        except Exception as e:
            logger.error("Failed to get cache stats", extra={"error": str(e)})
            return {"available": False, "error": str(e)}

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# Global cache client instance
_cache_client: Optional[CacheClient] = None


async def get_cache_client() -> CacheClient:
    """
    Get or create the global cache client instance.

    Returns:
        CacheClient instance
    """
    global _cache_client

    if _cache_client is None:
        _cache_client = CacheClient()
        await _cache_client.initialize()

    return _cache_client


async def close_cache_client():
    """Close the global cache client."""
    global _cache_client

    if _cache_client:
        await _cache_client.close()
        _cache_client = None
