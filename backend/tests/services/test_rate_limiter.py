"""
Unit tests for Rate Limiter service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.rate_limiter import RateLimiter, RateLimitExceededError, ADAPTIVE_PATHS_LIMIT, ASSESSMENTS_LIMIT


@pytest.mark.asyncio
class TestRateLimiter:
    """Unit tests for RateLimiter service."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def sample_student_id(self):
        """Sample student UUID."""
        return str(uuid4())

    async def test_get_limit_returns_correct_limits(self, mock_db):
        """Test that get_limit returns correct limits for features."""
        rate_limiter = RateLimiter(mock_db)

        assert rate_limiter._get_limit("adaptive-path") == ADAPTIVE_PATHS_LIMIT
        assert rate_limiter._get_limit("assessment") == ASSESSMENTS_LIMIT
        assert rate_limiter._get_limit("unknown") == ADAPTIVE_PATHS_LIMIT

    async def test_check_and_increment_allows_within_quota(self, mock_db, sample_student_id):
        """Test that check_and_increment succeeds when under quota."""
        rate_limiter = RateLimiter(mock_db)

        # Mock Redis operations
        with patch('app.services.rate_limiter.cache_client') as mock_cache:
            # First call (get_usage) returns None
            # Second call (increment) is separate
            call_count = [0]

            async def mock_get_impl(key):
                call_count[0] += 1
                if call_count[0] == 1:  # First get_usage call
                    return None
                return "0"  # Subsequent calls

            mock_cache.get = mock_get_impl
            mock_cache.setex = AsyncMock(return_value=True)

            # Should succeed
            result = await rate_limiter.check_and_increment(
                student_id=sample_student_id,
                feature="adaptive-path"
            )

            assert result["success"] is True
            assert result["used"] == 1
            assert result["limit"] == 10
            assert result["remaining"] == 9

    async def test_check_and_increment_blocks_when_quota_exceeded(self, mock_db, sample_student_id):
        """Test that check_and_increment raises error at quota limit."""
        rate_limiter = RateLimiter(mock_db)

        # Mock Redis at quota limit (10/10 used)
        with patch('app.services.rate_limiter.cache_client') as mock_cache:
            mock_cache.get = AsyncMock(return_value="10")  # Already at limit
            mock_cache.setex = AsyncMock(return_value=True)

            # Should raise error
            with pytest.raises(RateLimitExceededError) as exc_info:
                await rate_limiter.check_and_increment(
                    student_id=sample_student_id,
                    feature="adaptive-path"
                )

            assert exc_info.value.feature == "adaptive-path"
            assert exc_info.value.used == 10
            assert exc_info.value.limit == 10
            assert exc_info.value.used >= exc_info.value.limit

    async def test_get_usage_from_redis(self, mock_db, sample_student_id):
        """Test getting usage from Redis cache."""
        rate_limiter = RateLimiter(mock_db)

        month = "2025-01"

        with patch('app.services.rate_limiter.cache_client') as mock_cache:
            # Mock cached value: 5 adaptive paths used
            mock_cache.get = AsyncMock(return_value="5")

            usage = await rate_limiter.get_usage(sample_student_id, "adaptive-path", month)

            assert usage["used"] == 5
            assert usage["limit"] == 10
            assert usage["remaining"] == 5
            assert usage["source"] == "redis"

    async def test_get_usage_fallback_to_database(self, mock_db, sample_student_id):
        """Test database fallback when Redis unavailable."""
        rate_limiter = RateLimiter(mock_db)

        month = "2025-01"

        # Mock Redis failure
        with patch('app.services.rate_limiter.cache_client') as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)

            # Mock database query
            mock_quota = MagicMock()
            mock_quota.adaptive_paths_used = 3

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_quota

            mock_db.execute.return_value = mock_result

            usage = await rate_limiter.get_usage(sample_student_id, "adaptive-path", month)

            assert usage["used"] == 3
            assert usage["source"] == "database"

    async def test_increment_usage_in_redis(self, mock_db, sample_student_id):
        """Test incrementing Redis counter."""
        rate_limiter = RateLimiter(mock_db)

        month = "2025-01"

        with patch('app.services.rate_limiter.cache_client') as mock_cache:
            mock_cache.get = AsyncMock(return_value="7")  # Current: 7
            mock_cache.setex = AsyncMock(return_value=True)

            success = await rate_limiter._increment_usage(
                sample_student_id,
                "adaptive-path",
                month
            )

            assert success is True
            # Verify setex was called with incremented value (8)
            mock_cache.setex.assert_called_once()
            call_args = mock_cache.setex.call_args
            assert call_args[0][2] == "8"  # Incremented from 7 to 8
            assert call_args[0][1] == 2678400  # 31 days TTL

    async def test_increment_usage_database_fallback(self, mock_db, sample_student_id):
        """Test database fallback when Redis increment fails."""
        rate_limiter = RateLimiter(mock_db)

        month = "2025-01"

        # Mock current usage
        mock_usage = {
            "used": 5,
            "limit": 10,
            "remaining": 5,
            "resets_at": datetime(2025, 2, 1).isoformat(),
            "month": month,
            "source": "database"
        }

        with patch('app.services.rate_limiter.cache_client') as mock_cache:
            # Redis increment fails
            mock_cache.setex = AsyncMock(return_value=False)

            # Mock database operations
            mock_quota = MagicMock()
            mock_quota.adaptive_paths_used = 5

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_quota

            mock_db.execute.return_value = mock_result
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            result = await rate_limiter._increment_in_db(
                sample_student_id,
                "adaptive-path",
                month,
                mock_usage
            )

            assert result["success"] is True
            assert result["used"] == 6  # Incremented
            assert result["remaining"] == 4
            mock_db.commit.assert_called_once()

    async def test_get_quota_status_comprehensive(self, mock_db, sample_student_id):
        """Test getting comprehensive quota status."""
        rate_limiter = RateLimiter(mock_db)

        with patch('app.services.rate_limiter.cache_client') as mock_cache:
            # Mock adaptive path usage
            mock_cache.get = AsyncMock(return_value="7")

            # Mock assessment usage
            async def mock_get_impl(key):
                if "adaptive-path" in key:
                    return "7"
                else:
                    return "15"

            mock_cache.get = mock_get_impl

            status = await rate_limiter.get_quota_status(sample_student_id)

            assert status["student_id"] == sample_student_id
            assert status["total_usage"] == 22  # 7 + 15
            assert status["total_limit"] == 30  # 10 + 20
            assert status["features"]["adaptive-path"]["used"] == 7
            assert status["features"]["assessment"]["used"] == 15
            assert status["features"]["adaptive-path"]["remaining"] == 3
            assert status["features"]["assessment"]["remaining"] == 5

    async def test_reset_quota(self, mock_db, sample_student_id):
        """Test resetting quota (admin function)."""
        rate_limiter = RateLimiter(mock_db)

        with patch('app.services.rate_limiter.cache_client') as mock_cache:
            mock_cache.setex = AsyncMock(return_value=True)

            success = await rate_limiter.reset_quota(
                student_id=sample_student_id,
                feature="adaptive-path"
            )

            assert success is True
            mock_cache.setex.assert_called_once()
            # Verify reset to 0
            call_args = mock_cache.setex.call_args
            assert call_args[0][2] == "0"

    async def test_assessment_limit_higher_than_adaptive(self, mock_db):
        """Test that assessment limit (20) > adaptive limit (10)."""
        rate_limiter = RateLimiter(mock_db)

        adaptive_limit = rate_limiter._get_limit("adaptive-path")
        assessment_limit = rate_limiter._get_limit("assessment")

        assert assessment_limit == 20
        assert adaptive_limit == 10
        assert assessment_limit > adaptive_limit

    async def test_rate_limit_exceeded_error_attributes(self, mock_db, sample_student_id):
        """Test RateLimitExceededError has correct attributes."""
        rate_limiter = RateLimiter(mock_db)

        # Create error
        resets_at = datetime(2025, 2, 1)

        error = RateLimitExceededError(
            feature="assessment",
            used=20,
            limit=20,
            resets_at=resets_at
        )

        assert error.feature == "assessment"
        assert error.used == 20
        assert error.limit == 20
        assert error.resets_at == resets_at
        assert error.used >= error.limit
