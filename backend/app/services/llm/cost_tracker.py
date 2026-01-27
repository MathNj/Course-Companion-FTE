"""
LLM Usage Cost Tracker

Logs every LLM API call with token count, cost, and performance metrics.
"""

import logging
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usage import LLMUsageLog
from app.models.llm import AdaptivePath, AssessmentFeedback

logger = logging.getLogger(__name__)


# Pricing (Claude Sonnet 4.5 as of 2026-01-27)
INPUT_COST_PER_1M_TOKENS = 3.0  # $3 per million input tokens
OUTPUT_COST_PER_1M_TOKENS = 15.0  # $15 per million output tokens


class CostTracker:
    """
    Track and log LLM usage costs for monitoring and alerting.
    """

    @staticmethod
    def calculate_cost(input_tokens: int, output_tokens: int) -> float:
        """
        Calculate LLM API call cost in USD.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_1M_TOKENS
        output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_1M_TOKENS
        total_cost = input_cost + output_cost
        return round(total_cost, 6)

    @staticmethod
    async def log_usage(
        db: AsyncSession,
        student_id: str,
        feature: str,
        reference_id: str,
        request_data: Dict[str, Any],
        success: bool = True,
        error_code: str = None,
        error_message: str = None
    ) -> None:
        """
        Log LLM API call to database for cost tracking and audit.

        Args:
            db: Database session
            student_id: Student UUID
            feature: Feature type ("adaptive-path" or "assessment")
            reference_id: UUID of related entity (path_id or feedback_id)
            request_data: Response from Claude API (content, tokens, latency)
            success: Whether the API call succeeded
            error_code: Error code if failed
            error_message: Error message if failed
        """
        try:
            # Calculate cost
            cost_usd = CostTracker.calculate_cost(
                request_data["input_tokens"],
                request_data["output_tokens"]
            )

            # Create usage log entry
            log_entry = LLMUsageLog(
                student_id=student_id,
                feature=feature,
                reference_id=reference_id,
                request_timestamp=datetime.now(),
                model_version=request_data.get("model", "claude-sonnet-4-5-20250929"),
                tokens_input=request_data["input_tokens"],
                tokens_output=request_data["output_tokens"],
                cost_usd=cost_usd,
                latency_ms=request_data["latency_ms"],
                success=success,
                error_code=error_code,
                error_message=error_message
            )

            db.add(log_entry)
            await db.commit()

            logger.info(
                f"Logged LLM usage: student={student_id[:8]}..., "
                f"feature={feature}, tokens={request_data['total_tokens']}, "
                f"cost=${cost_usd:.4f}, latency={request_data['latency_ms']}ms"
            )

            # Check if cost threshold exceeded
            await CostTracker.check_cost_alert(db, student_id)

        except Exception as e:
            logger.error(f"Failed to log LLM usage: {str(e)}")
            # Don't fail the request if logging fails

    @staticmethod
    async def check_cost_alert(db: AsyncSession, student_id: str) -> None:
        """
        Check if student has exceeded monthly cost threshold and send alert.

        Args:
            db: Database session
            student_id: Student UUID
        """
        from sqlalchemy import select, func
        from app.database import get_llm_settings
        import os

        settings = get_llm_settings()
        threshold = settings.LLM_COST_ALERT_THRESHOLD

        # Query total cost for current month
        from sqlalchemy import cast, Date

        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)

        result = await db.execute(
            select(
                func.sum(LLMUsageLog.cost_usd)
            ).where(
                LLMUsageLog.student_id == student_id,
                LLMUsageLog.request_timestamp >= current_month_start,
                LLMUsageLog.success == True,
                LLMUsageLog.deleted_at.is_(None)
            )
        )
        monthly_cost = result.scalar() or 0.0

        # Alert if threshold exceeded
        if monthly_cost > threshold:
            logger.warning(
                f"⚠️ Cost alert: Student {student_id[:8]}... exceeded threshold "
                f"(${monthly_cost:.2f} > ${threshold:.2f})"
            )

            # TODO: Send email alert if LLM_COST_ALERT_EMAIL is configured
            email = settings.LLM_COST_ALERT_EMAIL
            if email:
                # Implement email sending logic here
                pass
