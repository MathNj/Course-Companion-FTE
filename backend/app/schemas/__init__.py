"""
Pydantic Schemas

Data validation and serialization schemas for API requests and responses.
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenRefresh,
)
from app.schemas.progress import (
    ChapterProgressCreate,
    ChapterProgressUpdate,
    ChapterProgressResponse,
    ChapterProgressSummary,
)
from app.schemas.quiz import (
    QuizAttemptCreate,
    QuizAttemptUpdate,
    QuizAttemptResponse,
    QuizAttemptSummary,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenRefresh",
    # Progress schemas
    "ChapterProgressCreate",
    "ChapterProgressUpdate",
    "ChapterProgressResponse",
    "ChapterProgressSummary",
    # Quiz schemas
    "QuizAttemptCreate",
    "QuizAttemptUpdate",
    "QuizAttemptResponse",
    "QuizAttemptSummary",
]
