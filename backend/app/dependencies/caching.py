"""
Caching Dependencies for FastAPI Endpoints

Decorators and dependency functions for cache-optimized API responses.
"""

import hashlib
import json
import logging
from functools import wraps
from typing import Optional, Callable, Any
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

from app.utils.cache import cache_client, CacheKeys

logger = logging.getLogger(__name__)


# Cache TTL constants
TTL_IMMUTABLE = 86400  # 24 hours
TTL_USER_SPECIFIC = 300  # 5 minutes
TTL_SEARCH = 60  # 1 minute


def cached_response(ttl: int = TTL_USER_SPECIFIC):
    """
    Decorator to cache API responses.

    Usage:
        @cached_response(ttl=TTL_IMMUTABLE)
        async def get_chapter(chapter_id: str):
            return fetch_chapter_content(chapter_id)

    Args:
        ttl: Time-to-live in seconds
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get from cache
            cache_key = f"response:{func.__name__}:{args}:{kwargs}"

            cached = await cache_client.get_json(cache_key)
            if cached is not None:
                logger.debug(f"Cache HIT: {func.__name__}")
                return JSONResponse(
                    content=cached,
                    headers={
                        "X-Cache": "HIT",
                        "Cache-Control": f"max-age={ttl}"
                    }
                )

            # Cache miss - call function
            logger.debug(f"Cache MISS: {func.__name__}")
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_client.set_json(cache_key, result, ttl=ttl)

            return JSONResponse(
                content=result,
                headers={
                    "X-Cache": "MISS",
                    "Cache-Control": f"max-age={ttl}"
                }
            )

        return wrapper
    return decorator


async def get_cached_chapter_content(
    chapter_id: str,
    fetch_func: Callable
) -> JSONResponse:
    """
    Get chapter content with caching.

    Args:
        chapter_id: Chapter identifier
        fetch_func: Async function to fetch content if not cached

    Returns:
        JSONResponse with chapter content
    """
    cache_key = CacheKeys.chapter_content(chapter_id)

    # Try cache first
    cached = await cache_client.get_json(cache_key)
    if cached is not None:
        logger.info(f"Chapter cache HIT: {chapter_id}")
        return JSONResponse(
            content=cached,
            headers={
                "X-Cache": "HIT",
                "Cache-Control": f"public, max-age={TTL_IMMUTABLE}, immutable",
                "ETag": hashlib.sha256(json.dumps(cached).encode()).hexdigest()[:16]
            }
        )

    # Cache miss - fetch content
    logger.info(f"Chapter cache MISS: {chapter_id}")
    content = await fetch_func(chapter_id)

    # Cache for 24 hours
    await cache_client.set_json(cache_key, content, ttl=TTL_IMMUTABLE)

    return JSONResponse(
        content=content,
        headers={
            "X-Cache": "MISS",
            "Cache-Control": f"public, max-age={TTL_IMMUTABLE}, immutable"
        }
    )


async def get_cached_quiz_content(
    quiz_id: str,
    fetch_func: Callable
) -> JSONResponse:
    """
    Get quiz content with caching.

    Args:
        quiz_id: Quiz identifier
        fetch_func: Async function to fetch quiz if not cached

    Returns:
        JSONResponse with quiz content
    """
    cache_key = CacheKeys.quiz_content(quiz_id)

    # Try cache first
    cached = await cache_client.get_json(cache_key)
    if cached is not None:
        logger.info(f"Quiz cache HIT: {quiz_id}")
        return JSONResponse(
            content=cached,
            headers={
                "X-Cache": "HIT",
                "Cache-Control": f"public, max-age={TTL_IMMUTABLE}, immutable"
            }
        )

    # Cache miss - fetch quiz
    logger.info(f"Quiz cache MISS: {quiz_id}")
    quiz = await fetch_func(quiz_id)

    # Cache for 24 hours
    await cache_client.set_json(cache_key, quiz, ttl=TTL_IMMUTABLE)

    return JSONResponse(
        content=quiz,
        headers={
            "X-Cache": "MISS",
            "Cache-Control": f"public, max-age={TTL_IMMUTABLE}, immutable"
        }
    )


def invalidate_cache_pattern(pattern: str):
    """
    Invalidate all cache keys matching a pattern.

    Usage:
        invalidate_cache_pattern("chapter:*")
        invalidate_cache_pattern(f"progress:{user_id}:*")

    Args:
        pattern: Glob pattern for cache keys
    """
    async def _invalidate():
        count = await cache_client.delete_pattern(pattern)
        logger.info(f"Invalidated {count} cache keys matching: {pattern}")

    return _invalidate()
