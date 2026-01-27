"""
Progress Tracking Demo
Demonstrates progress tracking functionality
"""

import requests
import json
import time
from datetime import date

BASE_URL = "http://localhost:8002"

print("="*60)
print("Progress Tracking Demo")
print("="*60)

# Test 1: Get initial dashboard
print("\n[TEST 1] Getting initial dashboard...")
try:
    response = requests.get(f"{BASE_URL}/progress/dashboard")
    dashboard = response.json()

    print(f"Overall Completion: {dashboard['overall_completion_percentage']}%")
    print(f"Completed: {dashboard['completed_chapters']}/{dashboard['completed_chapters'] + dashboard['in_progress_chapters'] + dashboard['not_started_chapters']}")
    print(f"Streak: {dashboard['streak']['current_streak']} days")
    print(f"Active: {dashboard['streak']['is_active']}")
except Exception as e:
    print(f"Server not running yet: {e}")
    print("\nPlease start the server first:")
    print("  python simple_progress_api.py")
    exit(1)

# Test 2: Record activity (should start streak)
print("\n[TEST 2] Recording learning activity...")
response = requests.post(f"{BASE_URL}/progress/activity")
result = response.json()

print(f"Activity recorded: {result['recorded']}")
print(f"Streak: {result['streak']['current_streak']} day(s)")
if result.get('milestone_achieved'):
    milestone = result['milestone_achieved']
    print(f"Milestone: {milestone.get('name', 'First Activity')}")
    print(f"Message: {milestone.get('message', '')}")

# Test 3: Update chapter progress
print("\n[TEST 3] Updating Chapter 1 progress...")

# Start Chapter 1 (50% complete, 5 minutes spent)
update_data = {
    "chapter_id": "chapter-1",
    "time_spent_seconds": 300,
    "completion_percentage": 50,
    "mark_completed": False
}

response = requests.post(f"{BASE_URL}/progress/chapters/chapter-1/update", json=update_data)
result = response.json()

print(f"Chapter: {result['chapter']['chapter_id']}")
print(f"Completion: {result['chapter']['completion_percentage']}%")
print(f"Time spent: {result['chapter']['time_spent_seconds']} seconds ({result['chapter']['time_spent_seconds']//60} minutes)")
if result.get('new_achievements'):
    print(f"New achievements: {result['new_achievements']}")

# Test 4: Complete Chapter 1
print("\n[TEST 4] Completing Chapter 1...")

update_data = {
    "chapter_id": "chapter-1",
    "time_spent_seconds": 300,  # Additional 5 minutes
    "completion_percentage": 100,
    "mark_completed": True
}

response = requests.post(f"{BASE_URL}/progress/chapters/chapter-1/update", json=update_data)
result = response.json()

print(f"Chapter completed: {result['chapter']['is_completed']}")
print(f"Total time: {result['chapter']['time_spent_seconds']//60} minutes")
if result.get('new_achievements'):
    print(f"Achievements earned: {', '.join(result['new_achievements'])}")

# Test 5: Start Chapter 2
print("\n[TEST 5] Starting Chapter 2...")

update_data = {
    "chapter_id": "chapter-2",
    "time_spent_seconds": 180,
    "completion_percentage": 25,
    "mark_completed": False
}

response = requests.post(f"{BASE_URL}/progress/chapters/chapter-2/update", json=update_data)
result = response.json()

print(f"Chapter 2 started: {result['chapter']['completion_percentage']}% complete")

# Test 6: Get updated dashboard
print("\n[TEST 6] Getting updated dashboard...")
response = requests.get(f"{BASE_URL}/progress/dashboard")
dashboard = response.json()

print(f"\n{'='*60}")
print(f"PROGRESS DASHBOARD")
print(f"{'='*60}")
print(f"\nOverall Completion: {dashboard['overall_completion_percentage']}%")
print(f"Completed Chapters: {dashboard['completed_chapters']}")
print(f"In-Progress Chapters: {dashboard['in_progress_chapters']}")
print(f"Not Started: {dashboard['not_started_chapters']}")
print(f"Total Time Spent: {dashboard['total_time_spent_seconds']//60} minutes")

print(f"\nStreak Information:")
print(f"  Current: {dashboard['streak']['current_streak']} days")
print(f"  Longest: {dashboard['streak']['longest_streak']} days")
print(f"  Total Active Days: {dashboard['streak']['total_active_days']}")
print(f"  Active: {dashboard['streak']['is_active']}")

print(f"\nChapter Progress:")
for chapter in dashboard['chapters']:
    status = "COMPLETED" if chapter['is_completed'] else "IN PROGRESS"
    print(f"  {chapter['id']}: {chapter['completion_percentage']}% ({status})")

print(f"\nAchievements: {len(dashboard['achievements'])} earned")
for ach in dashboard['achievements']:
    print(f"  - {ach}")

# Test 7: Get achievements
print("\n[TEST 7] Getting all achievements...")
response = requests.get(f"{BASE_URL}/progress/achievements")
achievements = response.json()

print(f"\nEarned ({len(achievements['earned'])}):")
for ach in achievements['earned']:
    print(f"  [{ach['id']}] {ach['name']}")

print(f"\nLocked ({len(achievements['locked'])}):")
for ach in achievements['locked'][:5]:  # Show first 5
    print(f"  [{ach['id']}] {ach['name']}")

# Test 8: Get streak info
print("\n[TEST 8] Getting streak information...")
response = requests.get(f"{BASE_URL}/progress/streak")
streak = response.json()

print(f"Current Streak: {streak['current_streak']} days")
print(f"Longest Streak: {streak['longest_streak']} days")
print(f"Total Active Days: {streak['total_active_days']}")
print(f"Last Activity: {streak['last_activity_date']}")
print(f"Streak Active: {streak['is_active']}")

print("\n" + "="*60)
print("Progress Tracking Demo Complete!")
print("="*60)

print("""
Features Demonstrated:
- Chapter progress tracking (start, update, complete)
- Time spent tracking
- Streak tracking (daily activity)
- Achievement system
- Progress dashboard
- Overall completion calculation

Progress is saved to: backend/progress_data.json

You can restart the server and progress will persist!
""")
