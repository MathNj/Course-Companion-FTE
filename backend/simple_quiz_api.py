"""
Simple Quiz API for Testing
Standalone FastAPI app to test quiz functionality without full backend
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Course Companion FTE - Quiz API",
    description="Simple quiz API for Generative AI Fundamentals",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Quiz storage path
CONTENT_DIR = Path(__file__).parent / "content" / "quizzes"

# Response Models
class QuizListResponse(BaseModel):
    total: int
    quizzes: List[Dict]


class QuizResponse(BaseModel):
    quiz_id: str
    title: str
    description: str
    total_questions: int
    passing_score: int
    questions: List[Dict]


class QuizSubmission(BaseModel):
    quiz_id: str
    answers: Dict[str, str]  # question_id -> answer


class QuizResult(BaseModel):
    quiz_id: str
    score: int
    total_points: int
    percentage: float
    passed: bool
    results: List[Dict]
    correct_answers: Dict[str, str]


# Helper functions
def load_quiz_file(quiz_id: str) -> Dict[str, Any]:
    """Load quiz JSON file"""
    quiz_file = CONTENT_DIR / f"{quiz_id}.json"

    if not quiz_file.exists():
        return None

    with open(quiz_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def remove_answers(quiz: Dict[str, Any]) -> Dict[str, Any]:
    """Remove answer keys from quiz for student view"""
    quiz_copy = quiz.copy()

    for question in quiz_copy.get("questions", []):
        question.pop("answer_key", None)
        question.pop("explanation_correct", None)
        question.pop("explanation_incorrect", None)
        question.pop("explanation", None)

    return quiz_copy


# Endpoints
@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "operational",
        "service": "Course Companion FTE - Quiz API",
        "course": "Generative AI Fundamentals",
        "quiz_files_available": len(list(CONTENT_DIR.glob("*.json")))
    }


@app.get("/quizzes", response_model=QuizListResponse)
async def list_quizzes():
    """List all available quizzes"""
    quizzes = []

    for quiz_file in sorted(CONTENT_DIR.glob("*.json")):
        try:
            with open(quiz_file, 'r', encoding='utf-8') as f:
                quiz_data = json.load(f)

            quizzes.append({
                "id": quiz_data.get("id", quiz_file.stem),
                "chapter_id": quiz_data.get("chapter_id"),
                "title": quiz_data.get("title"),
                "description": quiz_data.get("description"),
                "total_questions": quiz_data.get("total_questions"),
                "time_limit_minutes": quiz_data.get("time_limit_minutes"),
                "passing_score": quiz_data.get("passing_score")
            })
        except Exception as e:
            print(f"Error loading {quiz_file}: {e}")

    return QuizListResponse(total=len(quizzes), quizzes=quizzes)


@app.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: str, include_answers: bool = False):
    """
    Get quiz content

    By default, excludes answer keys. Set ?include_answers=true to see answers (for testing).
    """
    quiz_data = load_quiz_file(quiz_id)

    if not quiz_data:
        raise HTTPException(status_code=404, detail=f"Quiz '{quiz_id}' not found")

    # Remove answers unless explicitly requested
    if not include_answers:
        quiz_data = remove_answers(quiz_data)

    return QuizResponse(
        quiz_id=quiz_data.get("id"),
        title=quiz_data.get("title"),
        description=quiz_data.get("description"),
        total_questions=quiz_data.get("total_questions"),
        passing_score=quiz_data.get("passing_score"),
        questions=quiz_data.get("questions", [])
    )


@app.post("/quizzes/{quiz_id}/submit", response_model=QuizResult)
async def submit_quiz(quiz_id: str, submission: QuizSubmission):
    """
    Submit quiz answers for deterministic grading

    Grading is rule-based (Phase 1 compliant):
    - Multiple choice: exact match
    - True/False: exact match
    - Fill-in-blank: case-insensitive match with variants
    """
    # Load full quiz with answers
    quiz_data = load_quiz_file(quiz_id)

    if not quiz_data:
        raise HTTPException(status_code=404, detail=f"Quiz '{quiz_id}' not found")

    # Grade each question
    results = []
    total_score = 0
    total_points = 0
    correct_answers = {}

    for question in quiz_data.get("questions", []):
        question_id = question.get("id")
        user_answer = submission.answers.get(question_id)
        correct_answer = question.get("answer_key")

        # Store correct answer for feedback
        correct_answers[question_id] = correct_answer

        # Determine if correct (deterministic grading)
        is_correct = False
        points = question.get("points", 1)
        total_points += points

        question_type = question.get("type")

        if question_type == "multiple_choice":
            # Exact match for multiple choice
            is_correct = user_answer == correct_answer

        elif question_type == "true_false":
            # Handle true/false
            is_correct = str(user_answer).lower() == str(correct_answer).lower()

        elif question_type == "fill_in_blank":
            # Case-insensitive match with variants
            user_clean = str(user_answer).strip().lower()
            correct_clean = str(correct_answer).strip().lower()

            # Check main answer or variants
            answer_variants = question.get("answer_variants", [correct_answer])
            variants_clean = [str(v).strip().lower() for v in answer_variants]

            is_correct = user_clean in variants_clean

        # Calculate score
        if is_correct:
            total_score += points

        # Get explanation
        explanation = question.get(
            "explanation_correct" if is_correct else "explanation_incorrect",
            question.get("explanation", "")
        )

        results.append({
            "question_id": question_id,
            "question": question.get("question"),
            "type": question_type,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "points_earned": points if is_correct else 0,
            "points_possible": points,
            "explanation": explanation
        })

    # Calculate percentage
    percentage = (total_score / total_points * 100) if total_points > 0 else 0
    passing_score = quiz_data.get("passing_score", 70)
    passed = percentage >= passing_score

    return QuizResult(
        quiz_id=quiz_id,
        score=total_score,
        total_points=total_points,
        percentage=round(percentage, 1),
        passed=passed,
        results=results,
        correct_answers=correct_answers
    )


@app.get("/quizzes/{quiz_id}/preview")
async def preview_quiz(quiz_id: str):
    """Preview quiz with answers (for instructors/testing)"""
    return await get_quiz(quiz_id, include_answers=True)


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("Course Companion FTE - Quiz API")
    print("="*60)
    print(f"\nContent Directory: {CONTENT_DIR}")
    print(f"Quiz Files Available: {len(list(CONTENT_DIR.glob('*.json')))}")

    # List available quizzes
    print("\nAvailable Quizzes:")
    for quiz_file in sorted(CONTENT_DIR.glob("*.json")):
        print(f"  - {quiz_file.stem}")

    print("\nStarting server on http://localhost:8001")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8001)
