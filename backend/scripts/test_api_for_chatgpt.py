#!/usr/bin/env python3
"""
Manual API Testing Script for ChatGPT Integration

Tests all 6 API endpoints that ChatGPT will use to verify they work correctly.
Run this before testing with ChatGPT to ensure backend is ready.
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
# For local testing: http://localhost:8001/api/v1
# For production: https://your-backend-url.com/api/v1
BASE_URL = "http://localhost:8001/api/v1"

# Test user credentials
TEST_EMAIL = "chatgpt_test@example.com"
TEST_PASSWORD = "Test123!"


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_result(test_name: str, success: bool, details: str = ""):
    """Print test result."""
    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")


def authenticate() -> tuple[bool, str, Dict[str, Any]]:
    """Authenticate and get token."""
    print_section("1. Authentication")

    # Try to login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        },
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user = data.get("user", {})
        print_result("Login successful", True, f"User: {user.get('email')}, Tier: {user.get('subscription_tier')}")
        return True, token, user
    elif response.status_code == 401:
        # User doesn't exist, try to register
        print("    User doesn't exist, registering...")

        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": "ChatGPT Test User"
            },
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            print_result("Registration successful", True, f"User: {user.get('email')}")
            return True, token, user
        else:
            print_result("Registration failed", False, f"Status: {response.status_code}")
            return False, None, None
    else:
        print_result("Login failed", False, f"Status: {response.status_code}")
        print(f"    Response: {response.text[:200]}")
        return False, None, None


def test_get_chapters(token: str) -> bool:
    """Test GET /chapters endpoint."""
    print_section("2. Test GET /chapters")

    response = requests.get(
        f"{BASE_URL}/chapters",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if response.status_code == 200:
        chapters = response.json()
        print_result("get_chapters", True, f"Returned {len(chapters)} chapters")

        # Check structure
        if chapters and len(chapters) > 0:
            first_chapter = chapters[0]
            required_fields = ["id", "title", "access_tier", "user_has_access"]
            has_fields = all(field in first_chapter for field in required_fields)
            print_result("Chapter structure valid", has_fields)

            if has_fields:
                print(f"    First chapter: {first_chapter['title']}")
                print(f"    Access tier: {first_chapter['access_tier']}")
                print(f"    User has access: {first_chapter['user_has_access']}")

        return True
    else:
        print_result("get_chapters failed", False, f"Status: {response.status_code}")
        return False


def test_get_chapter(token: str) -> bool:
    """Test GET /chapters/{chapter_id} endpoint."""
    print_section("3. Test GET /chapters/chapter-1")

    response = requests.get(
        f"{BASE_URL}/chapters/chapter-1",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if response.status_code == 200:
        chapter = response.json()
        print_result("get_chapter", True, f"Retrieved: {chapter.get('title')}")

        # Check structure
        required_fields = ["id", "title", "sections", "learning_objectives"]
        has_fields = all(field in chapter for field in required_fields)
        print_result("Chapter content valid", has_fields)

        if has_fields:
            print(f"    Sections: {len(chapter.get('sections', []))}")
            print(f"    Learning objectives: {len(chapter.get('learning_objectives', []))}")

            # Check navigation
            if "navigation" in chapter:
                nav = chapter["navigation"]
                print(f"    Previous: {nav.get('previous_chapter')}")
                print(f"    Next: {nav.get('next_chapter')}")

        return True
    elif response.status_code == 403:
        print_result("get_chapter blocked", False, "403 Forbidden (premium content)")
        return False
    else:
        print_result("get_chapter failed", False, f"Status: {response.status_code}")
        return False


def test_search(token: str) -> bool:
    """Test GET /chapters/search endpoint (Grounded Q&A)."""
    print_section("4. Test GET /chapters/search (Grounded Q&A)")

    response = requests.get(
        f"{BASE_URL}/chapters/search",
        params={"q": "generative AI", "limit": 3},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if response.status_code == 200:
        results = response.json()
        print_result("search_chapters", True, f"Found {len(results)} results")

        if results:
            top_result = results[0]
            print_result("Search result structure", True)
            print(f"    Chapter: {top_result.get('chapter_title')}")
            print(f"    Section: {top_result.get('section_title')}")
            print(f"    Relevance: {top_result.get('relevance_score')}")
            print(f"    Snippet: {top_result.get('snippet', '')[:80]}...")
        else:
            print_result("No results found", False, "Search returned empty array")

        return True
    else:
        print_result("search_chapters failed", False, f"Status: {response.status_code}")
        print(f"    Response: {response.text[:200]}")
        return False


def test_get_quiz(token: str) -> bool:
    """Test GET /quizzes/{quiz_id} endpoint."""
    print_section("5. Test GET /quizzes/chapter-1-quiz")

    response = requests.get(
        f"{BASE_URL}/quizzes/chapter-1-quiz",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if response.status_code == 200:
        quiz = response.json()
        print_result("get_quiz", True, f"Quiz: {quiz.get('title')}")
        print(f"    Total questions: {quiz.get('total_questions')}")
        print(f"    Passing score: {quiz.get('passing_score')}%")

        # Verify no answer keys
        if "questions" in quiz:
            first_q = quiz["questions"][0]
            has_answer_key = "answer_key" in first_q
            print_result("Answer keys hidden", not has_answer_key)

        return True
    else:
        print_result("get_quiz failed", False, f"Status: {response.status_code}")
        return False


def test_submit_quiz(token: str) -> bool:
    """Test POST /quizzes/{quiz_id}/submit endpoint."""
    print_section("6. Test POST /quizzes/chapter-1-quiz/submit")

    # Submit sample answers
    response = requests.post(
        f"{BASE_URL}/quizzes/chapter-1-quiz/submit",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "quiz_id": "chapter-1-quiz",
            "answers": {
                "q1": "option_a",  # This might be wrong
                "q2": "option_a",
                "q3": True
            }
        },
        timeout=10
    )

    if response.status_code == 200:
        result = response.json()
        print_result("submit_quiz", True, f"Score: {result.get('score_percentage')}%")
        print(f"    Passed: {result.get('passed')}")
        print(f"    Correct: {result.get('correct_answers')}/{result.get('total_questions')}")
        return True
    else:
        print_result("submit_quiz failed", False, f"Status: {response.status_code}")
        print(f"    Response: {response.text[:200]}")
        return False


def test_get_progress(token: str) -> bool:
    """Test GET /progress endpoint."""
    print_section("7. Test GET /progress")

    response = requests.get(
        f"{BASE_URL}/progress",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if response.status_code == 200:
        progress = response.json()
        print_result("get_progress", True)

        print(f"    Completion: {progress.get('overall_completion_percentage')}%")
        print(f"    Completed: {progress.get('completed_chapters')}/{progress.get('total_chapters')}")

        # Check streak
        streak = progress.get("streak", {})
        print(f"    Current streak: {streak.get('current_streak')} days")

        # Check milestones
        milestones = progress.get("milestones", {})
        achieved = milestones.get("achieved_milestones", [])
        print(f"    Milestones: {len(achieved)} achieved")

        return True
    else:
        print_result("get_progress failed", False, f"Status: {response.status_code}")
        return False


def test_openapi_spec() -> bool:
    """Test OpenAPI spec is accessible."""
    print_section("8. Test OpenAPI Spec")

    response = requests.get(
        f"{BASE_URL}/../openapi.json",
        timeout=10
    )

    if response.status_code == 200:
        spec = response.json()

        # Check if search endpoint is in spec
        paths = spec.get("paths", {})
        has_search = "/api/v1/chapters/search" in paths

        print_result("OpenAPI spec accessible", True)
        print_result("Search endpoint documented", has_search)

        # Count endpoints
        endpoint_count = len([p for p in paths.keys() if p.startswith("/api/v1/")])
        print(f"    API endpoints documented: {endpoint_count}")

        # Check servers
        servers = spec.get("servers", [])
        if servers:
            print(f"    Server URLs: {[s.get('url') for s in servers]}")

        return True
    else:
        print_result("OpenAPI spec failed", False, f"Status: {response.status_code}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("CHATGPT INTEGRATION - API TESTING")
    print("=" * 60)
    print(f"\nBackend URL: {BASE_URL}")
    print(f"Test user: {TEST_EMAIL}")
    print("\nThis script tests all endpoints that ChatGPT will use.")

    # Authenticate
    success, token, user = authenticate()
    if not success:
        print("\n[FAIL] Authentication failed. Cannot continue.")
        return 1

    # Run all tests
    results = []

    results.append(("get_chapters", test_get_chapters(token)))
    results.append(("get_chapter", test_get_chapter(token)))
    results.append(("search_chapters", test_search(token)))
    results.append(("get_quiz", test_get_quiz(token)))
    results.append(("submit_quiz", test_submit_quiz(token)))
    results.append(("get_progress", test_get_progress(token)))
    results.append(("openapi_spec", test_openapi_spec()))

    # Print summary
    print_section("SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All endpoints working! Ready for ChatGPT integration.")
        print("\nNext steps:")
        print("1. Go to https://chat.openai.com")
        print("2. Create a new Custom GPT")
        print("3. Import OpenAPI spec from:")
        print(f"   {BASE_URL}/../openapi.json")
        print("4. Copy instructions from chatgpt-app/instructions.md")
        print("5. Test with the conversations in TESTING-CHATGPT-INTEGRATION.md")
        return 0
    else:
        print("\n[FAIL] Some endpoints failed. Check backend logs and fix issues.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
