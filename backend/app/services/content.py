"""
Content Service

Business logic for fetching and caching course content (chapters and quizzes).
"""

import json
import logging
from typing import Optional, Dict, Any
from app.utils.storage import r2_client
from app.utils.cache import cache_client, CacheKeys
from app.config import settings

logger = logging.getLogger(__name__)


async def get_chapter_with_cache(chapter_id: str) -> Optional[Dict[str, Any]]:
    """
    Get chapter content with Redis caching fallback to R2/local storage.

    Flow:
    1. Check Redis cache
    2. If not found, fetch from R2/local
    3. Cache the result
    4. Return chapter JSON

    Args:
        chapter_id: Chapter identifier (e.g., "chapter-1")

    Returns:
        Chapter content dictionary, or None if not found
    """
    cache_key = CacheKeys.chapter_content(chapter_id)

    # Try cache first
    cached_content = await cache_client.get_json(cache_key)
    if cached_content:
        logger.info(f"Chapter {chapter_id} served from cache")
        return cached_content

    # Cache miss - fetch from storage
    logger.info(f"Chapter {chapter_id} cache miss - fetching from storage")

    # For local development, try local files first
    # In production with R2 configured, this will use R2
    chapter_content = await _fetch_chapter_from_storage(chapter_id)

    if chapter_content:
        # Cache for 24 hours (86400 seconds)
        ttl = settings.content_cache_ttl
        await cache_client.set_json(cache_key, chapter_content, ttl=ttl)
        logger.info(f"Chapter {chapter_id} cached with TTL {ttl}s")

    return chapter_content


async def get_quiz_with_cache(quiz_id: str, exclude_answers: bool = True) -> Optional[Dict[str, Any]]:
    """
    Get quiz content with Redis caching fallback to R2/local storage.

    Flow:
    1. Check Redis cache
    2. If not found, fetch from R2/local
    3. Optionally exclude answer keys and explanations
    4. Cache the result
    5. Return quiz JSON

    Args:
        quiz_id: Quiz identifier (e.g., "chapter-1-quiz")
        exclude_answers: If True, remove answer_key and explanations from response

    Returns:
        Quiz content dictionary, or None if not found
    """
    cache_key = CacheKeys.quiz_content(quiz_id)

    # Try cache first
    cached_content = await cache_client.get_json(cache_key)
    if cached_content:
        logger.info(f"Quiz {quiz_id} served from cache")
        quiz_content = cached_content
    else:
        # Cache miss - fetch from storage
        logger.info(f"Quiz {quiz_id} cache miss - fetching from storage")
        quiz_content = await _fetch_quiz_from_storage(quiz_id)

        if quiz_content:
            # Cache the full quiz (with answers) for grading
            ttl = settings.content_cache_ttl
            await cache_client.set_json(cache_key, quiz_content, ttl=ttl)
            logger.info(f"Quiz {quiz_id} cached with TTL {ttl}s")

    if not quiz_content:
        return None

    # Exclude answer keys if requested (for student-facing endpoints)
    if exclude_answers:
        quiz_content = _remove_answer_keys(quiz_content)

    return quiz_content


async def _fetch_chapter_from_storage(chapter_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch chapter content from R2 or local files.

    Args:
        chapter_id: Chapter identifier

    Returns:
        Chapter content dictionary, or None if not found
    """
    # TODO: Implement local file fallback for development
    # For now, this is a placeholder that will be implemented with content seeding
    logger.warning(f"Chapter storage not yet implemented for {chapter_id}")
    return None


async def _fetch_quiz_from_storage(quiz_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch quiz content from R2 or local files.

    Args:
        quiz_id: Quiz identifier

    Returns:
        Quiz content dictionary, or None if not found
    """
    # TODO: Implement local file fallback for development
    # For now, this is a placeholder that will be implemented with content seeding
    logger.warning(f"Quiz storage not yet implemented for {quiz_id}")
    return None


def _remove_answer_keys(quiz_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove answer keys and explanations from quiz content.

    This ensures students cannot see the correct answers before submitting.

    Args:
        quiz_content: Full quiz content with answers

    Returns:
        Quiz content without answer keys or explanations
    """
    # Create a copy to avoid mutating the cached version
    student_quiz = quiz_content.copy()

    # Remove answer-related fields from each question
    if "questions" in student_quiz:
        for question in student_quiz["questions"]:
            question.pop("answer_key", None)
            question.pop("explanation_correct", None)
            question.pop("explanation_incorrect", None)
            question.pop("explanation", None)

    # Remove quiz-level answer key if present
    student_quiz.pop("answer_key", None)

    return student_quiz


async def invalidate_chapter_cache(chapter_id: str) -> bool:
    """
    Invalidate cached chapter content.

    Useful when chapter content is updated.

    Args:
        chapter_id: Chapter identifier

    Returns:
        True if cache was deleted, False otherwise
    """
    cache_key = CacheKeys.chapter_content(chapter_id)
    result = await cache_client.delete(cache_key)
    if result:
        logger.info(f"Invalidated cache for chapter {chapter_id}")
    return result


async def invalidate_quiz_cache(quiz_id: str) -> bool:
    """
    Invalidate cached quiz content.

    Useful when quiz content is updated.

    Args:
        quiz_id: Quiz identifier

    Returns:
        True if cache was deleted, False otherwise
    """
    cache_key = CacheKeys.quiz_content(quiz_id)
    result = await cache_client.delete(cache_key)
    if result:
        logger.info(f"Invalidated cache for quiz {quiz_id}")
    return result
