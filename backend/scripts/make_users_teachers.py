"""
Make specific users teachers

Run this script with: python scripts/make_users_teachers.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, update
from app.models.user import User
from app.config import settings


async def make_users_teachers():
    """Make specific users teachers"""
    engine = create_async_engine(settings.database_url)

    emails_to_update = [
        "teacher@test.com",
        "mathnj120@gmail.com"
    ]

    async with AsyncSession(engine) as session:
        for email in emails_to_update:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if user:
                if not user.is_teacher:
                    user.is_teacher = True
                    print(f"Made {email} a teacher")
                else:
                    print(f"{email} is already a teacher")
            else:
                print(f"User {email} not found")

        await session.commit()

    await engine.dispose()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(make_users_teachers())
