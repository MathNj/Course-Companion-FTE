"""
Unit tests for Redis caching functionality
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.utils.redis_client import RedisClient, ADAPTIVE_PATH_TTL, ASSESSMENT_FEEDBACK_TTL


@pytest.mark.asyncio
class TestRedisClient:
    """Unit tests for Redis cache manager."""

    @pytest.fixture
    def redis_client(self):
        """Create Redis client instance."""
        return RedisClient()

    def test_client_initialization(self, redis_client):
        """Test that Redis client initializes."""
        assert redis_client is not None
        assert hasattr(redis_client, 'client')

    def test_ttl_constants(self):
        """Test cache TTL constants are properly defined."""
        assert ADAPTIVE_PATH_TTL == 86400  # 24 hours
        assert ASSESSMENT_FEEDBACK_TTL == 86400  # 24 hours
        # 86400 seconds = 24 hours
        assert ADAPTIVE_PATH_TTL / 3600 == 24

    @pytest.mark.asyncio
    async def test_get_json_when_disconnected(self, redis_client):
        """Test get_json returns None when Redis unavailable."""
        # Mock is_connected to return False
        redis_client._enabled = False

        result = await redis_client.get_json("test_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_json_when_disconnected(self, redis_client):
        """Test set_json returns False when Redis unavailable."""
        redis_client._enabled = False

        result = await redis_client.set_json("test_key", {"data": "test"})

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_when_disconnected(self, redis_client):
        """Test delete returns False when Redis unavailable."""
        redis_client._enabled = False

        result = await redis_client.delete("test_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_when_disconnected(self, redis_client):
        """Test exists returns False when Redis unavailable."""
        redis_client._enabled = False

        result = await redis_client.exists("test_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_ttl_when_disconnected(self, redis_client):
        """Test ttl returns -2 (key doesn't exist) when Redis unavailable."""
        redis_client._enabled = False

        result = await redis_client.ttl("test_key")

        assert result == -2

    @pytest.mark.asyncio
    async def test_increment_when_disconnected(self, redis_client):
        """Test increment returns None when Redis unavailable."""
        redis_client._enabled = False

        result = await redis_client.increment("counter")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_json_with_custom_ttl(self, redis_client):
        """Test set_json with custom TTL parameter."""
        # Mock successful setex
        redis_client.client = AsyncMock()
        redis_client.client.setex = AsyncMock(return_value=True)

        result = await redis_client.set_json(
            "test_key",
            {"data": "test"},
            ttl=3600  # 1 hour
        )

        assert result is True
        redis_client.client.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_pattern(self, redis_client):
        """Test delete_pattern deletes multiple keys."""
        # Mock scan_iter and delete
        async def mock_scan_iter(*args, **kwargs):
            yield "adaptive_path:user1"
            yield "adaptive_path:user2"

        redis_client.client = AsyncMock()
        redis_client.client.scan_iter = mock_scan_iter
        redis_client.client.delete = AsyncMock(return_value=2)

        result = await redis_client.delete_pattern("adaptive_path:*")

        assert result == 2
        redis_client.client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_json_with_valid_json(self, redis_client):
        """Test get_json deserializes valid JSON."""
        # Mock successful get
        redis_client.client = AsyncMock()
        redis_client.client.get = AsyncMock(return_value='{"key": "value"}')

        result = await redis_client.get_json("test_key")

        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_json_with_invalid_json(self, redis_client):
        """Test get_json returns None on invalid JSON."""
        # Mock get returning invalid JSON
        redis_client.client = AsyncMock()
        redis_client.client.get = AsyncMock(return_value='invalid json{')

        result = await redis_client.get_json("test_key")

        assert result is None


@pytest.mark.asyncio
class TestAdaptivePathCaching:
    """Test caching integration with adaptive paths."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_cache_path_with_24_hour_ttl(self, mock_db):
        """Test that adaptive paths are cached with 24-hour TTL."""
        from app.services.llm.adaptive_path_generator import AdaptivePathGenerator
        from app.models.llm import AdaptivePath

        # Create mock path
        mock_path = MagicMock(spec=AdaptivePath)
        mock_path.path_id = "test-path-123"
        mock_path.generated_at = datetime.now()
        mock_path.expires_at = datetime.now() + timedelta(hours=24)
        mock_path.recommendations_json = [
            {
                "chapter_id": "04-rag",
                "priority": 1,
                "reason": "Test recommendation"
            }
        ]
        mock_path.reasoning = "Test reasoning"

        # Mock Redis client (imported inside method)
        with patch('app.utils.redis_client.cache_client') as mock_cache:
            mock_cache.set_json = AsyncMock(return_value=True)

            await AdaptivePathGenerator._cache_path(
                db=mock_db,
                student_id="test-student-123",
                path=mock_path
            )

            # Verify called with 24-hour TTL
            mock_cache.set_json.assert_called_once()
            call_args = mock_cache.set_json.call_args
            assert call_args[1]["ttl"] == 86400  # 24 hours

    @pytest.mark.asyncio
    async def test_get_cached_path_returns_valid_path(self, mock_db):
        """Test retrieving valid cached path."""
        from app.services.llm.adaptive_path_generator import AdaptivePathGenerator

        cached_data = {
            "path_id": "test-path-123",
            "student_id": "test-student-123",
            "generated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=23)).isoformat(),
            "recommendations": [{"chapter_id": "04-rag"}],
            "reasoning": "Test reasoning",
            "metadata": {"cached": True}
        }

        with patch('app.utils.redis_client.cache_client') as mock_cache:
            mock_cache.get_json = AsyncMock(return_value=cached_data)

            result = await AdaptivePathGenerator._get_cached_path(
                db=mock_db,
                student_id="test-student-123"
            )

            assert result is not None
            assert result["metadata"]["cached"] is True
            assert result["path_id"] == "test-path-123"

    @pytest.mark.asyncio
    async def test_invalidate_cache_deletes_key(self, mock_db):
        """Test cache invalidation deletes Redis key."""
        from app.services.llm.adaptive_path_generator import AdaptivePathGenerator

        with patch('app.utils.redis_client.cache_client') as mock_cache:
            mock_cache.delete = AsyncMock(return_value=True)

            result = await AdaptivePathGenerator.invalidate_cache(
                db=mock_db,
                student_id="test-student-123"
            )

            assert result is True
            mock_cache.delete.assert_called_once_with("adaptive_path:test-student-123")

    @pytest.mark.asyncio
    async def test_get_cache_stats_returns_ttl_info(self, mock_db):
        """Test cache stats returns TTL and age information."""
        from app.services.llm.adaptive_path_generator import AdaptivePathGenerator

        with patch('app.utils.redis_client.cache_client') as mock_cache:
            # Mock cache exists with 12 hours remaining
            mock_cache.exists = AsyncMock(return_value=True)
            mock_cache.ttl = AsyncMock(return_value=43200)  # 12 hours

            result = await AdaptivePathGenerator.get_cache_stats(
                db=mock_db,
                student_id="test-student-123"
            )

            assert result["cached"] is True
            assert result["ttl_seconds"] == 43200
            assert result["ttl_hours"] == 12.0
            assert result["age_hours"] == 12.0  # 24h - 12h = 12h age
