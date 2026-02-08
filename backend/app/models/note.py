"""
from app.models.types import UUID as UUIDType, JSON as JSONType
Note and Note Tag Models
from app.models.types import UUID as UUIDType, JSON as JSONType

from app.models.types import UUID as UUIDType, JSON as JSONType
Users can take notes on chapters and sections.
from app.models.types import UUID as UUIDType, JSON as JSONType
"""
from app.models.types import UUID as UUIDType, JSON as JSONType

from app.models.types import UUID as UUIDType, JSON as JSONType
from datetime import datetime
from app.models.types import UUID as UUIDType, JSON as JSONType
from typing import Optional, List
from app.models.types import UUID as UUIDType, JSON as JSONType
from uuid import UUID, uuid4
from app.models.types import UUID as UUIDType, JSON as JSONType

from app.models.types import UUID as UUIDType, JSON as JSONType
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Integer
from app.models.types import UUID as UUIDType, JSON as JSONType

from app.models.types import UUID as UUIDType, JSON as JSONType
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.types import UUID as UUIDType, JSON as JSONType

from app.models.types import UUID as UUIDType, JSON as JSONType
from app.models.base import Base, TimestampMixin
from app.models.types import UUID as UUIDType, JSON as JSONType


class NoteTag(Base, TimestampMixin):
    """
    Tags for organizing and categorizing notes.
    """

    __tablename__ = "note_tags"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    note_id: Mapped[UUID] = mapped_column(
        UUIDType,
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tag details
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True  # Tag names are global per user
    )

    color: Mapped[str] = mapped_column(
        String(7),  # Hex color
        nullable=False
    )

    # Relationships
    note: Mapped["Note"] = relationship("Note", back_populates="tags")

    def __repr__(self) -> str:
        return f"<NoteTag {self.id} -> {self.name}>"


class Note(Base, TimestampMixin):
    """
    User note on a chapter or section.
    """

    __tablename__ = "notes"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Note details
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

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    is_public: Mapped[Boolean] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    tags: Mapped[List["NoteTag"]] = relationship(
        "NoteTag",
        back_populates="note",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Note {self.id} -> {preview}>"
