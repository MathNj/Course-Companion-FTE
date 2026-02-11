"""
Cleanup Script: Remove all test users with @example.com email addresses

Run this script with: python scripts/cleanup_test_users.py
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.sql import select, delete
from app.models.user import User
from app.config import settings


async def cleanup_test_users():
    """Remove all users with @example.com email addresses"""
    engine = create_async_engine(settings.database_url)

    async with engine.begin() as conn:
        # Delete all users with @example.com email
        result = await conn.execute(
            delete(User).where(User.email.like('%@example.com'))
        )
        print(f"Deleted {result.rowcount} test users with @example.com email")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(cleanup_test_users())
