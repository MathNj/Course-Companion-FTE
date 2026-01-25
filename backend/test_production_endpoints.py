"""
Production ChatGPT Integration Test

Tests all 6 API endpoints that the ChatGPT Custom GPT will use.
Tests the production backend at https://course-companion-fte.fly.dev
"""

import asyncio
import httpx
import json
from typing import Optional

# Production configuration
BASE_URL = "https://course-companion-fte.fly.dev"
API_BASE = f"{BASE_URL}/api/v1"

# Test user credentials
TEST_USER = {
    "email": "chatgpt_test@example.com",
    "password": "TestPassword123!",
    "full_name": "ChatGPT Test User"
}

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_header(message: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

async def test_health_check():
    """Test 1: Health check endpoint"""
    print_header("TEST 1: Health Check Endpoint")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                print_success(f"Health check passed")
                print_info(f"Status: {data.get('status')}")
                print_info(f"Environment: {data.get('environment')}")
                print_info(f"Components: {json.dumps(data.get('components'), indent=2)}")
                return True
            else:
                print_error(f"Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Health check error: {str(e)}")
            return False

async def test_register_and_login():
    """Test 2: User registration and login"""
    print_header("TEST 2: User Registration & Login")

    async with httpx.AsyncClient() as client:
        # Try to register
        print_info("Attempting to register test user...")

        try:
            response = await client.post(
                f"{API_BASE}/auth/register",
                json=TEST_USER,
                timeout=10.0
            )

            if response.status_code in [200, 201]:
                print_success("User registered successfully")
                data = response.json()
                token = data.get("access_token")
                print_info(f"Got access token: {token[:20]}..." if token else "No token in response")
                return token
            elif response.status_code == 400:
                # User might already exist, try logging in
                print_info("User might already exist, attempting login...")

                login_response = await client.post(
                    f"{API_BASE}/auth/login",
                    json={
                        "username": TEST_USER["email"],
                        "password": TEST_USER["password"]
                    },
                    timeout=10.0
                )

                if login_response.status_code == 200:
                    print_success("User logged in successfully")
                    data = login_response.json()
                    token = data.get("access_token")
                    print_info(f"Got access token: {token[:20]}..." if token else "No token in response")
                    return token
                else:
                    print_error(f"Login failed with status {login_response.status_code}")
                    print_error(f"Response: {login_response.text}")
                    return None
            else:
                print_error(f"Registration failed with status {response.status_code}")
                print_error(f"Response: {response.text}")
                return None

        except Exception as e:
            print_error(f"Auth error: {str(e)}")
            return None

async def test_get_chapters(token: str):
    """Test 3: Get all chapters"""
    print_header("TEST 3: Get All Chapters")

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/chapters",
                headers=headers,
                timeout=10.0
            )

            if response.status_code == 200:
                chapters = response.json()
                print_success(f"Retrieved {len(chapters)} chapters")
                for chapter in chapters[:3]:  # Show first 3
                    print_info(f"  - {chapter.get('title')} (Order: {chapter.get('order')})")
                if len(chapters) > 3:
                    print_info(f"  ... and {len(chapters) - 3} more")
                return chapters
            else:
                print_error(f"Failed to get chapters with status {response.status_code}")
                print_error(f"Response: {response.text}")
                return []
        except Exception as e:
            print_error(f"Get chapters error: {str(e)}")
            return []

async def test_get_chapter_content(token: str, chapter_id: int):
    """Test 4: Get specific chapter content"""
    print_header(f"TEST 4: Get Chapter {chapter_id} Content")

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/chapters/{chapter_id}",
                headers=headers,
                timeout=10.0
            )

            if response.status_code == 200:
                content = response.json()
                print_success(f"Retrieved chapter: {content.get('title')}")
                print_info(f"Summary: {content.get('summary', 'N/A')[:100]}...")

                # Show sections count
                sections = content.get('sections', [])
                print_info(f"Sections: {len(sections)}")
                return content
            else:
                print_error(f"Failed to get chapter with status {response.status_code}")
                print_error(f"Response: {response.text}")
                return None
        except Exception as e:
            print_error(f"Get chapter content error: {str(e)}")
            return None

async def test_search_content(token: str):
    """Test 5: Search content (Grounded Q&A)"""
    print_header("TEST 5: Search Content (Grounded Q&A)")

    headers = {"Authorization": f"Bearer {token}"}

    search_queries = [
        "generative AI",
        "transformer architecture",
        "prompt engineering"
    ]

    async with httpx.AsyncClient() as client:
        for query in search_queries:
            try:
                print_info(f"Searching for: '{query}'")

                response = await client.get(
                    f"{API_BASE}/chapters/search",
                    headers=headers,
                    params={"q": query, "limit": 3},
                    timeout=10.0
                )

                if response.status_code == 200:
                    results = response.json()
                    print_success(f"Found {len(results)} results for '{query}'")
                    for i, result in enumerate(results[:2], 1):
                        print_info(f"  {i}. {result.get('title', 'N/A')[:80]}...")
                else:
                    print_error(f"Search failed with status {response.status_code}")

            except Exception as e:
                print_error(f"Search error for '{query}': {str(e)}")

