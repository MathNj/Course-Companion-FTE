"""
Adaptive Learning Path Generator

Analyzes student performance and generates personalized recommendations using Claude Sonnet 4.5.
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.services.llm.client import get_openai_client
from app.services.llm.cost_tracker import CostTracker
from app.models.llm import AdaptivePath
from app.models.user import User
from app.models.quiz import QuizAttempt
from app.models.progress import ChapterProgress

logger = logging.getLogger(__name__)


class AdaptivePathGenerator:
    """
    Generate personalized learning recommendations based on student performance.
    """

    @staticmethod
    async def get_student_performance_data(
        db: AsyncSession,
        student_id: str
    ) -> Dict[str, Any]:
        """
        Aggregate student performance data for analysis.

        Args:
            db: Database session
            student_id: Student UUID

        Returns:
            Dictionary with:
                - chapters_completed: List of completed chapters
                - quiz_scores: Dict mapping chapter_id to score
                - time_spent: Dict mapping chapter_id to minutes
                - weak_areas: List of chapters with score < 60%
                - strong_areas: List of chapters with score >= 85%
                - skipped_sections: List of sections not accessed
        """
        # Get quiz results
        quiz_result = await db.execute(
            select(
                QuizAttempt.chapter_id,
                func.avg(QuizAttempt.score).label("avg_score"),
                func.count(QuizAttempt.id).label("attempt_count")
            )
            .where(QuizAttempt.student_id == student_id)
            .group_by(QuizAttempt.chapter_id)
        )

        quiz_data = quiz_result.all()

        if len(quiz_data) < 2:
            raise ValueError(
                "Insufficient learning data. Complete at least 2 quizzes "
                "before requesting personalized recommendations."
            )

        # Get chapter progress (time spent)
        progress_result = await db.execute(
            select(
                ChapterProgress.chapter_id,
                ChapterProgress.time_spent_minutes
            )
            .where(ChapterProgress.student_id == student_id)
        )

        progress_data = progress_result.all()
        progress_dict = {p.chapter_id: p.time_spent_minutes for p in progress_data}

        # Calculate average time per chapter
        avg_time_per_chapter = sum(progress_dict.values()) / len(progress_dict) if progress_dict else 45

        # Build performance snapshot
        quiz_scores = {}
        time_spent = {}
        weak_areas = []
        strong_areas = []

        for chapter in quiz_data:
            chapter_id = chapter[0]
            avg_score = float(chapter[1])
            quiz_scores[chapter_id] = avg_score
            time_spent[chapter_id] = progress_dict.get(chapter_id, 0)

            # Identify weak and strong areas
            if avg_score < 60:
                weak_areas.append(chapter_id)
            elif avg_score >= 85:
                strong_areas.append(chapter_id)

        # Calculate average score
        overall_avg_score = sum(quiz_scores.values()) / len(quiz_scores)

        # Identify chapters where time spent > 1.5x average (indicates struggle)
        struggling_with_time = []
        for chapter_id, minutes in time_spent.items():
            if minutes > avg_time_per_chapter * 1.5:
                struggling_with_time.append(chapter_id)

        return {
            "student_id": student_id,
            "chapters_completed": list(quiz_scores.keys()),
            "quiz_scores": quiz_scores,
            "time_spent": time_spent,
            "overall_avg_score": overall_avg_score,
            "weak_areas": weak_areas,
            "strong_areas": strong_areas,
            "struggling_with_time": struggling_with_time,
            "generated_at": datetime.now().isoformat()
        }

    @staticmethod
    def build_adaptive_path_prompt(performance_data: Dict[str, Any]) -> str:
        """
        Create prompt for Claude Sonnet to generate adaptive path.

        Args:
            performance_data: Student performance snapshot

        Returns:
            Formatted prompt string
        """
        # Load system prompt template
        try:
            with open("backend/app/prompts/adaptive_path.txt", "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            # Fallback system prompt if file doesn't exist
            system_prompt = """You are an expert learning advisor for a Generative AI Fundamentals course. Analyze the student's performance data and generate 3-5 prioritized recommendations for personalized learning.

Your task:
1. Identify weak areas (quiz scores below 60% or time spent >1.5x average)
2. Suggest specific chapters/sections to review
3. Prioritize recommendations (1=highest impact, 5=lowest)
4. Explain reasoning for each recommendation
5. Estimate completion time (15-60 minutes per recommendation)

Output Format (JSON only, no additional text):
```json
{
  "recommendations": [
    {
      "chapter_id": "04-rag",
      "section_id": "embeddings-review",
      "priority": 1,
      "reason": "Your quiz scores show weak understanding of vector embeddings (45%), which are foundational for RAG systems.",
      "estimated_impact": "high",
      "estimated_time_minutes": 30
    }
  ]
}
```

