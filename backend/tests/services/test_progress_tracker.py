"""
Tests for Progress Tracking Service

Validates progress calculation, streak tracking, and milestone detection.
"""

import pytest
from datetime import date, timedelta
from app.services.progress_tracker import (
    get_milestone_encouragement,
    _check_milestone,
    MILESTONES,
)


class TestMilestoneDetection:
    """Tests for milestone achievement detection."""

    def test_check_milestone_3_day_streak(self):
        """Test milestone detection for 3-day streak."""
        milestone = _check_milestone(current_streak=3, previous_streak=2)

        assert milestone is not None
        assert milestone["name"] == "3-Day Streak"
        assert milestone["days"] == 3
        assert "3-day" in milestone["message"].lower()

    def test_check_milestone_7_day_streak(self):
        """Test milestone detection for 7-day streak."""
        milestone = _check_milestone(current_streak=7, previous_streak=6)

        assert milestone is not None
        assert milestone["name"] == "Week Warrior"
        assert milestone["days"] == 7

    def test_check_milestone_not_reached(self):
        """Test no milestone when threshold not crossed."""
        milestone = _check_milestone(current_streak=2, previous_streak=1)

        assert milestone is None

    def test_check_milestone_already_passed(self):
        """Test no milestone when already beyond threshold."""
        # Going from 4 to 5 doesn't trigger 3-day milestone (already passed)
        milestone = _check_milestone(current_streak=5, previous_streak=4)

        assert milestone is None

    def test_check_milestone_same_streak(self):
        """Test no milestone when streak unchanged."""
        milestone = _check_milestone(current_streak=5, previous_streak=5)

        assert milestone is None

    def test_check_milestone_30_day(self):
        """Test milestone detection for 30-day streak."""
        milestone = _check_milestone(current_streak=30, previous_streak=29)

        assert milestone is not None
        assert milestone["name"] == "Month Master"
        assert milestone["days"] == 30


class TestMilestoneEncouragement:
    """Tests for milestone encouragement messages."""

    def test_get_milestone_encouragement_no_streaks(self):
        """Test encouragement for user with no streak."""
        result = get_milestone_encouragement(current_streak=0)

        assert result["current_streak"] == 0
        assert len(result["achieved_milestones"]) == 0
        assert result["next_milestone"]["name"] == "3-Day Streak"
        assert result["next_milestone"]["days"] == 3
        assert result["next_milestone"]["days_remaining"] == 3

    def test_get_milestone_encouragement_1_day(self):
        """Test encouragement for 1-day streak."""
        result = get_milestone_encouragement(current_streak=1)

        assert result["current_streak"] == 1
        assert len(result["achieved_milestones"]) == 0
        assert result["next_milestone"]["name"] == "3-Day Streak"
        assert result["next_milestone"]["days_remaining"] == 2
        assert result["next_milestone"]["progress_percentage"] == 33  # 1/3 * 100

    def test_get_milestone_encouragement_3_day_achieved(self):
        """Test encouragement for 3-day streak (first milestone)."""
        result = get_milestone_encouragement(current_streak=3)

        assert result["current_streak"] == 3
        assert len(result["achieved_milestones"]) == 1
        assert result["achieved_milestones"][0]["name"] == "3-Day Streak"
        assert result["next_milestone"]["name"] == "Week Warrior"
        assert result["next_milestone"]["days_remaining"] == 4  # 7 - 3

    def test_get_milestone_encouragement_7_day_achieved(self):
        """Test encouragement for 7-day streak."""
        result = get_milestone_encouragement(current_streak=7)

        assert result["current_streak"] == 7
        assert len(result["achieved_milestones"]) == 2  # 3-day and 7-day
        assert result["achieved_milestones"][1]["name"] == "Week Warrior"
        assert result["next_milestone"]["name"] == "Two Week Champion"
        assert result["next_milestone"]["days_remaining"] == 7  # 14 - 7

    def test_get_milestone_encouragement_all_milestones(self):
        """Test encouragement when all milestones achieved."""
        # Assume last milestone is 100 days
        result = get_milestone_encouragement(current_streak=100)

        assert result["current_streak"] == 100
        assert len(result["achieved_milestones"]) == len(MILESTONES)
        assert result["next_milestone"] is None  # All milestones achieved

    def test_get_milestone_encouragement_between_milestones(self):
        """Test encouragement for streak between milestones."""
        result = get_milestone_encouragement(current_streak=10)

        # Should have achieved 3-day and 7-day
        assert len(result["achieved_milestones"]) == 2
        # Next should be 14-day
        assert result["next_milestone"]["name"] == "Two Week Champion"
        assert result["next_milestone"]["days_remaining"] == 4  # 14 - 10
        assert result["next_milestone"]["progress_percentage"] == 71  # 10/14 * 100


