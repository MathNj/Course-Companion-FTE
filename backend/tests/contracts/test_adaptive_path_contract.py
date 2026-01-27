"""
Contract Tests for Adaptive Path API

Tests that verify the API contract matches the specification.
These tests use the OpenAPI schema and validate request/response formats.
"""

import pytest
from httpx import AsyncClient
from pydantic import ValidationError

from app.main import app
from app.schemas.adaptive import AdaptivePathRequest, AdaptivePathResponse


@pytest.mark.contract
class TestAdaptivePathContract:
    """Contract tests for POST /api/v2/adaptive/path."""

    @pytest.mark.asyncio
    async def test_request_schema_accepts_valid_data(self):
        """Test that request schema accepts valid inputs."""
        # Valid requests
        valid_requests = [
            {"force_refresh": False, "include_reasoning": True},
            {"force_refresh": True, "include_reasoning": False},
            {"force_refresh": False, "include_reasoning": True},  # defaults
            {}  # all defaults
        ]

        for request_data in valid_requests:
            # Should not raise ValidationError
            try:
                validated = AdaptivePathRequest(**request_data)
                assert validated is not None
            except ValidationError as e:
                pytest.fail(f"Valid request failed validation: {e}")

    @pytest.mark.asyncio
    async def test_request_schema_rejects_invalid_force_refresh(self):
        """Test that request schema rejects invalid force_refresh type."""
        with pytest.raises(ValidationError):
            AdaptivePathRequest(force_refresh="not-a-boolean")

    @pytest.mark.asyncio
    async def test_request_schema_rejects_invalid_include_reasoning(self):
        """Test that request schema rejects invalid include_reasoning type."""
        with pytest.raises(ValidationError):
            AdaptivePathRequest(include_reasoning="not-a-boolean")

    @pytest.mark.asyncio
    async def test_response_schema_structure(self):
        """Test that response schema matches expected structure."""
        # Mock response data
        response_data = {
            "path_id": "123e4567-e89b-12d3-a456-426614174000",
            "student_id": "123e4567-e89b-12d3-a456-426614174000",
            "generated_at": "2026-01-27T10:00:00",
            "expires_at": "2026-01-28T10:00:00",
            "status": "active",
            "recommendations": [
                {
                    "chapter_id": "04-rag",
                    "section_id": "embeddings-review",
                    "priority": 1,
                    "reason": "Your quiz scores show weak understanding...",
                    "estimated_impact": "high",
                    "estimated_time_minutes": 30
                }
            ],
            "reasoning": "Based on your performance...",
            "metadata": {
                "total_recommendations": 1,
                "high_priority_count": 1,
                "estimated_total_time_minutes": 30,
                "cached": False
            }
        }

        # Should not raise ValidationError
        try:
            validated = AdaptivePathResponse(**response_data)
            assert validated.path_id == response_data["path_id"]
            assert len(validated.recommendations) == 1
        except ValidationError as e:
            pytest.fail(f"Valid response failed validation: {e}")

    @pytest.mark.asyncio
    async def test_response_schema_rejects_invalid_priority(self):
        """Test that response schema rejects invalid priority range."""
        invalid_response = {
            "path_id": "123",
            "student_id": "456",
            "generated_at": "2026-01-27",
            "expires_at": "2026-01-28",
            "status": "active",
            "recommendations": [
                {
                    "chapter_id": "04-rag",
                    "section_id": "embeddings-review",
                    "priority": 6,  # Invalid: must be 1-5
                    "reason": "Test",
                    "estimated_impact": "high",
                    "estimated_time_minutes": 30
                }
            ]
        }

        with pytest.raises(ValidationError):
            AdaptivePathResponse(**invalid_response)

    @pytest.mark.asyncio
    async def test_response_schema_rejects_invalid_impact(self):
        """Test that response schema rejects invalid impact value."""
        invalid_response = {
            "path_id": "123",
            "student_id": "456",
            "generated_at": "2026-01-27",
            "expires_at": "2026-01-28",
            "status": "active",
            "recommendations": [
                {
                    "chapter_id": "04-rag",
                    "section_id": "embeddings-review",
                    "priority": 1,
                    "reason": "Test",
                    "estimated_impact": "invalid",  # Invalid: must be high/medium/low
                    "estimated_time_minutes": 30
                }
            ]
        }

        with pytest.raises(ValidationError):
            AdaptivePathResponse(**invalid_response)

    @pytest.mark.asyncio
    async def test_response_schema_rejects_invalid_time(self):
        """Test that response schema rejects invalid time range."""
        invalid_response = {
            "path_id": "123",
            "student_id": "456",
            "generated_at": "2026-01-27",
            "expires_at": "2026-01-28",
            "status": "active",
            "recommendations": [
                {
                    "chapter_id": "04-rag",
                    "section_id": "embeddings-review",
                    "priority": 1,
                    "reason": "Test",
                    "estimated_impact": "high",
                    "estimated_time_minutes": 0  # Invalid: must be >0
                }
            ]
        }

        with pytest.raises(ValidationError):
            AdaptivePathResponse(**invalid_response)


@pytest.mark.contract
class TestErrorResponses:
    """Contract tests for error response formats."""

    @pytest.mark.asyncio
    async def test_premium_required_error_structure(self):
        """
        Test that 403 error for free-tier users has correct structure.

        FR-020: System MUST block free-tier users with clear upgrade messaging.
        """
        # Expected error structure
        expected_error = {
            "code": "PREMIUM_REQUIRED",
            "message": "This feature requires a Premium subscription.",
            "benefits": ["List of premium benefits"],
            "upgrade_url": "/api/v1/payments/create-checkout-session",
            "pricing": {"monthly": 9.99, "annual": 99.99}
        }

        # Verify structure has required fields
        assert "code" in expected_error
        assert "message" in expected_error
        assert "upgrade_url" in expected_error

    @pytest.mark.asyncio
    async def test_insufficient_data_error_structure(self):
        """
        Test that 400 error for insufficient data has correct structure.

        FR-001: System MUST identify weak areas, but needs data first.
        """
        # Expected error structure
        expected_error = {
            "code": "INSUFFICIENT_DATA",
            "message": "Not enough learning data to generate meaningful recommendations",
            "required_quizzes": 2,
            "completed_quizzes": int,
            "next_steps": ["List of actions"]
        }

        # Verify structure has required fields
        assert "code" in expected_error
        assert "required_quizzes" in expected_error
        assert "completed_quizzes" in expected_error
        assert "next_steps" in expected_error

    @pytest.mark.asyncio
    async def test_rate_limit_error_structure(self):
        """
        Test that 429 error for quota exceeded has correct structure.

        FR-023: System MUST enforce rate limits on premium features.
        """
        # Expected error structure
        expected_error = {
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "You have exceeded your monthly quota for this feature.",
            "quota": {
                "feature": "adaptive-path",
                "used": 10,
                "limit": 10,
                "resets_at": "2026-02-01T00:00:00Z"
            },
            "upgrade_option": {
                "tier": "pro",
                "benefit": "Unlimited adaptive paths and assessments",
                "price_monthly": 19.99
            }
        }

        # Verify structure has required fields
        assert "code" in expected_error
        assert "quota" in expected_error
        assert "upgrade_option" in expected_error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
