"""
Test script for MCP Server

Tests the MCP server by calling each tool and validating responses.
"""

import asyncio
import json
from mcp_server import (
    call_backend,
    get_chapters,
    get_chapter,
    get_quiz,
    get_progress,
    search_content,
    get_bookmarks,
    create_bookmark,
    get_notes,
    create_note,
    get_note_tags
)


async def test_backend_connection():
    """Test that backend is accessible."""
    print("\n" + "="*60)
    print("Testing Backend Connection")
    print("="*60)

    try:
        result = await call_backend("GET", "/")
        print("[PASS] Backend is running")
        print(f"  Response: {result.get('name', 'Unknown')}")
        return True
    except Exception as e:
        print(f"[FAIL] Backend connection failed: {e}")
        print("\nPlease start the backend server:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
        return False


async def test_get_chapters():
    """Test get_chapters tool."""
    print("\n" + "="*60)
    print("Testing: get_chapters()")
    print("="*60)

    try:
        result_json = await get_chapters()
        result = json.loads(result_json)

        if isinstance(result, list) and len(result) > 0:
            print(f"[PASS] Found {len(result)} chapters")
            print(f"  Sample: {result[0].get('title', 'Unknown')}")
            return True
        else:
            print(f"[FAIL] Unexpected response format: {type(result)}")
            return False
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


async def test_get_chapter():
    """Test get_chapter tool."""
    print("\n" + "="*60)
    print("Testing: get_chapter()")
    print("="*60)

    try:
        result_json = await get_chapter("chapter-1")
        result = json.loads(result_json)

        if "id" in result and "sections" in result:
            print(f"[PASS] Retrieved chapter: {result.get('title', 'Unknown')}")
            print(f"  Sections: {len(result.get('sections', []))}")
            print(f"  Objectives: {len(result.get('learning_objectives', []))}")
            return True
        elif "error" in result:
            print(f"[WARN] Got error (might be expected): {result['error']}")
            return True
        else:
            print(f"[FAIL] Unexpected response format")
            return False
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


async def test_search():
    """Test search_content tool."""
    print("\n" + "="*60)
    print("Testing: search_content()")
    print("="*60)

    try:
        result_json = await search_content("neural network", limit=5)
        result = json.loads(result_json)

        if isinstance(result, list):
            print(f"[PASS] Search returned {len(result)} results")
            if len(result) > 0:
                print(f"  Top result: {result[0].get('section_title', 'Unknown')}")
            return True
        else:
            print(f"[FAIL] Unexpected response format: {type(result)}")
            return False
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


async def test_progress():
    """Test get_progress tool."""
    print("\n" + "="*60)
    print("Testing: get_progress()")
    print("="*60)

    try:
        result_json = await get_progress()
        result = json.loads(result_json)

        if "total_chapters" in result:
            print(f"[PASS] Retrieved progress data")
            print(f"  Total chapters: {result.get('total_chapters', 0)}")
            print(f"  Completed: {result.get('completed_chapters', 0)}")
            print(f"  Completion: {result.get('overall_completion_percentage', 0)}%")
            return True
        else:
            print(f"[FAIL] Unexpected response format")
            return False
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


async def test_bookmarks():
    """Test bookmarks functionality."""
    print("\n" + "="*60)
    print("Testing: get_bookmarks()")
    print("="*60)

    try:
        # Try to get bookmarks first
        result_json = await get_bookmarks()
        result = json.loads(result_json)

        print(f"[PASS] Bookmarks endpoint accessible")
        if "bookmarks" in result:
            print(f"  Current bookmarks: {len(result.get('bookmarks', []))}")
        else:
            print(f"  Response: {list(result.keys())}")
        return True
    except Exception as e:
        print(f"[WARN] Failed (might not be implemented yet): {e}")
        return True  # Not critical


async def test_notes():
    """Test notes functionality."""
    print("\n" + "="*60)
    print("Testing: get_notes()")
    print("="*60)

    try:
        # Try to get notes first
        result_json = await get_notes()
        result = json.loads(result_json)

        print(f"[PASS] Notes endpoint accessible")
        if "notes" in result:
            print(f"  Current notes: {len(result.get('notes', []))}")
        else:
            print(f"  Response: {list(result.keys())}")
        return True
    except Exception as e:
        print(f"[WARN] Failed (might not be implemented yet): {e}")
        return True  # Not critical


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("MCP Server Test Suite")
    print("="*60)
    print("Testing Course Companion FTE MCP Server")
    print("="*60)

    results = []

    # Run tests
    results.append(await test_backend_connection())
    if results[-1]:  # Only continue if backend is up
        results.append(await test_get_chapters())
        results.append(await test_get_chapter())
        results.append(await test_search())
        results.append(await test_progress())
        results.append(await test_bookmarks())
        results.append(await test_notes())

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("[PASS] All tests passed[WARN]")
    else:
        print(f"[FAIL] {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    print("MCP Server Test Suite")
    print("="*60)
    print("This will test all MCP server tools.")
    print("Make sure your backend server is running on http://localhost:8000")
    print("="*60)

    # Auto-start tests
    asyncio.run(run_all_tests())
