"""
Test script to verify teacher students endpoint is working.
"""
import asyncio
import sys
sys.path.insert(0, 'C:/Users/Najma-LP/Desktop/Course-Companion-FTE/backend')

from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.progress import ChapterProgress
from app.models.quiz import QuizAttempt
from app.models.streak import Streak


async def check_database():
    """Check what users exist and their is_teacher status."""
    async for db in get_db():
        # Get all users
        result = await db.execute(select(User))
        users = result.scalars().all()

        print(f"\n=== USERS IN DATABASE ({len(users)} total) ===\n")

        for user in users:
            # Get chapter progress
            progress_result = await db.execute(
                select(ChapterProgress).where(ChapterProgress.user_id == user.id)
            )
            progress = progress_result.scalars().all()

            completed = len([p for p in progress if p.is_completed])

            print(f"Email: {user.email}")
            print(f"  ID: {user.id}")
            print(f"  is_teacher: {user.is_teacher}")
            print(f"  is_active: {user.is_active}")
            print(f"  Chapters completed: {completed}")
            print(f"  Progress records: {len(progress)}")
            print()

        # Now test the query that the teacher endpoint uses
        print("\n=== TESTING TEACHER QUERY ===\n")

        from sqlalchemy import or_
        result = await db.execute(
            select(User).where(
                User.is_active == True,
                or_(User.is_teacher == False, User.is_teacher == None)
            )
        )
        students = result.scalars().all()

        print(f"Students found: {len(students)}")
        for student in students:
            print(f"  - {student.email} (is_teacher={student.is_teacher})")

        break


if __name__ == "__main__":
    asyncio.run(check_database())
