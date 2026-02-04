"""
Chapter Routes

Endpoints for browsing and accessing course chapter content.
"""

from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.progress import ChapterProgress
from app.dependencies import get_current_user, get_optional_user
from app.services.content import get_chapter_with_cache
from app.services.search import search_chapters as search_chapters_service

router = APIRouter(prefix="/chapters", tags=["Chapters"])


# Chapter metadata (in production, this would come from database or config)
CHAPTER_METADATA = [
    {
        "id": "chapter-1",
        "title": "Introduction to Generative AI",
        "subtitle": "Understanding the fundamentals of AI that creates content",
        "access_tier": "free",
        "estimated_time": "45 minutes",
        "difficulty": "beginner"
    },
    {
        "id": "chapter-2",
        "title": "Large Language Models",
        "subtitle": "How LLMs work and what makes them powerful",
        "access_tier": "free",
        "estimated_time": "60 minutes",
        "difficulty": "beginner"
    },
    {
        "id": "chapter-3",
        "title": "Prompt Engineering Basics",
        "subtitle": "Crafting effective prompts for better AI outputs",
        "access_tier": "free",
        "estimated_time": "50 minutes",
        "difficulty": "intermediate"
    },
    {
        "id": "chapter-4",
        "title": "Advanced Prompt Techniques",
        "subtitle": "Chain-of-thought, few-shot learning, and more",
        "access_tier": "premium",
        "estimated_time": "70 minutes",
        "difficulty": "intermediate"
    },
    {
        "id": "chapter-5",
        "title": "AI Safety and Ethics",
        "subtitle": "Responsible AI development and deployment",
        "access_tier": "premium",
        "estimated_time": "55 minutes",
        "difficulty": "intermediate"
    },
    {
        "id": "chapter-6",
        "title": "Real-World AI Applications",
        "subtitle": "Building practical AI solutions",
        "access_tier": "premium",
        "estimated_time": "80 minutes",
        "difficulty": "advanced"
    }
]


@router.get("/test-no-auth")
async def test_no_auth():
    """Test endpoint without any authentication"""
    return {"status": "ok", "message": "No auth required!"}


