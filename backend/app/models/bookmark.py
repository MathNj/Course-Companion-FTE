"""
Bookmark and Bookmark Folder Models

Users can bookmark chapters and sections for quick access.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class BookmarkFolder(Base, TimestampMixin):
    """
    Bookmark folder for organizing bookmarks.
    """

    __tablename__ = "bookmark_folders"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign key to user
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Folder details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    bookmarks: Mapped[List["Bookmark"]] = relationship(
        "Bookmark",
        back_populates="folder",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<BookmarkFolder {self.id} -> {self.name}>"


class Bookmark(Base, TimestampMixin):
    """
    User bookmark for chapters or sections.
    """

    __tablename__ = "bookmarks"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    folder_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("bookmark_folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Bookmark details
    chapter_id: Mapped[str] = mapped_column(
        String(50),  # "chapter-1", "chapter-2", etc.
        nullable=False,
        index=True,
    )

    section_id: Mapped[Optional[str]] = mapped_column(
        String(100),  # Section ID
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    is_premium: Mapped[Boolean] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    folder: Mapped[Optional["BookmarkFolder"]] = relationship(
        "BookmarkFolder",
        back_populates="bookmarks"
    )

    def __repr__(self) -> str:
        return f"<Bookmark {self.id} -> {self.title}>"
