"""
Create a demo teacher account for testing

Run this script with: python scripts/create_demo_teacher.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.utils.auth import hash_password
from app.config import settings


async def create_demo_teacher():
    """Create a demo teacher account"""
    engine = create_async_engine(settings.database_url)

    async with AsyncSession(engine) as session:
        # Check if demo teacher already exists
        result = await session.execute(
            select(User).where(User.email == "teacher@demo.com")
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("Demo teacher account already exists")
            print(f"Email: teacher@demo.com")
            print(f"ID: {existing.id}")
            return

        # Create demo teacher
        demo_teacher = User(
            email="teacher@demo.com",
            password_hash=hash_password("Demo123!"),
            full_name="Demo Teacher",
            is_teacher=True,
            is_active=True,
            subscription_tier="premium"
        )

        session.add(demo_teacher)
        await session.commit()

        print("Demo teacher account created successfully!")
        print("Email: teacher@demo.com")
        print("Password: Demo123!")
        print("Account is marked as teacher and has premium subscription")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_demo_teacher())