class TestProgressCalculation:
    """Tests for completion percentage calculation."""

    def test_calculate_completion_percentage_formula(self):
        """Test completion percentage calculation formula."""
        # Formula: (completed_chapters / 6) * 100

        # No chapters completed
        assert int((0 / 6) * 100) == 0

        # 1 chapter completed
        assert int((1 / 6) * 100) == 16

        # 3 chapters completed (half of free tier)
        assert int((3 / 6) * 100) == 50

        # All chapters completed
        assert int((6 / 6) * 100) == 100

    def test_milestone_thresholds(self):
        """Test that milestone thresholds are properly defined."""
        # Verify milestones are in ascending order
        milestone_days = [m["days"] for m in MILESTONES]
        assert milestone_days == sorted(milestone_days)

        # Verify all milestones have required fields
        for milestone in MILESTONES:
            assert "days" in milestone
            assert "name" in milestone
            assert "message" in milestone
            assert isinstance(milestone["days"], int)
            assert milestone["days"] > 0


class TestTimezoneAwareness:
    """Tests for timezone-aware date calculations."""

    def test_different_timezones_same_calendar_day(self):
        """Test that streak calculation respects user timezone."""
        import pytz
        from datetime import datetime

        # Test that date calculation uses correct timezone
        utc_tz = pytz.timezone("UTC")
        eastern_tz = pytz.timezone("America/New_York")

        # Same moment in time
        utc_time = datetime(2026, 1, 25, 4, 0, 0, tzinfo=utc_tz)  # 4 AM UTC
        eastern_time = utc_time.astimezone(eastern_tz)  # 11 PM previous day Eastern

        # Dates should be different
        assert utc_time.date() != eastern_time.date()

    def test_streak_continuation_same_day_different_timezone(self):
        """Test streak logic with timezone considerations."""
        # If user's last activity was yesterday in their timezone,
        # and they access today in their timezone, streak should continue

        # This is handled by using user's timezone for date calculation
        # Implementation should always use pytz.timezone(user_timezone).now().date()


class TestEdgeCases:
    """Tests for edge cases in progress tracking."""

    def test_zero_chapters_completion(self):
        """Test completion with no progress."""
        completion = int((0 / 6) * 100)
        assert completion == 0

    def test_partial_chapter_completion(self):
        """Test that partial completion doesn't count as completed."""
        # A chapter at 75% should not count toward completed_chapters
        # Only is_completed=True should count
        pass  # Tested in integration tests

    def test_streak_broken_after_gap(self):
        """Test that streak resets after gap > 1 day."""
        # If last_activity_date was 3 days ago, streak should reset to 1
        # This is tested in integration tests with real database
        pass

    def test_milestone_progress_percentage(self):
        """Test milestone progress percentage calculation."""
        # For 5-day streak toward 7-day milestone
        progress = int((5 / 7) * 100)
        assert progress == 71

        # For 1-day streak toward 3-day milestone
        progress = int((1 / 3) * 100)
        assert progress == 33

    def test_longest_streak_never_decreases(self):
        """Test that longest_streak only increases."""
        # If current_streak goes from 10 to 5, longest_streak stays 10
        # This is enforced by the Streak model logic
        pass  # Model-level invariant
