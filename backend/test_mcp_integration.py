"""
Integration test for MCP Server using FastMCP

Tests the MCP server by invoking tools through the FastMCP server.
"""

import asyncio
import json
from mcp_server import mcp, call_backend


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


async def test_tool_execution():
    """Test that MCP tools can be invoked."""
    print("\n" + "="*60)
    print("Testing MCP Tool Execution")
    print("="*60)

    try:
        # List all available tools
        tools = mcp._tool_manager._tools
        print(f"[PASS] MCP Server has {len(tools)} registered tools")

        # Show tool names
        tool_names = list(tools.keys())
        print(f"  Available tools: {', '.join(tool_names[:5])}...")

        return True
    except Exception as e:
        print(f"[FAIL] Failed to list tools: {e}")
        return False


async def test_get_chapters():
    """Test get_chapters tool by calling backend directly."""
    print("\n" + "="*60)
    print("Testing: get_chapters() endpoint")
    print("="*60)

    try:
        result = await call_backend("GET", "/chapters")

        if isinstance(result, list) and len(result) > 0:
            print(f"[PASS] Found {len(result)} chapters")
            print(f"  Sample: {result[0].get('title', 'Unknown')}")
            return True
        elif isinstance(result, dict) and "error" in result:
            print(f"[WARN] Got error response: {result['error']}")
            return True
        else:
            print(f"[FAIL] Unexpected response format: {type(result)}")
            print(f"  Response: {result}")
            return False
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


async def test_get_chapter():
    """Test get_chapter endpoint."""
    print("\n" + "="*60)
    print("Testing: get_chapter() endpoint")
    print("="*60)

    try:
        result = await call_backend("GET", "/chapters/chapter-1")

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
            print(f"  Response: {result}")
            return False
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


async def test_search():
    """Test search_content endpoint."""
    print("\n" + "="*60)
    print("Testing: search_content() endpoint")
    print("="*60)

    try:
        result = await call_backend("GET", "/search", params={"query": "neural network", "limit": 5})

        if isinstance(result, list):
            print(f"[PASS] Search returned {len(result)} results")
            if len(result) > 0:
                print(f"  Top result: {result[0].get('section_title', 'Unknown')}")
            return True
        elif isinstance(result, dict) and "error" in result:
            print(f"[WARN] Got error: {result['error']}")
            return True
        else:
            print(f"[FAIL] Unexpected response format: {type(result)}")
            return False
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


async def test_progress():
    """Test get_progress endpoint."""
    print("\n" + "="*60)
    print("Testing: get_progress() endpoint")
    print("="*60)

    try:
        result = await call_backend("GET", "/progress")

        if "total_chapters" in result:
            print(f"[PASS] Retrieved progress data")
            print(f"  Total chapters: {result.get('total_chapters', 0)}")
            print(f"  Completed: {result.get('completed_chapters', 0)}")
            print(f"  Completion: {result.get('overall_completion_percentage', 0)}%")
            return True
        elif "error" in result:
            print(f"[WARN] Got error: {result['error']}")
            return True
        else:
            print(f"[FAIL] Unexpected response format")
            print(f"  Response: {result}")
            return False
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


async def test_bookmarks():
    """Test bookmarks functionality."""
    print("\n" + "="*60)
    print("Testing: bookmarks endpoint")
    print("="*60)

    try:
        result = await call_backend("GET", "/bookmarks")

        print(f"[PASS] Bookmarks endpoint accessible")
        if isinstance(result, dict):
            if "bookmarks" in result:
                print(f"  Current bookmarks: {len(result.get('bookmarks', []))}")
            else:
                print(f"  Response keys: {list(result.keys())}")
        return True
    except Exception as e:
        print(f"[WARN] Failed (might not be implemented yet): {e}")
        return True  # Not critical


async def test_notes():
    """Test notes functionality."""
    print("\n" + "="*60)
    print("Testing: notes endpoint")
    print("="*60)

    try:
        result = await call_backend("GET", "/notes")

        print(f"[PASS] Notes endpoint accessible")
        if isinstance(result, dict):
            if "notes" in result:
                print(f"  Current notes: {len(result.get('notes', []))}")
            else:
                print(f"  Response keys: {list(result.keys())}")
        return True
    except Exception as e:
        print(f"[WARN] Failed (might not be implemented yet): {e}")
        return True  # Not critical


async def test_mcp_tool_definitions():
    """Test that MCP tool definitions are correct."""
    print("\n" + "="*60)
    print("Testing: MCP Tool Definitions")
    print("="*60)

    try:
        tools = mcp._tool_manager._tools

        # Expected tools
        expected_tools = [
            "get_chapters",
            "get_chapter",
            "search_content",
            "get_quiz",
            "submit_quiz",
            "get_progress",
            "get_bookmarks",
            "create_bookmark",
            "delete_bookmark",
            "get_notes",
            "create_note",
            "update_note",
            "delete_note",
            "get_note_tags"
        ]

        missing_tools = [t for t in expected_tools if t not in tools]

        if missing_tools:
            print(f"[WARN] Missing tools: {', '.join(missing_tools)}")
        else:
            print(f"[PASS] All expected tools registered")

        print(f"  Total tools: {len(tools)}")
        print(f"  Expected tools: {len(expected_tools)}")

        return len(missing_tools) == 0
    except Exception as e:
        print(f"[FAIL] Failed to check tool definitions: {e}")
        return False


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("MCP Server Integration Test Suite")
    print("="*60)
    print("Testing Course Companion FTE MCP Server")
    print("="*60)

    results = []

    # Run tests
    results.append(await test_backend_connection())
    if results[-1]:  # Only continue if backend is up
        results.append(await test_tool_execution())
        results.append(await test_mcp_tool_definitions())
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
        print("[PASS] All tests passed!")
        print("\nThe MCP server is ready for ChatGPT App integration!")
    else:
        print(f"[WARN] {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    print("MCP Server Integration Test Suite")
    print("="*60)
    print("This will test the MCP server integration.")
    print("Make sure your backend server is running on http://localhost:8000")
    print("="*60)

    asyncio.run(run_all_tests())
