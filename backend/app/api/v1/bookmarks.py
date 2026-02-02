"""
Bookmarks and Notes API Endpoints

RESTful endpoints for user bookmarks and notes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.bookmark import Bookmark, BookmarkFolder
from app.models.note import Note, NoteTag
from app.services.bookmark_service import BookmarkService
from app.services.note_service import NoteService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/bookmarks", tags=["Bookmarks & Notes"])


# Request/Response Schemas
class CreateBookmarkRequest(BaseModel):
    chapter_id: str
    section_id: Optional[str] = None
    title: Optional[str] = None
    folder_id: Optional[str] = None
    notes: Optional[str] = None


class UpdateBookmarkRequest(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    folder_id: Optional[str] = None


class CreateNoteRequest(BaseModel):
    chapter_id: str
    section_id: Optional[str] = None
    content: str
    is_public: bool = False
    tags: Optional[List[str]] = None


class UpdateNoteRequest(BaseModel):
    content: Optional[str] = None
    is_public: Optional[bool] = None


class CreateFolderRequest(BaseModel):
    name: str
    description: Optional[str] = None


# ==================== Bookmarks ====================

@router.post("")
async def create_bookmark(
    request: CreateBookmarkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new bookmark."""
    service = BookmarkService()

    # Generate title if not provided
    title = request.title or f"Bookmark for {request.chapter_id}"
    if request.section_id:
        title += f" - {request.section_id}"

    bookmark = await service.create_bookmark(
        db=db,
        user_id=current_user.id,
        chapter_id=request.chapter_id,
        section_id=request.section_id,
        title=title,
        folder_id=request.folder_id,
        notes=request.notes
    )

    return {
        "id": str(bookmark.id),
        "chapter_id": bookmark.chapter_id,
        "section_id": bookmark.section_id,
        "title": bookmark.title,
        "folder_id": str(bookmark.folder_id) if bookmark.folder_id else None,
        "notes": bookmark.notes,
        "created_at": bookmark.created_at.isoformat(),
        "updated_at": bookmark.updated_at.isoformat()
    }


@router.get("")
async def get_bookmarks(
    folder_id: Optional[str] = Query(None),
    chapter_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's bookmarks with optional filters."""
    service = BookmarkService()

    bookmarks = await service.get_user_bookmarks(
        db=db,
        user_id=current_user.id,
        folder_id=folder_id,
        chapter_id=chapter_id
    )

    return {
        "bookmarks": [
            {
                "id": str(b.id),
                "chapter_id": b.chapter_id,
                "section_id": b.section_id,
                "title": b.title,
                "folder_id": str(b.folder_id) if b.folder_id else None,
                "notes": b.notes,
                "created_at": b.created_at.isoformat(),
                "updated_at": b.updated_at.isoformat()
            }
            for b in bookmarks
        ]
    }


@router.put("/{bookmark_id}")
async def update_bookmark(
    bookmark_id: str,
    request: UpdateBookmarkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a bookmark."""
    service = BookmarkService()

    bookmark = await service.update_bookmark(
        db=db,
        bookmark_id=bookmark_id,
        user_id=current_user.id,
        title=request.title,
        notes=request.notes,
        folder_id=request.folder_id
    )

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )

    return {
        "id": str(bookmark.id),
        "chapter_id": bookmark.chapter_id,
        "section_id": bookmark.section_id,
        "title": bookmark.title,
        "folder_id": str(bookmark.folder_id) if bookmark.folder_id else None,
        "notes": bookmark.notes,
        "created_at": bookmark.created_at.isoformat(),
        "updated_at": bookmark.updated_at.isoformat()
    }


@router.delete("/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a bookmark."""
    service = BookmarkService()

    success = await service.delete_bookmark(
        db=db,
        bookmark_id=bookmark_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )

    return {"message": "Bookmark deleted successfully"}


# ==================== Folders ====================

@router.post("/folders")
async def create_folder(
    request: CreateFolderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new bookmark folder."""
    service = BookmarkService()

    folder = await service.create_folder(
        db=db,
        user_id=current_user.id,
        name=request.name,
        description=request.description
    )

    return {
        "id": str(folder.id),
        "name": folder.name,
        "description": folder.description,
        "created_at": folder.created_at.isoformat()
    }


@router.get("/folders")
async def get_folders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's bookmark folders."""
    service = BookmarkService()

    folders = await service.get_user_folders(db=db, user_id=current_user.id)

    return {
        "folders": [
            {
                "id": str(f.id),
                "name": f.name,
                "description": f.description,
                "created_at": f.created_at.isoformat()
            }
            for f in folders
        ]
    }


@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a folder and all its bookmarks."""
    service = BookmarkService()

    success = await service.delete_folder(
        db=db,
        folder_id=folder_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )

    return {"message": "Folder deleted successfully"}


# ==================== Notes ====================

@router.post("/notes")
async def create_note(
    request: CreateNoteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new note."""
    service = NoteService()

    note = await service.create_note(
        db=db,
        user_id=current_user.id,
        chapter_id=request.chapter_id,
        section_id=request.section_id,
        content=request.content,
        is_public=request.is_public,
        tags=request.tags
    )

    # Load tags
    await db.refresh(note)

    return {
        "id": str(note.id),
        "chapter_id": note.chapter_id,
        "section_id": note.section_id,
        "content": note.content,
        "is_public": note.is_public,
        "tags": [
            {"name": tag.name, "color": tag.color}
            for tag in note.tags
        ],
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat()
    }


@router.get("/notes")
async def get_notes(
    chapter_id: Optional[str] = Query(None),
    section_id: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    limit: int = Query(100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's notes with optional filters."""
    service = NoteService()

    notes = await service.get_user_notes(
        db=db,
        user_id=current_user.id,
        chapter_id=chapter_id,
        section_id=section_id,
        tag=tag,
        limit=limit
    )

    return {
        "notes": [
            {
                "id": str(n.id),
                "chapter_id": n.chapter_id,
                "section_id": n.section_id,
                "content": n.content,
                "is_public": n.is_public,
                "tags": [{"name": t.name, "color": t.color} for t in n.tags],
                "created_at": n.created_at.isoformat(),
                "updated_at": n.updated_at.isoformat()
            }
            for n in notes
        ]
    }


@router.put("/notes/{note_id}")
async def update_note(
    note_id: str,
    request: UpdateNoteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a note."""
    service = NoteService()

    note = await service.update_note(
        db=db,
        note_id=note_id,
        user_id=current_user.id,
        content=request.content,
        is_public=request.is_public
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    await db.refresh(note)

    return {
        "id": str(note.id),
        "chapter_id": note.chapter_id,
        "section_id": note.section_id,
        "content": note.content,
        "is_public": note.is_public,
        "tags": [{"name": t.name, "color": t.color} for t in note.tags],
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat()
    }


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a note."""
    service = NoteService()

    success = await service.delete_note(
        db=db,
        note_id=note_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    return {"message": "Note deleted successfully"}


@router.get("/notes/tags")
async def get_all_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all unique tags for user."""
    service = NoteService()

    tags = await service.get_all_tags(db=db, user_id=current_user.id)

    return {"tags": tags}


@router.get("/stats")
async def get_bookmark_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bookmark and note statistics."""
    bookmark_service = BookmarkService()
    note_service = NoteService()

    bookmark_stats = await bookmark_service.get_bookmark_stats(db=db, user_id=current_user.id)
    note_stats = await note_service.get_note_stats(db=db, user_id=current_user.id)

    return {
        "bookmarks": bookmark_stats,
        "notes": note_stats
    }
