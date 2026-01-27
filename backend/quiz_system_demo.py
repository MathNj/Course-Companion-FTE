"""
Quiz System Demo - Direct Test Without Server
Demonstrates quiz functionality by loading files directly
"""

import json
from pathlib import Path

CONTENT_DIR = Path(__file__).parent / "content" / "quizzes"

print("="*60)
print("Quiz System Demo - Generative AI Fundamentals")
print("="*60)

# Load all available quizzes
quiz_files = sorted(CONTENT_DIR.glob("*.json"))

print(f"\nFound {len(quiz_files)} quiz files\n")

# List all quizzes
print("Available Quizzes:")
print("-"*60)
for quiz_file in quiz_files:
    with open(quiz_file, 'r', encoding='utf-8') as f:
        quiz = json.load(f)
    print(f"\nID: {quiz.get('id')}")
    print(f"Title: {quiz.get('title')}")
    print(f"Chapter: {quiz.get('chapter_id')}")
    print(f"Questions: {quiz.get('total_questions')}")
    print(f"Time Limit: {quiz.get('time_limit_minutes')} minutes")
    print(f"Passing Score: {quiz.get('passing_score')}%")

# Load Chapter 1 quiz for detailed demo
print("\n" + "="*60)
print("DETAILED QUIZ DEMO: Chapter 1")
print("="*60)

with open(CONTENT_DIR / "chapter-1-quiz.json", 'r', encoding='utf-8') as f:
    chapter1_quiz = json.load(f)

print(f"\nQuiz: {chapter1_quiz['title']}")
print(f"Description: {chapter1_quiz['description']}")

# Show first 3 questions (student view - no answers)
print("\n" + "-"*60)
print("STUDENT VIEW (First 3 Questions)")
print("-"*60)

for i, q in enumerate(chapter1_quiz['questions'][:3], 1):
    print(f"\nQuestion {i}: {q['question']}")
    print(f"Type: {q['type']} | Points: {q['points']}")

    if q['type'] == 'multiple_choice':
        print("Options:")
        for opt in q.get('options', []):
            print(f"  {opt}")
    elif q['type'] == 'true_false':
        print("Options:")
        for opt in q.get('options', []):
            print(f"  {opt}")

# Demonstrate grading
print("\n" + "-"*60)
print("GRADING DEMONSTRATION")
print("-"*60)

# Simulate student answers
sample_answers = {
    "q1": "option_a",  # Correct: "Generative AI creates new content..."
    "q2": "option_b",  # Let's see...
    "q3": "True"       # Let's see...
}

print("\nStudent Answers:")
for q_id, answer in sample_answers.items():
    # Find the question
    question = next((q for q in chapter1_quiz['questions'] if q['id'] == q_id), None)
    if question:
        print(f"\n{q_id}: {question['question'][:60]}...")
        print(f"  Student Answer: {answer}")
        print(f"  Correct Answer: {question['answer_key']}")

        # Grade (deterministic)
        is_correct = (answer == question['answer_key'])
        status = "CORRECT" if is_correct else "INCORRECT"
        print(f"  Result: {status}")

# Show instructor view (with answers)
print("\n" + "-"*60)
print("INSTRUCTOR VIEW (First Question with Answer Key)")
print("-"*60)

q1 = chapter1_quiz['questions'][0]
print(f"\nQuestion: {q1['question']}")
print(f"\nCorrect Answer: {q1['answer_key']}")
print(f"\nExplanation (Correct):")
print(f"  {q1['explanation_correct'][:200]}...")
print(f"\nExplanation (Incorrect):")
print(f"  {q1['explanation_incorrect'][:200]}...")

# Summary
print("\n" + "="*60)
print("QUIZ SYSTEM FEATURES")
print("="*60)
print("""
✅ Phase 1 Compliant Features:
  - Deterministic, rule-based grading
  - No LLM calls in backend
  - Exact match for multiple choice
  - Case-insensitive matching for true/false
  - Support for answer variants in fill-in-blank

✅ Question Types Supported:
  - Multiple Choice
  - True/False
  - Fill-in-the-blank

✅ Quiz Features:
  - Freely mix question types
  - Point values per question
  - Configurable passing score
  - Time limits
  - Detailed explanations

✅ Student Experience:
  - Clean quiz interface (no answers shown)
  - Immediate feedback after submission
  - Detailed explanations for each answer
  - Score tracking

✅ Instructor Tools:
  - Preview with answer keys
  - Detailed question metadata
  - Explanations for correct/incorrect answers
""")

print("="*60)
print("Quiz System Demo Complete!")
print("="*60)
