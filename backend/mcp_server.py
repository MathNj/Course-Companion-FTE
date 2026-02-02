"""
MCP Server for Course Companion FTE
Exposes backend functionality as MCP tools for ChatGPT App

This server wraps the existing FastAPI backend and exposes it via the
Model Context Protocol (MCP) using FastMCP for integration with
ChatGPT Apps built with the OpenAI Apps SDK.
"""

import asyncio
import json
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from fastmcp import FastMCP

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
APP_NAME = "course-companion-fte"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "AI-powered learning companion for mastering Generative AI fundamentals"

# Create MCP server
mcp = FastMCP(APP_NAME)


async def call_backend(
    method: str,
    path: str,
    params: Optional[dict] = None,
    data: Optional[dict] = None
) -> dict:
    """
    Make an HTTP request to the backend API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        path: API path (will be joined with BACKEND_URL)
        params: Query parameters
        data: Request body data

    Returns:
        Response data as dictionary

    Raises:
        httpx.HTTPError: If the request fails
    """
    url = urljoin(BACKEND_URL, path)

    try:
        if method.upper() == "GET":
            response = await client.get(url, params=params)
        elif method.upper() == "POST":
            response = await client.post(url, json=data)
        elif method.upper() == "PUT":
            response = await client.put(url, json=data)
        elif method.upper() == "DELETE":
            response = await client.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        # Return error information
        return {
            "error": str(e),
            "status_code": getattr(e.response, "status_code", None) if hasattr(e, "response") else None
        }


# HTTP client for backend communication
client = httpx.AsyncClient(timeout=30.0)


# ==================== MCP TOOLS ====================

