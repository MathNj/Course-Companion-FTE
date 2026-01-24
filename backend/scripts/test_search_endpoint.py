"""
Integration Test Script for Search Endpoint (Grounded Q&A)

Tests the /chapters/search endpoint with real authentication and content.
"""

import asyncio
import httpx
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8001/api/v1"


async def register_test_user() -> Dict[str, Any]:
    """Register a test user and return credentials."""
    async with httpx.AsyncClient() as client:
        # Register
        response = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "search_test@example.com",
                "password": "Test123!",
                "full_name": "Search Tester"
            }
        )

        if response.status_code == 201:
            print("[OK] User registered successfully")
        elif response.status_code in (400, 409):
            print("[OK] User already exists, will login...")
        else:
            print(f"[FAIL] Registration failed: {response.status_code}")
            print(response.text)
            return None

        # Login to get token
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "search_test@example.com",
                "password": "Test123!"
            }
        )

        if response.status_code == 200:
            print("[OK] Login successful")
            return response.json()
        else:
            print(f"[FAIL] Login failed: {response.status_code}")
            return None


async def test_search_endpoint(token: str):
    """Test various search queries."""
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        print("\n" + "="*60)
        print("Testing Search Endpoint (Grounded Q&A)")
        print("="*60)

        # Test 1: Search for "generative AI"
        print("\n[Test 1] Search: 'generative AI'")
        response = await client.get(
            f"{BASE_URL}/chapters/search",
            params={"q": "generative AI", "limit": 5},
            headers=headers
        )

        if response.status_code == 200:
            results = response.json()
            print(f"[OK] Status: 200 OK")
            print(f"[OK] Results found: {len(results)}")

            if results:
                print(f"\nTop result:")
                top = results[0]
                print(f"  Chapter: {top['chapter_title']}")
                print(f"  Section: {top['section_title']}")
                print(f"  Relevance: {top['relevance_score']}")
                print(f"  Matches: {top['match_count']}")
                print(f"  Snippet: {top['snippet'][:150]}...")
        else:
            print(f"[FAIL] Failed: {response.status_code}")
            print(response.text)

        # Test 2: Search for "LLM"
        print("\n[Test 2] Search: 'LLM language models'")
        response = await client.get(
            f"{BASE_URL}/chapters/search",
            params={"q": "LLM language models", "limit": 3},
            headers=headers
        )

        if response.status_code == 200:
            results = response.json()
            print(f"[OK] Status: 200 OK")
            print(f"[OK] Results found: {len(results)}")

            for i, result in enumerate(results[:3], 1):
                print(f"\n  Result {i}:")
                print(f"    Chapter: {result['chapter_id']}")
                print(f"    Section: {result['section_id']}")
                print(f"    Relevance: {result['relevance_score']}")
        else:
            print(f"[FAIL] Failed: {response.status_code}")

        # Test 3: Search specific chapter
        print("\n[Test 3] Search: 'AI' in chapter-1 only")
        response = await client.get(
            f"{BASE_URL}/chapters/search",
            params={"q": "AI", "chapter_id": "chapter-1", "limit": 3},
            headers=headers
        )

        if response.status_code == 200:
            results = response.json()
            print(f"[OK] Status: 200 OK")
            print(f"[OK] Results found: {len(results)}")

            # Verify all results are from chapter-1
            all_from_chapter_1 = all(r["chapter_id"] == "chapter-1" for r in results)
            if all_from_chapter_1:
                print(f"[OK] All results from chapter-1")
            else:
                print(f"[FAIL] Results from multiple chapters!")
        else:
            print(f"[FAIL] Failed: {response.status_code}")

        # Test 4: Search with no results
        print("\n[Test 4] Search: 'xyznonexistent' (expect no results)")
        response = await client.get(
            f"{BASE_URL}/chapters/search",
            params={"q": "xyznonexistent", "limit": 10},
            headers=headers
        )

        if response.status_code == 200:
            results = response.json()
            print(f"[OK] Status: 200 OK")
            print(f"[OK] Results found: {len(results)}")
            if len(results) == 0:
                print(f"[OK] Correctly returns empty results for nonsense query")
        else:
            print(f"[FAIL] Failed: {response.status_code}")

        # Test 5: Search stopwords only
        print("\n[Test 5] Search: 'what is the' (stopwords only)")
        response = await client.get(
            f"{BASE_URL}/chapters/search",
            params={"q": "what is the", "limit": 10},
            headers=headers
        )

        if response.status_code == 200:
            results = response.json()
            print(f"[OK] Status: 200 OK")
            print(f"[OK] Results found: {len(results)}")
            if len(results) == 0:
                print(f"[OK] Correctly returns empty for stopwords-only query")
        else:
            print(f"[FAIL] Failed: {response.status_code}")

        # Test 6: Verify access control (free user can only search chapters 1-3)
        print("\n[Test 6] Access Control: Free user searching chapter-4")
        response = await client.get(
            f"{BASE_URL}/chapters/search",
            params={"q": "AI", "chapter_id": "chapter-4", "limit": 10},
            headers=headers
        )

        if response.status_code == 200:
            results = response.json()
            print(f"[OK] Status: 200 OK")
            print(f"[OK] Results found: {len(results)}")
            if len(results) == 0:
                print(f"[OK] Correctly blocks access to premium chapter")
        elif response.status_code == 403:
            print(f"[OK] Returns 403 Forbidden for premium chapter")
        else:
            print(f"[?] Unexpected status: {response.status_code}")

        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)


async def main():
    """Run all tests."""
    print("Grounded Q&A Feature - Integration Test\n")

    # Register/login user
    auth_data = await register_test_user()
    if not auth_data:
        print("Failed to authenticate. Exiting.")
        return

    token = auth_data["access_token"]

    # Run search tests
    await test_search_endpoint(token)


if __name__ == "__main__":
    asyncio.run(main())
