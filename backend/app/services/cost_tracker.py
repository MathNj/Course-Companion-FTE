"""
Cost Tracker Service for Phase 2 Premium Features

Tracks LLM usage and enforces usage limits for premium features.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session


class CostTracker:
    """Service for tracking and managing LLM usage costs"""

    def __init__(self, db: Session):
        self.db = db

        # Load limits from environment
        self.free_assessments_limit = int(os.getenv("FREE_TIER_ASSESSMENTS_LIMIT", "0"))
        self.premium_assessments_limit = int(os.getenv("PREMIUM_ASSESSMENTS_LIMIT", "30"))
        self.free_learning_paths_limit = int(os.getenv("FREE_TIER_LEARNING_PATHS_LIMIT", "0"))
        self.premium_learning_paths_limit = int(os.getenv("PREMIUM_LEARNING_PATHS_LIMIT", "10"))

    async def check_usage_limits(
        self,
        user_id: int,
        feature_type: str
    ) -> Dict[str, int]:
        """
        Check usage limits for a feature

        Args:
            user_id: User ID
            feature_type: 'graded_assessment' or 'learning_path'

        Returns:
            Dict with 'used', 'limit', 'remaining' counts
        """
        try:
            from app.models.user import User

            # Get user's subscription type
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"used": 0, "limit": 0, "remaining": 0}

            # Get limits based on subscription tier
            if feature_type == "graded_assessment":
                limit = self.premium_assessments_limit if user.subscription_type == 'premium' else self.free_assessments_limit
            elif feature_type == "learning_path":
                limit = self.premium_learning_paths_limit if user.subscription_type == 'premium' else self.free_learning_paths_limit
            else:
                limit = 0

            # Get current month's usage
            today = datetime.utcnow()
            used = await self._get_monthly_usage(user_id, feature_type, today.year, today.month)

            # Calculate remaining
            remaining = max(0, limit - used)

            return {
                "used": used,
                "limit": limit,
                "remaining": remaining
            }

        except Exception as e:
            print(f"Error checking usage limits: {e}")
            # On error, allow the request but log it
            return {"used": 0, "limit": 999, "remaining": 999}

    async def _get_monthly_usage(
        self,
        user_id: int,
        feature_type: str,
        year: int,
        month: int
    ) -> int:
        """
        Get monthly usage count for a feature

        Args:
            user_id: User ID
            feature_type: Feature type
            year: Year
            month: Month (1-12)

        Returns:
            int: Usage count
        """
        try:
            from app.models.llm_usage import LLMUsageLog

            # Query usage logs for this month
            start_of_month = datetime(year, month, 1)
            if month == 12:
                start_of_next_month = datetime(year + 1, 1, 1)
            else:
                start_of_next_month = datetime(year, month + 1, 1)

            count = self.db.query(LLMUsageLog).filter(
                LLMUsageLog.user_id == user_id,
                LLMUsageLog.feature_type == feature_type,
                LLMUsageLog.created_at >= start_of_month,
                LLMUsageLog.created_at < start_of_next_month
            ).count()

            return count

        except Exception as e:
            print(f"Error getting monthly usage: {e}")
            return 0

    async def increment_usage(
        self,
        user_id: int,
        feature_type: str
    ):
        """
        Increment usage counter (logging happens in llm_service)

        This is a placeholder for any additional increment logic needed.
        Actual logging happens in llm_service._log_llm_usage()

        Args:
            user_id: User ID
            feature_type: Feature type
        """
        # Usage is logged in llm_service, so this is just a hook
        # for any additional logic needed
        pass

    async def get_monthly_cost_summary(
        self,
        user_id: int,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """
        Get monthly cost summary for a user

        Args:
            user_id: User ID
            year: Year
            month: Month (1-12)

        Returns:
            Dict with cost breakdown
        """
        try:
            from app.models.llm_usage import LLMUsageLog

            # Get month boundaries
            start_of_month = datetime(year, month, 1)
            if month == 12:
                start_of_next_month = datetime(year + 1, 1, 1)
            else:
                start_of_next_month = datetime(year, month + 1, 1)

            # Query all usage for the month
            logs = self.db.query(LLMUsageLog).filter(
                LLMUsageLog.user_id == user_id,
                LLMUsageLog.created_at >= start_of_month,
                LLMUsageLog.created_at < start_of_next_month
            ).all()

            # Calculate totals
            total_requests = len(logs)
            total_tokens = sum(log.tokens_used for log in logs)
            total_cost = sum(log.cost_usd for log in logs)

            assessments_count = sum(1 for log in logs if log.feature_type == "graded_assessment")
            learning_paths_count = sum(1 for log in logs if log.feature_type == "learning_path")

            return {
                "total_requests": total_requests,
                "total_tokens": total_tokens,
                "total_cost_usd": round(total_cost, 4),
                "assessments_count": assessments_count,
                "learning_paths_count": learning_paths_count
            }

        except Exception as e:
            print(f"Error getting monthly cost summary: {e}")
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "assessments_count": 0,
                "learning_paths_count": 0
            }

    async def reset_usage_limits_if_needed(self):
        """
        Reset usage limits if new month has started

        This should be called periodically (e.g., daily cron job)
        to ensure limits are reset at the start of each month.
        """
        # Usage is calculated dynamically from llm_usage_logs table,
        # so no explicit reset is needed. The monthly queries will
        # automatically return 0 for new months.
        pass

    async def get_total_system_cost(
        self,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """
        Get total system-wide LLM costs for a month (admin function)

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Dict with system-wide cost data
        """
        try:
            from app.models.llm_usage import LLMUsageLog

            # Get month boundaries
            start_of_month = datetime(year, month, 1)
            if month == 12:
                start_of_next_month = datetime(year + 1, 1, 1)
            else:
                start_of_next_month = datetime(year, month + 1, 1)

            # Query all usage for the month
            logs = self.db.query(LLMUsageLog).filter(
                LLMUsageLog.created_at >= start_of_month,
                LLMUsageLog.created_at < start_of_next_month
            ).all()

            # Calculate totals
            total_requests = len(logs)
            total_tokens = sum(log.tokens_used for log in logs)
            total_cost = sum(log.cost_usd for log in logs)
            unique_users = len(set(log.user_id for log in logs))

            # Break down by feature
            assessments_count = sum(1 for log in logs if log.feature_type == "graded_assessment")
            learning_paths_count = sum(1 for log in logs if log.feature_type == "learning_path")

            # Break down by mock vs real
            mock_count = sum(1 for log in logs if log.mock_call)
            real_count = sum(1 for log in logs if not log.mock_call)

            return {
                "total_requests": total_requests,
                "total_tokens": total_tokens,
                "total_cost_usd": round(total_cost, 4),
                "unique_users": unique_users,
                "assessments_count": assessments_count,
                "learning_paths_count": learning_paths_count,
                "mock_calls": mock_count,
                "real_llm_calls": real_count,
                "average_cost_per_request": round(total_cost / total_requests, 4) if total_requests > 0 else 0
            }

        except Exception as e:
            print(f"Error getting system cost: {e}")
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "unique_users": 0,
                "assessments_count": 0,
                "learning_paths_count": 0,
                "mock_calls": 0,
                "real_llm_calls": 0,
                "average_cost_per_request": 0
            }
