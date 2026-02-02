"""
Note-Taking Service

Allows users to take notes on chapters and sections.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note, NoteTag
from app.models.user import User

logger = logging.getLogger(__name__)


class NoteService:
    """Service for managing user notes."""

    async def create_note(
        self,
        db: AsyncSession,
        user_id: UUID,
        chapter_id: str,
        content: str,
        section_id: Optional[str] = None,
        is_public: bool = False,
        tags: Optional[List[str]] = None
    ) -> Note:
        """
        Create a new note.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter identifier
            section_id: Section identifier (None for whole chapter)
            content: Note content
            is_public: Whether note is shareable
            tags: Optional list of tags

        Returns:
            Created note with tags
        """
        note = Note(
            id=uuid4(),
            user_id=user_id,
            chapter_id=chapter_id,
            section_id=section_id,
            content=content,
            is_public=is_public
        )

        db.add(note)
        await db.flush()

        # Add tags if provided
        if tags:
            for tag_name in tags:
                tag = NoteTag(
                    id=uuid4(),
                    note_id=note.id,
                    user_id=user_id,
                    name=tag_name,
                    color=self._get_tag_color(tag_name)
                )
                db.add(tag)

        await db.commit()
        await db.refresh(note)

        logger.info(f"Created note {note.id} for user {user_id}")
        return note

    async def get_user_notes(
        self,
        db: AsyncSession,
        user_id: UUID,
        chapter_id: Optional[str] = None,
        section_id: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 100
    ) -> List[Note]:
        """
        Get notes for a user with optional filters.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Optional chapter filter
            section_id: Optional section filter
            tag: Optional tag filter
            limit: Max results to return

        Returns:
            List of notes sorted by creation date (newest first)
        """
        # Base query
        query = select(Note).where(Note.user_id == user_id)

        # Apply filters
        if chapter_id:
            query = query.where(Note.chapter_id == chapter_id)
        if section_id:
            query = query.where(Note.section_id == section_id)
        if tag:
            # Join with tags table
            query = query.join(Note.tags).where(NoteTag.name == tag)

        # Order by creation date
        query = query.order_by(Note.created_at.desc())

        result = await db.execute(query.limit(limit))
        notes = result.scalars().all()

        logger.info(f"Retrieved {len(notes)} notes for user {user_id}")
        return notes

    async def update_note(
        self,
        db: AsyncSession,
        note_id: UUID,
        user_id: UUID,
        content: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> Optional[Note]:
        """
        Update note content or public status.

        Args:
            db: Database session
            note_id: Note ID
            user_id: User ID (for ownership check)
            content: New content
            is_public: New public status

        Returns:
            Updated note or None if not found
        """
        result = await db.execute(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == user_id
            )
        )

        note = await result.scalar_one_or_none()

        if not note:
            logger.warning(f"Note {note_id} not found for user {user_id}")
            return None

        if content is not None:
            note.content = content
        if is_public is not None:
            note.is_public = is_public

        note.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(note)

        logger.info(f"Updated note {note_id}")
        return note

    async def delete_note(
        self,
        db: AsyncSession,
        note_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a note.

        Args:
            db: Database session
            note_id: Note ID
            user_id: User ID (for ownership check)

        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == user_id
            )
        )

        note = await result.scalar_one_or_none()

        if not note:
            logger.warning(f"Note {note_id} not found for user {user_id}")
            return False

        # Delete tags (cascade should handle this, but be explicit)
        await db.execute(
            select(NoteTag).where(NoteTag.note_id == note_id)
        ).delete()

        await db.delete(note)

        await db.commit()

        logger.info(f"Deleted note {note_id}")
        return True

    async def get_all_tags(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> List[str]:
        """
        Get all unique tags for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of unique tag names
        """
        result = await db.execute(
            select(NoteTag.name)
            .where(NoteTag.user_id == user_id)
            .distinct()
            .order_by(NoteTag.name)
        )

        tags = result.scalars().all()

        logger.info(f"Retrieved {len(tags)} unique tags for user {user_id}")
        return tags

    async def get_note_stats(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get note statistics for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Statistics dictionary
        """
        # Total notes
        total_notes = await db.execute(
            select(Note.id).where(Note.user_id == user_id)
        )
        total = total_notes.scalar_one() or 0

        # Public vs private
        public_count = await db.execute(
            select(Note.id).where(
                Note.user_id == user_id,
                Note.is_public == True
            )
        )
        public_notes = public_count.scalar_one() or 0

        # Notes by chapter
        chapter_counts = await db.execute(
            select(Note.chapter_id, func.count(Note.id))
            .where(Note.user_id == user_id)
            .group_by(Note.chapter_id)
        )

        chapter_counts = {
            row[0]: row[1]
            for row in chapter_counts.all()
        }

        # Most recent note
        recent_note = await db.execute(
            select(Note)
            .where(Note.user_id == user_id)
            .order_by(Note.created_at.desc())
            .first()
        )

        return {
            "total_notes": total,
            "public_notes": public_notes,
            "private_notes": total - public_notes,
            "chapter_counts": chapter_counts,
            "most_recent_note": recent_note.created_at if recent_note else None
        }

    def _get_tag_color(self, tag_name: str) -> str:
        """Get color for a tag based on its name (hash-based)."""
        import hashlib

        # Hash tag name to a color
        hash_val = int(hashlib.md5(tag_name.encode()).hexdigest()[:8], 16)
        colors = [
            '#ef4444', '#f97316', '#f59e0b', '#fbbf24', '#84cc16',
            '#10b981', '#06b6d4', '#3b82f6', '#8b5cf6', '#d946ef',
            '#666666', '#a3a3a3', '#717171', '#989898', '#c4c4c4'
        ]
        return colors[hash_val % len(colors)]
