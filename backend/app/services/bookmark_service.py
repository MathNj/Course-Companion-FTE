"""
Bookmarking Service

Allows users to bookmark chapters and sections for quick access.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookmark import Bookmark, BookmarkFolder
from app.models.user import User

logger = logging.getLogger(__name__)


class BookmarkService:
    """Service for managing user bookmarks."""

    async def create_bookmark(
        self,
        db: AsyncSession,
        user_id: UUID,
        chapter_id: str,
        title: str,
        section_id: Optional[str] = None,
        folder_id: Optional[UUID] = None,
        notes: Optional[str] = None
    ) -> Bookmark:
        """
        Create a new bookmark.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter identifier
            section_id: Section identifier (None for whole chapter)
            title: Custom title or auto-generated
            folder_id: Optional folder ID
            notes: Optional notes

        Returns:
            Created bookmark
        """
        bookmark = Bookmark(
            id=uuid4(),
            user_id=user_id,
            chapter_id=chapter_id,
            section_id=section_id,
            title=title,
            folder_id=folder_id,
            notes=notes,
            is_premium=False  # All users can bookmark (Phase 1)
        )

        db.add(bookmark)
        await db.commit()
        await db.refresh(bookmark)

        logger.info(f"Created bookmark {bookmark.id} for user {user_id}")
        return bookmark

    async def get_user_bookmarks(
        self,
        db: AsyncSession,
        user_id: UUID,
        folder_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[Bookmark]:
        """
        Get all bookmarks for a user.

        Args:
            db: Database session
            user_id: User ID
            folder_id: Optional folder filter
            limit: Max results to return

        Returns:
            List of bookmarks sorted by creation date (newest first)
        """
        query = select(Bookmark).where(Bookmark.user_id == user_id)

        if folder_id:
            query = query.where(Bookmark.folder_id == folder_id)

        query = query.order_by(Bookmark.created_at.desc())

        result = await db.execute(query.limit(limit))
        bookmarks = result.scalars().all()

        logger.info(f"Retrieved {len(bookmarks)} bookmarks for user {user_id}")
        return bookmarks

    async def update_bookmark(
        self,
        db: AsyncSession,
        bookmark_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Bookmark]:
        """
        Update bookmark title or notes.

        Args:
            db: Database session
            bookmark_id: Bookmark ID
            user_id: User ID (for ownership check)
            title: New title
            notes: New notes

        Returns:
            Updated bookmark or None if not found
        """
        result = await db.execute(
            select(Bookmark).where(
                Bookmark.id == bookmark_id,
                Bookmark.user_id == user_id
            )
        )

        bookmark = await result.scalar_one_or_none()

        if not bookmark:
            logger.warning(f"Bookmark {bookmark_id} not found for user {user_id}")
            return None

        if title is not None:
            bookmark.title = title
        if notes is not None:
            bookmark.notes = notes
        bookmark.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(bookmark)

        logger.info(f"Updated bookmark {bookmark_id}")
        return bookmark

    async def delete_bookmark(
        self,
        db: AsyncSession,
        bookmark_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a bookmark.

        Args:
            db: Database session
            bookmark_id: Bookmark ID
            user_id: User ID (for ownership check)

        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(
            select(Bookmark).where(
                Bookmark.id == bookmark_id,
                Bookmark.user_id == user_id
            )
        )

        bookmark = await result.scalar_one_or_none()

        if not bookmark:
            logger.warning(f"Bookmark {bookmark_id} not found for user {user_id}")
            return False

        await db.delete(bookmark)

        await db.commit()

        logger.info(f"Deleted bookmark {bookmark_id}")
        return True

    async def create_folder(
        self,
        db: AsyncSession,
        user_id: UUID,
        name: str,
        description: Optional[str] = None
    ) -> BookmarkFolder:
        """
        Create a bookmark folder for organization.

        Args:
            db: Database session
            user_id: User ID
            name: Folder name
            description: Folder description

        Returns:
            Created folder
        """
        folder = BookmarkFolder(
            id=uuid4(),
            user_id=user_id,
            name=name,
            description=description
        )

        db.add(folder)
        await db.commit()
        await db.refresh(folder)

        logger.info(f"Created folder {folder.id} for user {user_id}")
        return folder

    async def get_user_folders(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> List[BookmarkFolder]:
        """
        Get all folders for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of folders sorted by name
        """
        result = await db.execute(
            select(BookmarkFolder).where(BookmarkFolder.user_id == user_id)
            .order_by(BookmarkFolder.name)
        )

        folders = result.scalars().all()

        logger.info(f"Retrieved {len(folders)} folders for user {user_id}")
        return folders

    async def update_folder(
        self,
        db: AsyncSession,
        folder_id: UUID,
        user_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[BookmarkFolder]:
        """
        Update folder details.

        Args:
            db: Database session
            folder_id: Folder ID
            user_id: User ID (for ownership check)
            name: New name
            description: New description

        Returns:
            Updated folder or None
        """
        result = await db.execute(
            select(BookmarkFolder).where(
                BookmarkFolder.id == folder_id,
                BookmarkFolder.user_id == user_id
            )
        )

        folder = await result.scalar_one_or_none()

        if not folder:
            return None

        if name is not None:
            folder.name = name
        if description is not None:
            folder.description = description

        await db.commit()
        await db.refresh(folder)

        logger.info(f"Updated folder {folder_id}")
        return folder

    async def delete_folder(
        self,
        db: AsyncSession,
        folder_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a folder and its bookmarks.

        Args:
            db: Database session
            folder_id: Folder ID
            user_id: User ID (for ownership check)

        Returns:
            True if deleted, False if not found
        """
        # Delete bookmarks in folder
        await db.execute(
            select(Bookmark).where(
                Bookmark.folder_id == folder_id,
                Bookmark.user_id == user_id
            )
        ).delete()

        # Delete folder
        result = await db.execute(
            select(BookmarkFolder).where(
                BookmarkFolder.id == folder_id,
                BookmarkFolder.user_id == user_id
            )
        )

        folder = await result.scalar_one_or_none()

        if not folder:
            return False

        await db.delete(folder)

        await db.commit()

        logger.info(f"Deleted folder {folder_id} and its bookmarks")
        return True

    async def get_bookmark_stats(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get bookmark statistics for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Statistics dictionary
        """
        total_bookmarks = await db.execute(
            select(Bookmark.id).where(Bookmark.user_id == user_id)
        )
        total = total_bookmarks.scalar_one() or 0

        total_folders = await db.execute(
            select(BookmarkFolder.id).where(BookmarkFolder.user_id == user_id)
        )
        folders = total_folders.scalar_one() or 0

        # Count by chapter
        chapter_counts = await db.execute(
            select(Bookmark.chapter_id, Bookmark.id)
            .where(Bookmark.user_id == user_id)
            .group_by(Bookmark.chapter_id)
        )

        chapter_counts = {
            row[0]: row[1]
            for row in chapter_counts.all()
        }

        return {
            "total_bookmarks": total,
            "total_folders": folders,
            "chapter_counts": chapter_counts,
            "most_bookmarked_chapter": max(
                chapter_counts.items(),
                key=lambda item: item[1],
                default=(None, 0)
            )[0] if chapter_counts else (None, 0)
        }
