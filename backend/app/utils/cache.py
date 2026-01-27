"""
Redis Caching Utilities

High-performance caching for content, user data, and API responses.
"""

import json
import logging
from typing import Optional, Any
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)


class CacheClient:
    """
    Redis cache client for storing and retrieving cached data.

    Provides async methods for caching with TTL, key patterns for different data types.
    """

    def __init__(self):
        """Initialize Redis client from settings."""
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Establish connection to Redis server."""
        try:
            self.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.redis_max_connections
            )
            # Test connection
            await self.redis.ping()
            logger.info("Redis cache client connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis cache client disconnected")

    def is_connected(self) -> bool:
        """Check if Redis client is connected."""
        return self.redis is not None

    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value as string, or None if not found
        """
        if not self.is_connected():
            logger.warning("Redis not connected - cache get skipped")
            return None

        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
            else:
                logger.debug(f"Cache miss: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set a value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache (string)
            ttl: Time-to-live in seconds (None = no expiration)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected - cache set skipped")
            return False

        try:
            if ttl:
                await self.redis.setex(key, ttl, value)
            else:
                await self.redis.set(key, value)

            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """
        Get a JSON value from cache and deserialize.

        Args:
            key: Cache key

        Returns:
            Deserialized JSON object, or None if not found
        """
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for key '{key}': {e}")
                return None
        return None

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Serialize and set a JSON value in cache.

        Args:
            key: Cache key
            value: Value to serialize and cache
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encode error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if deleted, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected - cache delete skipped")
            return False

        try:
            result = await self.redis.delete(key)
            logger.debug(f"Cache delete: {key} (result: {result})")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Pattern to match (e.g., 'user:*', 'chapter:1:*')

        Returns:
            Number of keys deleted
        """
        if not self.is_connected():
            logger.warning("Redis not connected - cache pattern delete skipped")
            return 0

        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Cache pattern delete: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache pattern delete error for pattern '{pattern}': {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            result = await self.redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter in cache.

        Args:
            key: Cache key
            amount: Amount to increment by (default 1)

        Returns:
            New value after increment, or None on error
        """
        if not self.is_connected():
            logger.warning("Redis not connected - cache increment skipped")
            return None

        try:
            value = await self.redis.incrby(key, amount)
            logger.debug(f"Cache increment: {key} by {amount} = {value}")
            return value
        except Exception as e:
            logger.error(f"Cache increment error for key '{key}': {e}")
            return None


# Key pattern helpers for consistent cache key naming
class CacheKeys:
    """Cache key patterns for different data types."""

    @staticmethod
    def user(user_id: str) -> str:
        """Cache key for user data."""
        return f"user:{user_id}"

    @staticmethod
    def user_progress(user_id: str, chapter_id: str) -> str:
        """Cache key for user's chapter progress."""
        return f"progress:{user_id}:{chapter_id}"

    @staticmethod
    def chapter_content(chapter_id: str) -> str:
        """Cache key for chapter content."""
        return f"chapter:{chapter_id}:content"

    @staticmethod
    def quiz_content(quiz_id: str) -> str:
        """Cache key for quiz content."""
        return f"quiz:{quiz_id}:content"

    @staticmethod
    def user_streak(user_id: str) -> str:
        """Cache key for user's learning streak."""
        return f"streak:{user_id}"

    @staticmethod
    def session(session_id: str) -> str:
        """Cache key for chat session data."""
        return f"session:{session_id}"

    @staticmethod
    def rate_limit(identifier: str) -> str:
        """Cache key for rate limiting."""
        return f"ratelimit:{identifier}"

    # Phase 2: Hybrid Intelligence cache keys

    @staticmethod
    def adaptive_path(student_id: str) -> str:
        """Cache key for adaptive learning path (24h TTL)."""
        return f"adaptive_path:{student_id}"

    @staticmethod
    def adaptive_path_version(student_id: str, last_quiz_timestamp: str) -> str:
        """Generate cache version key based on last quiz time (for invalidation)."""
        # Version changes daily or when new quiz data exists
        import hashlib
        date_hash = hashlib.md5(last_quiz_timestamp[:10].encode()).hexdigest()[:8]
        return f"{CacheKeys.adaptive_path(student_id)}:v{date_hash}"


# Global cache client instance
cache_client = CacheClient()
