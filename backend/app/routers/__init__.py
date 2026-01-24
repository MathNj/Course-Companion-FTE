"""
API Routers

FastAPI route handlers organized by feature domain.
"""

from app.routers.auth import router as auth_router

__all__ = ["auth_router"]
