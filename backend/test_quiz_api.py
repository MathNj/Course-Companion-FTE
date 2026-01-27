"""
Test Quiz API
Demonstrates quiz functionality with deterministic grading
"""

import requests
import json

BASE_URL = "http://localhost:8001"

print("="*60)
print("Quiz API Test - Generative AI Fundamentals")
print("="*60)

# Test 1: List all quizzes
print("\n[TEST 1] Listing all quizzes...")
response = requests.get(f"{BASE_URL}/quizzes")
data = response.json()

print(f"Status: {response.status_code}")
print(f"Total quizzes: {data['total']}")
print("\nAvailable quizzes:")
for quiz in data['quizzes']:
    print(f"  - {quiz['id']}: {quiz['title']}")
    print(f"    Questions: {quiz['total_questions']}")
    print(f"    Passing Score: {quiz['passing_score']}%")
    print()

# Test 2: Get Chapter 1 Quiz (without answers)
print("\n[TEST 2] Getting Chapter 1 Quiz (student view)...")
response = requests.get(f"{BASE_URL}/quizzes/chapter-1-quiz")
quiz = response.json()

print(f"Quiz: {quiz['title']}")
print(f"Description: {quiz['description']}")
print(f"Total Questions: {quiz['total_questions']}")
print(f"Passing Score: {quiz['passing_score']}%")

print("\nFirst 3 questions (answers hidden):")
for i, q in enumerate(quiz['questions'][:3], 1):
    print(f"\nQ{i}: {q['question']}")
    print(f"Type: {q['type']}")
    if q['type'] == 'multiple_choice':
        for opt in q.get('options', []):
            print(f"  - {opt}")
    elif q['type'] == 'true_false':
        for opt in q.get('options', []):
            print(f"  - {opt}")

# Test 3: Submit a quiz attempt
print("\n\n[TEST 3] Submitting quiz answers...")

# Create sample answers (mix of correct and incorrect)
sample_answers = {
    "q1": "option_a",  # Correct
    "q2": "option_b",  # Correct
    "q3": "True",      # Incorrect (should be False)
    "q4": "option_a",  # Placeholder
    "q5": "option_b",  # Placeholder
}

submission = {
    "quiz_id": "chapter-1-quiz",
    "answers": sample_answers
}

print(f"Submitting answers for {len(sample_answers)} questions...")

response = requests.post(
    f"{BASE_URL}/quizzes/chapter-1-quiz/submit",
    json=submission
)

result = response.json()

print(f"\n{'='*60}")
print(f"QUIZ RESULTS")
print(f"{'='*60}")
print(f"Score: {result['score']}/{result['total_points']}")
print(f"Percentage: {result['percentage']}%")
print(f"Passed: {result['passed']}")

print(f"\n{'='*60}")
print("DETAILED RESULTS")
print(f"{'='*60}")

for r in result['results']:
    status = "✓ CORRECT" if r['is_correct'] else "✗ INCORRECT"
    print(f"\n{status}")
    print(f"Question: {r['question'][:80]}...")
    print(f"Your Answer: {r['user_answer']}")
    print(f"Correct Answer: {r['correct_answer']}")
    print(f"Points: {r['points_earned']}/{r['points_possible']}")
    print(f"Explanation: {r['explanation'][:100]}...")

# Test 4: Preview with answers (instructor view)
print(f"\n\n[TEST 4] Previewing quiz with answers (instructor view)...")
response = requests.get(f"{BASE_URL}/quizzes/chapter-1-quiz?include_answers=true")
quiz_with_answers = response.json()

print(f"\nFirst question with answer key:")
q1 = quiz_with_answers['questions'][0]
print(f"Question: {q1['question']}")
print(f"Correct Answer: {q1.get('answer_key', 'N/A')}")
print(f"Explanation: {q1.get('explanation_correct', 'N/A')[:100]}...")

print("\n" + "="*60)
print("Quiz API Test Complete!")
print("="*60)
