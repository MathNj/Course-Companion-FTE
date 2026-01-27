"""
Redis Client Utility

Comprehensive cache manager for Phase 2 LLM features with 24-hour TTL.
"""

import logging
import json
from typing import Optional, Any, Dict
from datetime import timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


# Cache TTL constants (24 hours for Phase 2 features)
ADAPTIVE_PATH_TTL = 86400  # 24 hours in seconds
ASSESSMENT_FEEDBACK_TTL = 86400  # 24 hours
QUIZ_GRADING_TTL = 3600  # 1 hour
DEFAULT_TTL = ADAPTIVE_PATH_TTL


class RedisClient:
    """
    Async Redis client wrapper for caching operations.

    Features:
    - 24-hour TTL for adaptive paths and assessment feedback
    - JSON serialization/deserialization
    - Graceful degradation when Redis unavailable
    - Cache invalidation support
    """

    def __init__(self):
        """Initialize Redis client from settings."""
        self.client = None
        self._enabled = True

        if not REDIS_AVAILABLE:
            logger.warning("redis package not installed - caching features disabled")
            self._enabled = False
            return

        try:
            from app.config import settings

            self.client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.redis_max_connections
            )
            logger.info("Redis cache manager initialized successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache manager: {e}")
            self._enabled = False

    def is_connected(self) -> bool:
        """Check if Redis client is connected and enabled."""
        return self._enabled and self.client is not None

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get JSON value from Redis and deserialize.

        Args:
            key: Cache key

        Returns:
            Deserialized JSON dict or None if not found/error
        """
        if not self.is_connected():
            return None

        try:
            cached = await self.client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.warning(f"Redis get_json failed for key '{key}': {e}")
            return None

    async def set_json(self, key: str, value: Dict[str, Any], ttl: int = DEFAULT_TTL) -> bool:
        """
        Set JSON value in Redis with expiration.

        Args:
            key: Cache key
            value: Dict to serialize and cache
            ttl: Time to live in seconds (default 24 hours)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            serialized = json.dumps(value)
            await self.client.setex(key, ttl, serialized)
            logger.debug(f"Cached key '{key}' with TTL {ttl}s")
            return True
        except Exception as e:
            logger.warning(f"Redis set_json failed for key '{key}': {e}")
            return False

    async def get(self, key: str) -> Optional[str]:
        """Get raw string value from Redis."""
        if not self.is_connected():
            return None

        try:
            return await self.client.get(key)
        except Exception as e:
            logger.warning(f"Redis get failed for key '{key}': {e}")
            return None

    async def setex(self, key: str, time: int, value: str) -> bool:
        """Set raw string value in Redis with expiration."""
        if not self.is_connected():
            return False

        try:
            await self.client.setex(key, time, value)
            logger.debug(f"Cached key '{key}' with TTL {time}s")
            return True
        except Exception as e:
            logger.warning(f"Redis setex failed for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from Redis.

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            await self.client.delete(key)
            logger.debug(f"Deleted cache key '{key}'")
            return True
        except Exception as e:
            logger.warning(f"Redis delete failed for key '{key}': {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "adaptive_path:*")

        Returns:
            Number of keys deleted
        """
        if not self.is_connected():
            return 0

        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await self.client.delete(*keys)
                logger.info(f"Deleted {len(keys)} cache keys matching pattern '{pattern}'")
                return len(keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis delete_pattern failed for '{pattern}': {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.warning(f"Redis exists check failed for key '{key}': {e}")
            return False

    async def ttl(self, key: str) -> int:
        """
        Get remaining time to live for key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if key exists without expiration, -2 if key doesn't exist
        """
        if not self.is_connected():
            return -2

        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.warning(f"Redis ttl check failed for key '{key}': {e}")
            return -2

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment counter in Redis.

        Args:
            key: Counter key
            amount: Amount to increment (default 1)

        Returns:
            New counter value or None if failed
        """
        if not self.is_connected():
            return None

        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.warning(f"Redis increment failed for key '{key}': {e}")
            return None

    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")


# Global Redis client instance
cache_client = RedisClient()

