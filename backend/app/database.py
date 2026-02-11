"""
Database Connection Module

Provides async SQLAlchemy engine and session management.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

from app.config import settings


# Create async engine
# For asyncpg with SSL on Fly.io/Neon, we need to pass SSL via connect_args
# The DATABASE_URL contains sslmode which asyncpg doesn't recognize in query string
connect_args = {}
if settings.app_env == "production" or "neon.tech" in settings.database_url:
    # Enable SSL for production databases (Fly.io, Neon, etc.)
    connect_args = {"ssl": "require"}

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Verify connections before using
    poolclass=NullPool if settings.app_env == "test" else None,  # Disable pooling in tests
    connect_args=connect_args,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get database session.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database (create tables if they don't exist).

    Note: In production, use Alembic migrations instead.
    This is mainly for testing and local development.
    """
    from app.models import Base

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections (cleanup on shutdown).
    """
    await engine.dispose()