Focus on:
- Foundational concepts (prerequisites before advanced topics)
- Knowledge gaps (score < 60% or excessive time spent)
- Learning progression (natural chapter sequence)
- Practical application (real-world scenarios)

Be encouraging and specific in your reasoning."""

        # Build user message with performance data
        user_message = f"""Please analyze this student's learning performance and generate personalized recommendations:

Student Performance Data:
{json.dumps(performance_data, indent=2)}

Course Structure (6 chapters):
1. Introduction to Generative AI
2. Large Language Models (LLMs)
3. Prompt Engineering
4. Retrieval-Augmented Generation (RAG)
5. Fine-Tuning LLMs
6. Building AI Applications

Generate 3-5 prioritized recommendations in JSON format following the system prompt instructions."""

        return system_prompt, user_message

    @staticmethod
    async def generate_path(
        db: AsyncSession,
        student_id: str,
        force_refresh: bool = False,
        current_user: User = None
    ) -> Dict[str, Any]:
        """
        Generate adaptive learning path using Claude Sonnet 4.5.

        Args:
            db: Database session
            student_id: Student UUID
            force_refresh: Bypass cache and regenerate
            current_user: Authenticated user

        Returns:
            Dictionary with path data including recommendations

        Raises:
            ValueError: If insufficient learning data
            APIError: If Claude API call fails
        """
        # Check cache first (unless force_refresh)
        if not force_refresh:
            cached_path = await AdaptivePathGenerator._get_cached_path(db, student_id)
            if cached_path:
                logger.info(f"Returning cached adaptive path for student {student_id[:8]}...")
                return cached_path

        # Aggregate performance data
        performance_data = await AdaptivePathGenerator.get_student_performance_data(db, student_id)

        # Build prompt
        system_prompt, user_message = AdaptivePathGenerator.build_adaptive_path_prompt(performance_data)

        # Call OpenAI API with JSON mode for structured output
        client = get_openai_client()
        response = await client.create_message(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=500,
            temperature=0.3,  # Low temperature for consistent recommendations
            response_format={"type": "json_object"}  # Enable JSON mode
        )

        # Parse JSON response
        try:
            recommendations_data = json.loads(response["content"])
            recommendations = recommendations_data.get("recommendations", [])

            if not recommendations:
                raise ValueError("No recommendations generated")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {response['content']}")
            raise ValueError("Invalid response format from LLM") from e

        # Calculate reasoning
        reasoning = f"""Based on your performance (overall average: {performance_data['overall_avg_score']:.1f}%):

{''.join([
    f"- Weak areas identified: {', '.join(performance_data['weak_areas'])}" if performance_data['weak_areas'] else "- All chapters show strong understanding",
    f"- Strong areas: {', '.join(performance_data['strong_areas'])}" if performance_data['strong_areas'] else "- Build on your existing knowledge",
    f"- Time analysis: {', '.join(performance_data['struggling_with_time'])} (excessive time indicates struggle)" if performance_data['struggling_with_time'] else "- Learning pace is appropriate"
])}

