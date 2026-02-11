"""
Verification Script: Check for any remaining @example.com users
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.sql import select
from app.models.user import User
from app.config import settings


async def verify_cleanup():
    """Check for any remaining users with @example.com email"""
    engine = create_async_engine(settings.database_url)

    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).where(User.email.like('%@example.com'))
        )
        users = result.scalars().all()

        if users:
            print(f"Found {len(users)} remaining @example.com users:")
            for user in users:
                print(f"  - {user.email}")
        else:
            print("Success! No @example.com users found in database. Cleanup successful!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(verify_cleanup())
