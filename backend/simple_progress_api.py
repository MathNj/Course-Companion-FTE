"""
Simple Progress Tracking API for Testing
In-memory progress tracking (for development/testing without database)
"""

import json
import os
from datetime import datetime, date
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

app = FastAPI(
    title="Course Companion FTE - Progress Tracking API",
    description="Simple progress tracking for Generative AI Fundamentals",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage file
PROGRESS_FILE = Path(__file__).parent / "progress_data.json"

# Course structure
COURSE_STRUCTURE = {
    "total_chapters": 4,
    "chapters": [
        {"id": "chapter-1", "title": "The Age of Synthesis: An Introduction to Generative AI"},
        {"id": "chapter-2", "title": "What are LLMs?"},
        {"id": "chapter-3", "title": "Transformer Architecture"},
        {"id": "chapter-4", "title": "Prompt Engineering Basics"}
    ]
}

# In-memory progress storage (for demo user)
user_progress = {
    "user_id": "demo-user",
    "chapters": {},
    "streak": {
        "current_streak": 0,
        "longest_streak": 0,
        "total_active_days": 0,
        "last_activity_date": None
    },
    "quiz_attempts": {},
    "achievements": []
}


# Response Models
class ChapterProgressResponse(BaseModel):
    chapter_id: str
    completion_percentage: int
    is_completed: bool
    time_spent_seconds: int
    started_at: str
    last_accessed: str


class ProgressUpdate(BaseModel):
    chapter_id: str
    time_spent_seconds: int = 0
    completion_percentage: int = 0
    mark_completed: bool = False


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    total_active_days: int
    last_activity_date: str
    is_active: bool


class DashboardResponse(BaseModel):
    overall_completion_percentage: int
    completed_chapters: int
    in_progress_chapters: int
    not_started_chapters: int
    total_time_spent_seconds: int
    streak: Dict
    chapters: List[Dict]
    achievements: List[str]


# Helper functions
def load_progress():
    """Load progress from file"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return user_progress


def save_progress(progress):
    """Save progress to file"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, default=str)


def update_streak(progress):
    """Update streak based on activity"""
    today = date.today().isoformat()
    streak = progress["streak"]

    if streak["last_activity_date"] is None:
        # First activity
        streak["current_streak"] = 1
        streak["longest_streak"] = 1
        streak["total_active_days"] = 1
        streak["last_activity_date"] = today
        return {
            "milestone": "First Step",
            "message": "Welcome! You've started your learning journey!"
        }

    last_date = date.fromisoformat(streak["last_activity_date"])
    days_since = (date.today() - last_date).days

    if days_since == 0:
        # Same day, no change
        pass
    elif days_since == 1:
        # Consecutive day
        streak["current_streak"] += 1
        streak["total_active_days"] += 1
        if streak["current_streak"] > streak["longest_streak"]:
            streak["longest_streak"] = streak["current_streak"]
        streak["last_activity_date"] = today

        # Check milestones
        milestones = {
            3: ("3-Day Streak", "Amazing! You've maintained a 3-day learning streak!"),
            7: ("Week Warrior", "Incredible! A full week of consistent learning!"),
            14: ("Two Week Champion", "Outstanding! Two weeks of dedication!"),
            30: ("Month Master", "Legendary! 30 days of continuous learning!")
        }

        if streak["current_streak"] in milestones:
            return {
                "milestone": milestones[streak["current_streak"]][0],
                "message": milestones[streak["current_streak"]][1]
            }
    else:
        # Streak broken
        streak["current_streak"] = 1
        streak["total_active_days"] += 1
        streak["last_activity_date"] = today

    streak["last_activity_date"] = today
    return None


def check_achievements(progress):
    """Check for new achievements"""
    achievements = progress.get("achievements", [])

    # Chapter completion achievements
    completed_count = sum(1 for c in progress["chapters"].values() if c.get("is_completed", False))

    achievement_list = [
        ("first_chapter", "First Chapter Complete", completed_count >= 1 and "first_chapter" not in achievements),
        ("halfway", "Halfway There", completed_count >= 2 and "halfway" not in achievements),
        ("chapter_master", "Chapter Master", completed_count >= 4 and "chapter_master" not in achievements),
    ]

    new_achievements = []
    for ach_id, ach_name, condition in achievement_list:
        if condition:
            achievements.append(ach_id)
            new_achievements.append(ach_name)

    progress["achievements"] = achievements
    return new_achievements


# Endpoints
@app.get("/")
async def root():
    """API health check"""
    progress = load_progress()
    return {
        "status": "operational",
        "service": "Progress Tracking API",
        "user_id": progress["user_id"],
        "chapters_tracked": len(progress["chapters"])
    }


@app.get("/progress/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    """Get comprehensive progress dashboard"""
    progress = load_progress()

    # Calculate overall completion
    chapters = progress["chapters"]
    completed = sum(1 for c in chapters.values() if c.get("is_completed", False))
    in_progress = sum(1 for c in chapters.values() if not c.get("is_completed", False) and c.get("completion_percentage", 0) > 0)
    not_started = COURSE_STRUCTURE["total_chapters"] - len(chapters)

    overall_percentage = int((completed / COURSE_STRUCTURE["total_chapters"]) * 100) if COURSE_STRUCTURE["total_chapters"] > 0 else 0

    # Total time
    total_time = sum(c.get("time_spent_seconds", 0) for c in chapters.values())

    # Streak info
    streak = progress["streak"]
    last_active = streak.get("last_activity_date")
    is_active = False
    if last_active:
        days_since = (date.today() - date.fromisoformat(last_active)).days
        is_active = days_since <= 1

    return DashboardResponse(
        overall_completion_percentage=overall_percentage,
        completed_chapters=completed,
        in_progress_chapters=in_progress,
        not_started_chapters=not_started,
        total_time_spent_seconds=total_time,
        streak={
            "current_streak": streak["current_streak"],
            "longest_streak": streak["longest_streak"],
            "total_active_days": streak["total_active_days"],
            "last_activity_date": last_active,
            "is_active": is_active
        },
        chapters=[
            {
                "id": chapter_id,
                "title": next(c["title"] for c in COURSE_STRUCTURE["chapters"] if c["id"] == chapter_id),
                **chapter_data
            }
            for chapter_id, chapter_data in chapters.items()
        ],
        achievements=progress.get("achievements", [])
    )


@app.get("/progress/chapters/{chapter_id}")
async def get_chapter_progress(chapter_id: str):
    """Get progress for a specific chapter"""
    progress = load_progress()

    if chapter_id not in progress["chapters"]:
        # Chapter not started yet
        return {
            "chapter_id": chapter_id,
            "status": "not_started",
            "completion_percentage": 0,
            "is_completed": False
        }

    return progress["chapters"][chapter_id]


@app.post("/progress/chapters/{chapter_id}/update")
async def update_chapter_progress(chapter_id: str, update: ProgressUpdate):
    """Update progress for a chapter"""
    progress = load_progress()

    # Validate chapter exists
    if not any(c["id"] == chapter_id for c in COURSE_STRUCTURE["chapters"]):
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")

    # Initialize chapter progress if not exists
    if chapter_id not in progress["chapters"]:
        progress["chapters"][chapter_id] = {
            "chapter_id": chapter_id,
            "completion_percentage": 0,
            "is_completed": False,
            "time_spent_seconds": 0,
            "started_at": datetime.now().isoformat()
        }

    # Update progress
    chapter = progress["chapters"][chapter_id]
    chapter["time_spent_seconds"] += update.time_spent_seconds
    chapter["completion_percentage"] = max(chapter["completion_percentage"], update.completion_percentage)
    chapter["last_accessed"] = datetime.now().isoformat()

    if update.mark_completed and not chapter["is_completed"]:
        chapter["is_completed"] = True
        chapter["completed_at"] = datetime.now().isoformat()

    # Update streak
    milestone = update_streak(progress)

    # Check achievements
    new_achievements = check_achievements(progress)

    # Save
    save_progress(progress)

    return {
        "chapter": chapter,
        "milestone_achieved": milestone,
        "new_achievements": new_achievements
    }


@app.get("/progress/streak", response_model=StreakResponse)
async def get_streak():
    """Get current streak information"""
    progress = load_progress()
    streak = progress["streak"]

    last_active = streak.get("last_activity_date")
    is_active = False
    if last_active:
        days_since = (date.today() - date.fromisoformat(last_active)).days
        is_active = days_since <= 1

    return StreakResponse(
        current_streak=streak["current_streak"],
        longest_streak=streak["longest_streak"],
        total_active_days=streak["total_active_days"],
        last_activity_date=last_active or "Never",
        is_active=is_active
    )


@app.post("/progress/activity")
async def record_activity():
    """Record learning activity (updates streak)"""
    progress = load_progress()

    milestone = update_streak(progress)
    save_progress(progress)

    return {
        "recorded": True,
        "streak": progress["streak"],
        "milestone_achieved": milestone
    }


@app.get("/progress/achievements")
async def get_achievements():
    """Get all achievements"""
    progress = load_progress()

    all_achievements = {
        "first_chapter": "First Chapter Complete - Completed your first chapter!",
        "halfway": "Halfway There - Completed 50% of the course",
        "chapter_master": "Chapter Master - Completed all chapters!",
        "streak_3": "3-Day Streak - Maintained a 3-day learning streak",
        "streak_7": "Week Warrior - 7 days of consistent learning",
        "streak_14": "Two Week Champion - 14 days of learning",
        "streak_30": "Month Master - 30 days continuous learning"
    }

    earned = progress.get("achievements", [])

    return {
        "earned": [
            {"id": ach_id, "name": all_achievements.get(ach_id, ach_id)}
            for ach_id in earned
        ],
        "locked": [
            {"id": ach_id, "name": name}
            for ach_id, name in all_achievements.items()
            if ach_id not in earned
        ]
    }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("Progress Tracking API")
    print("="*60)
    print(f"\nStorage: {PROGRESS_FILE}")
    print(f"Total Chapters: {COURSE_STRUCTURE['total_chapters']}")
    print("\nStarting server on http://localhost:8002")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8002)