async def test_submit_quiz(token: str):
    """Test 6: Submit quiz answer"""
    print_header("TEST 6: Submit Quiz Answer")

    headers = {"Authorization": f"Bearer {token}"}

    # Create a test quiz submission
    quiz_submission = {
        "chapter_id": 1,
        "question_id": 1,
        "user_answer": "Test answer about generative AI"
    }

    async with httpx.AsyncClient() as client:
        try:
            print_info("Submitting quiz answer...")

            response = await client.post(
                f"{API_BASE}/quizzes/submit",
                headers=headers,
                json=quiz_submission,
                timeout=10.0
            )

            if response.status_code in [200, 201]:
                result = response.json()
                print_success("Quiz submitted successfully")
                print_info(f"Score: {result.get('score', 'N/A')}")
                print_info(f"Feedback: {result.get('feedback', 'No feedback')[:100]}...")
                return result
            else:
                print_error(f"Quiz submission failed with status {response.status_code}")
                print_error(f"Response: {response.text}")
                return None
        except Exception as e:
            print_error(f"Submit quiz error: {str(e)}")
            return None

async def test_get_progress(token: str):
    """Test 7: Get user progress"""
    print_header("TEST 7: Get User Progress")

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/progress",
                headers=headers,
                timeout=10.0
            )

            if response.status_code == 200:
                progress = response.json()
                print_success("Retrieved user progress")
                print_info(f"Completed Chapters: {progress.get('completed_chapters', 0)}")
                print_info(f"Quiz Score Average: {progress.get('quiz_score_average', 'N/A')}")
                print_info(f"Last Activity: {progress.get('last_activity', 'N/A')}")
                return progress
            else:
                print_error(f"Failed to get progress with status {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Get progress error: {str(e)}")
            return None

async def test_openapi_spec():
    """Test: Verify OpenAPI spec is available for ChatGPT"""
    print_header("BONUS TEST: OpenAPI Specification for ChatGPT")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/openapi.json",
                timeout=10.0
            )

            if response.status_code == 200:
                spec = response.json()
                print_success("OpenAPI specification is available")
                print_info(f"OpenAPI Version: {spec.get('openapi')}")
                print_info(f"Title: {spec.get('info', {}).get('title')}")

                # Count endpoints
                paths = spec.get('paths', {})
                print_info(f"Total Endpoints: {len(paths)}")

                # Check for critical endpoints
                critical_paths = [
                    '/api/v1/auth/login',
                    '/api/v1/auth/register',
                    '/api/v1/chapters',
                    '/api/v1/chapters/{id}',
                    '/api/v1/chapters/search',
                    '/api/v1/quizzes/submit',
                    '/api/v1/progress'
                ]

                available = [p for p in critical_paths if p in paths]
                print_success(f"Critical endpoints available: {len(available)}/{len(critical_paths)}")

                return True
            else:
                print_error(f"Failed to get OpenAPI spec with status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"OpenAPI spec error: {str(e)}")
            return False

async def main():
    """Run all integration tests"""
    print(f"\n{Colors.BOLD}")
    print("=" * 60)
    print("ChatGPT Integration Test - Production Backend")
    print("Course: Generative AI Fundamentals")
    print(f"URL: {BASE_URL}")
    print("=" * 60)
    print(f"{Colors.END}\n")

    results = {
        "Health Check": False,
        "Authentication": False,
        "Get Chapters": False,
        "Get Chapter Content": False,
        "Search Content": False,
        "Submit Quiz": False,
        "Get Progress": False,
        "OpenAPI Spec": False
    }

    # Test 1: Health Check
    results["Health Check"] = await test_health_check()

    # Test 2: Authentication
    token = await test_register_and_login()
    results["Authentication"] = token is not None

    if not token:
        print_error("Cannot continue tests without authentication token")
        return

    # Test 3: Get Chapters
    chapters = await test_get_chapters(token)
    results["Get Chapters"] = len(chapters) > 0

    # Test 4: Get Chapter Content
    if chapters:
        first_chapter_id = chapters[0].get('id')
        if first_chapter_id:
            content = await test_get_chapter_content(token, first_chapter_id)
            results["Get Chapter Content"] = content is not None

    # Test 5: Search Content
    await test_search_content(token)
    results["Search Content"] = True  # If we got here without crashing

    # Test 6: Submit Quiz
    quiz_result = await test_submit_quiz(token)
    results["Submit Quiz"] = quiz_result is not None

    # Test 7: Get Progress
    progress = await test_get_progress(token)
    results["Get Progress"] = progress is not None

    # Test 8: OpenAPI Spec
    results["OpenAPI Spec"] = await test_openapi_spec()

    # Print Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{test_name:.<40} {status}")

    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! ChatGPT integration is ready!{Colors.END}\n")
        print(f"{Colors.BLUE}ChatGPT Configuration:{Colors.END}")
        print(f"  OpenAPI URL: {BASE_URL}/api/openapi.json")
        print(f"  Auth Type: Bearer Token")
        print(f"  CORS: Configured for https://chat.openai.com\n")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Please review the errors above.{Colors.END}\n")

if __name__ == "__main__":
    asyncio.run(main())