@mcp.tool()
async def get_chapters() -> str:
    """
    Get all available course chapters with access status and progress.

    Returns a list of all course chapters including:
    - Chapter metadata (title, description, difficulty)
    - Access tier (free/premium)
    - User's access status
    - Current progress if any

    Example:
        User: "What chapters can I learn?"
        You: [Calls get_chapters()] → Presents available chapters
    """
    result = await call_backend("GET", "/chapters")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_chapter(chapter_id: str) -> str:
    """
    Get full chapter content including all sections.

    Retrieves complete chapter material with:
    - Learning objectives
    - All sections with content
    - Chapter summary
    - Next steps recommendations

    IMPORTANT: Always use this tool to get course material.
    NEVER generate your own explanations - use the content from this API.

    Args:
        chapter_id: Chapter identifier (e.g., "chapter-1", "chapter-2")

    Example:
        User: "Show me Chapter 1"
        You: [Calls get_chapter("chapter-1")] → Presents chapter content
    """
    result = await call_backend("GET", f"/chapters/{chapter_id}")

    # Check for premium gate error
    if "message" in result and "upgrade_benefits" in result:
        return json.dumps({
            "error": "Premium content required",
            "message": result["message"],
            "upgrade_benefits": result["upgrade_benefits"]
        })

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_quiz(quiz_id: str) -> str:
    """
    Get quiz questions for a chapter.

    Retrieves quiz with:
    - Quiz questions (no answer keys)
    - Question types (multiple choice, true/false, short answer)
    - Time limit
    - Passing score requirement
    - User's previous attempts (if any)

    Use submit_quiz() to grade answers.

    Args:
        quiz_id: Quiz identifier (e.g., "chapter-1-quiz", "chapter-2-quiz")

    Example:
        User: "Quiz me on Chapter 1"
        You: [Calls get_quiz("chapter-1-quiz")] → Presents quiz questions
    """
    result = await call_backend("GET", f"/quizzes/{quiz_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def submit_quiz(quiz_id: str, answers: dict) -> str:
    """
    Submit quiz answers for grading.

    Grades the quiz submission and returns:
    - Overall score (percentage)
    - Pass/fail status (70% to pass)
    - Detailed grading for each question
    - Explanations for correct answers
    - Feedback based on performance
    - Whether chapter was completed

    Also updates user progress if quiz is passed.

    Args:
        quiz_id: Quiz identifier (e.g., "chapter-1-quiz")
        answers: Map of question_id to selected answer

    Example:
        User: "Submit my quiz"
        You: [Calls submit_quiz("chapter-1-quiz", {"q1": "option_a", ...})]
    """
    result = await call_backend("POST", f"/quizzes/{quiz_id}/submit", data={
        "quiz_id": quiz_id,
        "answers": answers
    })
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_progress() -> str:
    """
    Get comprehensive progress summary.

    Returns detailed progress information:
    - Chapters completed vs total
    - Overall completion percentage
    - Current learning streak
    - Longest streak achieved
    - Milestones earned
    - Next milestone to achieve
    - Quiz statistics (attempts, pass rate)
    - Time spent learning

    Use this to celebrate achievements and motivate students!

    Example:
        User: "How am I doing?"
        User: "What's my progress?"
        You: [Calls get_progress()] → Shows comprehensive progress
    """
    result = await call_backend("GET", "/progress")
    return json.dumps(result, indent=2)


@mcp.tool()
async def search_content(query: str, limit: int = 20) -> str:
    """
    Search through all course content for relevant sections.

    Performs a full-text search across all accessible chapters
    to find content relevant to the student's question.

    Returns matching sections with:
    - Chapter and section titles
    - Relevant content snippets
    - Relevance scores
    - Match counts

    Use this for grounded Q&A - answer student questions using
    ONLY course material (zero hallucination).

    Args:
        query: Search query (minimum 2 characters)
        limit: Maximum number of results to return (default 20)

    Example:
        User: "What is a neural network?"
        You: [Calls search_content("neural network")] → Finds relevant sections
    """
    result = await call_backend("GET", "/chapters/search", params={
        "q": query,
        "limit": limit
    })
    return json.dumps(result, indent=2)


# ==================== BOOKMARKS & NOTES TOOLS ====================

@mcp.tool()
async def get_bookmarks() -> str:
    """
    Get all bookmarks for the current user.

    Returns list of saved bookmarks with:
    - Chapter and section information
    - Custom titles
    - Notes attached to bookmarks
    - Creation dates
    - Folder organization

    Example:
        User: "Show my bookmarks"
        You: [Calls get_bookmarks()] → Lists all saved bookmarks
    """
    result = await call_backend("GET", "/bookmarks")
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_bookmark(
    chapter_id: str,
    section_id: Optional[str] = None,
    title: Optional[str] = None,
    notes: Optional[str] = None
) -> str:
    """
    Create a new bookmark.

    Save a chapter or section for quick access later.

    Args:
        chapter_id: Chapter identifier (e.g., "chapter-1")
        section_id: Optional section identifier for specific sections
        title: Custom title for the bookmark
        notes: Optional notes to attach to the bookmark

    Example:
        User: "Bookmark this section"
        You: [Calls create_bookmark(...)] → Saves bookmark
    """
    result = await call_backend("POST", "/bookmarks", data={
        "chapter_id": chapter_id,
        "section_id": section_id,
        "title": title,
        "notes": notes
    })
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_bookmark(bookmark_id: str) -> str:
    """
    Delete a bookmark.

    Args:
        bookmark_id: ID of the bookmark to delete

    Example:
        User: "Remove this bookmark"
        You: [Calls delete_bookmark(...)] → Deletes bookmark
    """
    result = await call_backend("DELETE", f"/bookmarks/{bookmark_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_notes(
    chapter_id: Optional[str] = None,
    tag: Optional[str] = None
) -> str:
    """
    Get user's notes with optional filters.

    Returns all notes or filtered by chapter/tag.

    Args:
        chapter_id: Optional - filter by chapter
        tag: Optional - filter by tag

    Example:
        User: "Show my notes"
        You: [Calls get_notes()] → Lists all notes
    """
    params = {}
    if chapter_id:
        params["chapter_id"] = chapter_id
    if tag:
        params["tag"] = tag

    result = await call_backend("GET", "/notes", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_note(
    chapter_id: str,
    content: str,
    section_id: Optional[str] = None,
    tags: Optional[list[str]] = None
) -> str:
    """
    Create a new note.

    Save a note with content and optional tags.

    Args:
        chapter_id: Chapter identifier
        content: Note content
        section_id: Optional section identifier
        tags: Optional list of tags for organization

    Example:
        User: "Take a note: Neural networks have layers"
        You: [Calls create_note(...)] → Saves note
    """
    result = await call_backend("POST", "/notes", data={
        "chapter_id": chapter_id,
        "section_id": section_id,
        "content": content,
        "tags": tags or []
    })
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_note(
    note_id: str,
    content: Optional[str] = None
) -> str:
    """
    Update an existing note.

    Args:
        note_id: ID of the note to update
        content: New content for the note

    Example:
        User: "Update my note with more details"
        You: [Calls update_note(...)] → Updates note
    """
    result = await call_backend("PUT", f"/notes/{note_id}", data={
        "content": content
    })
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_note(note_id: str) -> str:
    """
    Delete a note.

    Args:
        note_id: ID of the note to delete

    Example:
        User: "Delete this note"
        You: [Calls delete_note(...)] → Deletes note
    """
    result = await call_backend("DELETE", f"/notes/{note_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_note_tags() -> str:
    """
    Get all unique tags across user's notes.

    Returns list of all tags with counts and colors.

    Example:
        User: "What tags do I have?"
        You: [Calls get_note_tags()] → Lists all tags
    """
    result = await call_backend("GET", "/notes/tags")
    return json.dumps(result, indent=2)


# ==================== PHASE 2: HYBRID FEATURES (PREMIUM) ====================

@mcp.tool()
async def generate_adaptive_path(
    user_goal: str = "comprehensive",
    time_available: int = 30,
    current_level: str = "beginner"
) -> str:
    """
    Generate personalized learning path (Premium Feature).

    ⚠️ PREMIUM FEATURE - Uses LLM APIs and will incur costs.

    Creates a customized learning path based on:
    - User's learning goals
    - Time available per day
    - Current knowledge level
    - Performance on quizzes and assessments

    Only call for premium users who explicitly request this feature.

    Args:
        user_goal: Learning objective (quick_start, comprehensive, exam_prep, research)
        time_available: Minutes available per day
        current_level: Current knowledge level (beginner, intermediate, advanced)

    Returns:
        Personalized learning path with recommendations
        Token usage and cost information

    Example:
        User: "Create a personalized learning path"
        You: "This will use AI analysis and cost ~$0.01. Continue?"
        User: "Yes"
        You: [Calls generate_adaptive_path(...)] → Returns personalized path
    """
    result = await call_backend("POST", "/v2/adaptive/path", data={
        "user_goal": user_goal,
        "time_available": time_available,
        "current_level": current_level
    })
    return json.dumps(result, indent=2)


# ==================== SERVER INFO ====================

@mcp.tool()
async def mcp_server_info() -> str:
    """
    Get information about this MCP server.

    Returns server metadata including:
    - Server name and version
    - Available tools
    - Connection information
    """
    return json.dumps({
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "backend_url": BACKEND_URL,
        "tools": [
            "get_chapters",
            "get_chapter",
            "get_quiz",
            "submit_quiz",
            "get_progress",
            "search_content",
            "get_bookmarks",
            "create_bookmark",
            "delete_bookmark",
            "get_notes",
            "create_note",
            "update_note",
            "delete_note",
            "get_note_tags",
            "generate_adaptive_path",
            "mcp_server_info"
        ],
        "phase_1_tools": [
            "get_chapters",
            "get_chapter",
            "get_quiz",
            "submit_quiz",
            "get_progress",
            "search_content",
            "get_bookmarks",
            "create_bookmark",
            "delete_bookmark",
            "get_notes",
            "create_note",
            "update_note",
            "delete_note",
            "get_note_tags"
        ],
        "phase_2_tools": [
            "generate_adaptive_path"
        ]
    }, indent=2)


# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    import sys

    print(f"Starting MCP server for {APP_NAME}")
    print(f"Version: {APP_VERSION}")
    print(f"Backend URL: {BACKEND_URL}")
    print("\nAvailable tools:")
    print("- get_chapters")
    print("- get_chapter")
    print("- get_quiz")
    print("- submit_quiz")
    print("- get_progress")
    print("- search_content")
    print("- get_bookmarks")
    print("- create_bookmark")
    print("- delete_bookmark")
    print("- get_notes")
    print("- create_note")
    print("- update_note")
    print("- delete_note")
    print("- get_note_tags")
    print("- generate_adaptive_path (Premium)")
    print("- mcp_server_info")
    print("\nRunning on stdio transport...")
    print("Press Ctrl+C to stop")
    print()

    # Run the server
    mcp.run()