Recommendations are prioritized by impact on your learning progression."""

        # Create database record
        expires_at = datetime.now() + datetime.timedelta(hours=24)

        # Import models here to avoid circular imports
        import uuid

        new_path = AdaptivePath(
            path_id=uuid.uuid4(),
            student_id=student_id,
            generated_at=datetime.now(),
            expires_at=expires_at,
            recommendations_json=recommendations,
            reasoning=reasoning,
            tokens_input=response["input_tokens"],
            tokens_output=response["output_tokens"],
            cost_usd=response["total_tokens"] / 100000,  # Approximate cost calculation
            status="active"
        )

        db.add(new_path)
        await db.commit()
        await db.refresh(new_path)

        # Log usage
        await CostTracker.log_usage(
            db=db,
            student_id=student_id,
            feature="adaptive-path",
            reference_id=str(new_path.path_id),
            request_data=response,
            success=True
        )

        # Cache in Redis (24 hour TTL)
        await AdaptivePathGenerator._cache_path(db, student_id, new_path)

        logger.info(
            f"Generated adaptive path for student {student_id[:8]}... "
            f"({len(recommendations)} recommendations, expires in 24h)"
        )

        # Build response
        return {
            "path_id": str(new_path.path_id),
            "student_id": student_id,
            "generated_at": new_path.generated_at.isoformat(),
            "expires_at": new_path.expires_at.isoformat(),
            "status": new_path.status,
            "recommendations": recommendations,
            "reasoning": reasoning,
            "metadata": {
                "total_recommendations": len(recommendations),
                "high_priority_count": sum(1 for r in recommendations if r.get("priority") == 1),
                "estimated_total_time_minutes": sum(r.get("estimated_time_minutes", 0) for r in recommendations),
                "cached": False
            }
        }

    @staticmethod
    async def _get_cached_path(
        db: AsyncSession,
        student_id: str
    ) -> Dict[str, Any] | None:
        """
        Check Redis cache for existing adaptive path (24-hour TTL).

        Returns cached path if valid and not expired, None otherwise.
        """
        from app.utils.redis_client import cache_client, ADAPTIVE_PATH_TTL

        try:
            cache_key = f"adaptive_path:{student_id}"
            path_data = await cache_client.get_json(cache_key)

            if path_data:
                # Check if still valid (not expired)
                expires_at = datetime.fromisoformat(path_data["expires_at"])
                if expires_at > datetime.now():
                    logger.info(f"Cache HIT for student {student_id[:8]}... (TTL: {ADAPTIVE_PATH_TTL}s)")
                    # Add cached flag
                    path_data["metadata"]["cached"] = True
                    return path_data
                else:
                    # Cache expired, delete it
                    await cache_client.delete(cache_key)
                    logger.info(f"Cache expired for student {student_id[:8]}...")
            else:
                logger.debug(f"Cache MISS for student {student_id[:8]}...")

        except Exception as e:
            logger.warning(f"Cache check failed for student {student_id[:8]}...: {str(e)}")

        return None

    @staticmethod
    async def _cache_path(
        db: AsyncSession,
        student_id: str,
        path: AdaptivePath
    ) -> None:
        """
        Cache adaptive path in Redis with 24-hour TTL.

        Uses JSON serialization for structured data and 86400s (24h) expiration.
        """
        from app.utils.redis_client import cache_client, ADAPTIVE_PATH_TTL

        try:
            cache_key = f"adaptive_path:{student_id}"
            cache_data = {
                "path_id": str(path.path_id),
                "student_id": student_id,
                "generated_at": path.generated_at.isoformat(),
                "expires_at": path.expires_at.isoformat(),
                "recommendations": path.recommendations_json,
                "reasoning": path.reasoning,
                "metadata": {
                    "total_recommendations": len(path.recommendations_json),
                    "high_priority_count": sum(1 for r in path.recommendations_json if r.get("priority") == 1),
                    "estimated_total_time_minutes": sum(r.get("estimated_time_minutes", 0) for r in path.recommendations_json),
                    "cached": True
                }
            }

            # Cache for 24 hours (86400 seconds)
            success = await cache_client.set_json(
                cache_key,
                cache_data,
                ttl=ADAPTIVE_PATH_TTL
            )

            if success:
                logger.info(f"Cached adaptive path for student {student_id[:8]}... (TTL: {ADAPTIVE_PATH_TTL}s = 24h)")
            else:
                logger.warning(f"Failed to cache adaptive path for student {student_id[:8]}...")

        except Exception as e:
            logger.warning(f"Failed to cache path for student {student_id[:8]}...: {str(e)}")

    @staticmethod
    async def invalidate_cache(
        db: AsyncSession,
        student_id: str
    ) -> bool:
        """
        Invalidate cached adaptive path for a student.

        Call this when student completes a new quiz or significantly changes performance.

        Args:
            db: Database session
            student_id: Student UUID

        Returns:
            True if cache was invalidated, False otherwise
        """
        from app.utils.redis_client import cache_client

        try:
            cache_key = f"adaptive_path:{student_id}"
            success = await cache_client.delete(cache_key)

            if success:
                logger.info(f"Invalidated cache for student {student_id[:8]}...")

            return success

        except Exception as e:
            logger.warning(f"Failed to invalidate cache for student {student_id[:8]}...: {str(e)}")
            return False

    @staticmethod
    async def get_cache_stats(
        db: AsyncSession,
        student_id: str
    ) -> Dict[str, Any]:
        """
        Get cache statistics for a student's adaptive path.

        Args:
            db: Database session
            student_id: Student UUID

        Returns:
            Dictionary with cache stats (exists, ttl, age_hours)
        """
        from app.utils.redis_client import cache_client, ADAPTIVE_PATH_TTL

        try:
            cache_key = f"adaptive_path:{student_id}"
            exists = await cache_client.exists(cache_key)

            if not exists:
                return {
                    "cached": False,
                    "ttl_seconds": None,
                    "age_hours": None
                }

            ttl = await cache_client.ttl(cache_key)

            # Calculate age: 24h - ttl_remaining
            if ttl > 0:
                age_seconds = ADAPTIVE_PATH_TTL - ttl
                age_hours = age_seconds / 3600
            else:
                age_hours = None

            return {
                "cached": True,
                "ttl_seconds": ttl if ttl > 0 else 0,
                "age_hours": round(age_hours, 2) if age_hours else None,
                "ttl_hours": round(ttl / 3600, 2) if ttl > 0 else 0
            }

        except Exception as e:
            logger.warning(f"Failed to get cache stats for student {student_id[:8]}...: {str(e)}")
            return {
                "cached": False,
                "error": str(e)
            }