@router.get("", response_model=List[dict])
async def get_chapters(
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all chapters with user access and progress info.

    Returns metadata for all 6 chapters including:
    - Basic info (title, subtitle, difficulty, estimated_time)
    - Access status (user_has_access based on subscription tier)
    - Progress status (completion_status, quiz_score)

    For unauthenticated users, returns public metadata only.
    """
    # For authenticated users, fetch progress
    progress_records = {}
    if current_user:
        result = await db.execute(
            select(ChapterProgress).where(ChapterProgress.user_id == current_user.id)
        )
        progress_records = {p.chapter_id: p for p in result.scalars().all()}

    # Build response with metadata + access + progress
    chapters = []
    for chapter_meta in CHAPTER_METADATA:
        chapter_id = chapter_meta["id"]

        # Check access (free tier can access chapters 1-3, premium can access all)
        if current_user:
            user_has_access = (
                chapter_meta["access_tier"] == "free" or
                current_user.subscription_tier in ("premium", "pro")
            )
        else:
            # Unauthenticated users can access free tier content only
            user_has_access = chapter_meta["access_tier"] == "free"

        # Get progress if exists
        progress = progress_records.get(chapter_id)
        user_progress = {
            "completion_status": "completed" if (progress and progress.is_completed) else
                                "in_progress" if progress else "not_started",
            "completion_percentage": progress.completion_percentage if progress else 0,
            "quiz_score": None  # Will be populated when quiz attempts are queried
        }

        chapters.append({
            **chapter_meta,
            "user_has_access": user_has_access,
            "user_progress": user_progress
        })

    return chapters


@router.get("/{chapter_id}", response_model=dict)
async def get_chapter(
    chapter_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get full chapter content by ID.

    Returns complete chapter content including:
    - All sections with markdown content
    - Learning objectives
    - Navigation links (next/previous chapters)

    Access Control:
    - Chapters 1-3: Available to all users (free tier)
    - Chapters 4-6: Require premium subscription

    Returns 403 Forbidden if user doesn't have access.
    Returns 404 Not Found if chapter doesn't exist.

    For unauthenticated users, only free tier chapters are accessible.
    """
    # Find chapter metadata
    chapter_meta = next((c for c in CHAPTER_METADATA if c["id"] == chapter_id), None)

    if not chapter_meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )

    # Check freemium access
    # Unauthenticated users can only access free tier
    user_tier = current_user.subscription_tier if current_user else "free"
    if chapter_meta["access_tier"] == "premium" and user_tier == "free":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "This chapter requires a premium subscription",
                "chapter_title": chapter_meta["title"],
                "upgrade_benefits": [
                    "Access to chapters 4-6 (Advanced Topics)",
                    "Advanced prompt engineering techniques",
                    "AI safety and ethics deep dive",
                    "Real-world application examples",
                    "Certificate of completion"
                ],
                "upgrade_url": "/upgrade"  # TODO: Replace with actual upgrade URL
            }
        )

    # Fetch chapter content from cache/storage
    chapter_content = await get_chapter_with_cache(chapter_id)

    if not chapter_content:
        # Content not yet seeded - return placeholder
        chapter_content = {
            "sections": [],
            "learning_objectives": [],
            "note": "Chapter content will be available after content seeding"
        }

    # Add navigation links
    chapter_index = next((i for i, c in enumerate(CHAPTER_METADATA) if c["id"] == chapter_id), -1)

    chapter_content["navigation"] = {
        "previous_chapter": CHAPTER_METADATA[chapter_index - 1]["id"] if chapter_index > 0 else None,
        "next_chapter": CHAPTER_METADATA[chapter_index + 1]["id"] if chapter_index < len(CHAPTER_METADATA) - 1 else None
    }

    # Combine metadata with content
    response = {
        **chapter_meta,
        **chapter_content
    }

    return response


@router.get("/search", response_model=List[dict])
async def search_chapters(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    chapter_id: Optional[str] = Query(None, description="Limit search to specific chapter"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search across chapter content (Grounded Q&A).

    Performs keyword search across all accessible chapters and returns relevant sections.
    This enables ChatGPT to answer questions using only course material (zero-hallucination).

    Query parameters:
    - **q**: Search query (minimum 2 characters)
    - **limit**: Maximum number of results (default 20, max 100)
    - **chapter_id**: Optional - limit search to specific chapter

    Returns search results with:
    - chapter_id: Which chapter the result is from
    - chapter_title: Chapter title for context
    - section_id: Which section contains the match
    - section_title: Section title for context
    - snippet: Text excerpt with the matched content
    - relevance_score: How well it matches the query (higher is better)
    - match_count: Number of times query terms appear in this section

    Access Control:
    - Only searches chapters the user has access to
    - Free users: chapters 1-3
    - Premium users: all chapters 1-6

    Requires authentication.
    """
    # Determine which chapters user has access to
    accessible_chapters = []
    for chapter_meta in CHAPTER_METADATA:
        user_has_access = (
            chapter_meta["access_tier"] == "free" or
            current_user.subscription_tier in ("premium", "pro")
        )
        if user_has_access:
            accessible_chapters.append(chapter_meta["id"])

    # If specific chapter requested, verify access
    if chapter_id:
        chapter_meta = next((c for c in CHAPTER_METADATA if c["id"] == chapter_id), None)
        if not chapter_meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chapter {chapter_id} not found"
            )

        # Check access
        user_has_access = (
            chapter_meta["access_tier"] == "free" or
            current_user.subscription_tier in ("premium", "pro")
        )
        if not user_has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Chapter {chapter_id} requires premium subscription"
            )

    # Perform search using search service
    results = await search_chapters_service(
        query=q,
        accessible_chapter_ids=accessible_chapters,
        limit=limit,
        chapter_id=chapter_id
    )

    return results
