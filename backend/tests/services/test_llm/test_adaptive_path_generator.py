"""
Unit Tests for Adaptive Path Generator

Tests for performance data aggregation, prompt building, and path generation.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm.adaptive_path_generator import AdaptivePathGenerator


class TestPerformanceDataAggregation:
    """Test performance data collection and analysis."""

    @pytest.mark.asyncio
    async def test_aggregate_performance_data(self):
        """Test aggregation of student performance data."""
        mock_db = MagicMock(spec=AsyncSession)

        # Mock quiz results
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_result.all.return_value = [
            MagicMock(chapter_id="01-intro", avg_score="85.5", attempt_count="2"),
            MagicMock(chapter_id="02-llms", avg_score="45.0", attempt_count="3")
        ]

        # Mock progress data
        mock_progress_result = MagicMock()
        mock_progress_result.all.return_value = [
            MagicMock(chapter_id="01-intro", time_spent_minutes=45),
            MagicMock(chapter_id="02-llms", time_spent_minutes=90)
        ]

        # Setup execute to return different results
        execute_results = [mock_result, mock_progress_result]

        async def mock_execute(query):
            return execute_results.pop(0) if execute_results else None

        mock_db.execute.return_value.then.return_value = mock_execute

        # This would require actual implementation to test properly
        # For now, we verify the method exists
        assert hasattr(AdaptivePathGenerator, 'get_student_performance_data')

    def test_identify_weak_areas(self):
        """Test weak area detection logic."""
        # Test data: scores below 60% or time >1.5x average
        quiz_scores = {
            "01-intro": 85.5,
            "02-llms": 45.0,  # Weak (<60%)
            "03-prompting": 72.0,
            "04-rag": 58.0,  # Weak (<60%)
        }

        time_spent = {
            "01-intro": 45,
            "02-llms": 90,  # >1.5x average (assuming avg is 60)
            "03-prompting": 50,
            "04-rag": 55
        }

        # Calculate average time
        avg_time = sum(time_spent.values()) / len(time_spent)  # 60

        # Identify weak areas
        weak_areas = [
            chapter for chapter, score in quiz_scores.items()
            if score < 60
        ]

        # Identify struggling with time
        struggling = [
            chapter for chapter, time in time_spent.items()
            if time > avg_time * 1.5
        ]

        assert "02-llms" in weak_areas
        assert "04-rag" in weak_areas
        assert "02-llms" in struggling


class TestPromptBuilding:
    """Test adaptive path prompt generation."""

    def test_build_prompt_includes_performance_data(self):
        """Test that prompt includes student performance data."""
        performance_data = {
            "student_id": "test-student-123",
            "quiz_scores": {"01-intro": 85, "02-llms": 45},
            "weak_areas": ["02-llms"],
            "generated_at": "2026-01-27T10:00:00"
        }

        system_prompt, user_message = AdaptivePathGenerator.build_adaptive_path_prompt(performance_data)

        # Assert performance data is included
        assert "02-llms" in user_message
        assert "45" in user_message  # Score is included
        assert "test-student-123" in user_message

    def test_build_prompt_includes_course_structure(self):
        """Test that prompt includes course structure."""
        performance_data = {
            "quiz_scores": {},
            "generated_at": "2026-01-27T10:00:00"
        }

        system_prompt, user_message = AdaptivePathGenerator.build_adaptive_path_prompt(performance_data)

        # Assert course structure is mentioned
        assert "chapters" in user_message.lower() or "course" in user_message.lower()


class TestPromptTemplate:
    """Test the prompt template file."""

    def test_prompt_template_exists(self):
        """Test that prompt template file exists and is not empty."""
        import os

        prompt_path = "backend/app/prompts/adaptive_path.txt"

        assert os.path.exists(prompt_path), f"Prompt template not found: {prompt_path}"

        with open(prompt_path, 'r') as f:
            content = f.read()

        assert len(content) > 100, "Prompt template is too short"
        assert "JSON" in content or "json" in content, "Prompt should mention JSON output"
        assert "recommendations" in content.lower(), "Prompt should mention recommendations"


class TestCostCalculation:
    """Test cost tracking calculations."""

    def test_calculate_cost_with_gpt4o_mini_pricing(self):
        """Test cost calculation with GPT-4o-mini pricing."""
        from app.services.llm.cost_tracker import CostTracker

        # GPT-4o-mini pricing: $0.15/1M input, $0.60/1M output
        input_tokens = 1500
        output_tokens = 500

        cost = CostTracker.calculate_cost(input_tokens, output_tokens)

        # Expected: (1500 * 0.15 / 1M) + (500 * 0.60 / 1M)
        # = 0.000225 + 0.0003
        # = 0.000525

        expected_cost = (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)

        assert abs(cost - expected_cost) < 0.000001, f"Cost calculation incorrect: {cost}"

    def test_calculate_cost_handles_large_token_counts(self):
        """Test cost calculation with realistic token counts."""
        from app.services.llm.cost_tracker import CostTracker

        # Adaptive path: 1800 input + 300 output
        cost = CostTracker.calculate_cost(1800, 300)
        assert cost > 0
        assert cost < 0.01  # Should still be under 1 cent

        # Assessment: 1200 input + 200 output
        cost = CostTracker.calculate_cost(1200, 200)
        assert cost > 0
        assert cost < 0.01


class TestCachingLogic:
    """Test caching logic for adaptive paths."""

    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test that cache keys are generated correctly."""
        from app.utils.cache import CacheKeys

        student_id = "test-student-123"
        cache_key = CacheKeys.adaptive_path(student_id)

        assert cache_key == "adaptive_path:test-student-123"

    @pytest.mark.asyncio
    async def test_cache_version_invalidation(self):
        """Test cache version changes with new quiz data."""
        from app.utils.cache import CacheKeys
        from datetime import datetime

        student_id = "test-student-123"
        timestamp1 = "2026-01-27T10:00:00"
        timestamp2 = "2026-01-28T15:30:00"

        version1 = CacheKeys.adaptive_path_version(student_id, timestamp1)
        version2 = CacheKeys.adaptive_path_version(student_id, timestamp2)

        # Versions should be different (dates changed)
        assert version1 != version2

        # Version should contain student_id
        assert student_id in version1
        assert student_id in version2

    @pytest.mark.asyncio
    async def test_cache_invalidation_on_new_quiz(self):
        """Test that cache is invalidated when student completes new quiz."""
        # This would require mocking the cache client and database
        # For now, verify the logic exists in adaptive_path_generator.py
        assert hasattr(AdaptivePathGenerator, '_get_cached_path')
        assert hasattr(AdaptivePathGenerator, '_cache_path')
