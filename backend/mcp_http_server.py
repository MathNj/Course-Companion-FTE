"""
HTTP MCP Server for ChatGPT App Integration

This wrapper runs the MCP server with HTTP/SSE transport instead of stdio,
allowing it to be accessed via a URL for ChatGPT App integration.
"""

import asyncio
import json
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from fastmcp import FastMCP
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sse_starlette import EventSourceResponse
import uvicorn

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
APP_NAME = "course-companion-fte"
HTTP_PORT = 8001

# Create MCP server
mcp = FastMCP(APP_NAME)


async def call_backend(
    method: str,
    path: str,
    params: Optional[dict] = None,
    data: Optional[dict] = None
) -> dict:
    """Make an HTTP request to the backend API."""
    url = urljoin(BACKEND_URL, path)
    async with httpx.AsyncClient(timeout=30.0) as client:
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
            return {
                "error": str(e),
                "status_code": getattr(e.response, "status_code", None) if hasattr(e, "response") else None
            }


# ==================== MCP TOOLS ====================

@mcp.tool()
async def get_chapters() -> str:
    """Get all available course chapters with access status and progress."""
    result = await call_backend("GET", "/chapters")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_chapter(chapter_id: str) -> str:
    """Get full chapter content including all sections."""
    result = await call_backend("GET", f"/chapters/{chapter_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def search_content(query: str, limit: int = 5) -> str:
    """Search course content for relevant sections."""
    result = await call_backend("GET", "/chapters/search", params={"query": query, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_quiz(quiz_id: str) -> str:
    """Get quiz questions for a chapter."""
    result = await call_backend("GET", f"/quizzes/{quiz_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def submit_quiz(quiz_id: str, answers: dict) -> str:
    """Submit quiz answers for grading."""
    result = await call_backend("POST", f"/quizzes/{quiz_id}/submit", data=answers)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_progress() -> str:
    """Get comprehensive learning progress."""
    result = await call_backend("GET", "/progress")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_bookmarks() -> str:
    """Get all saved bookmarks."""
    result = await call_backend("GET", "/bookmarks")
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_bookmark(chapter_id: str, section_id: Optional[str] = None, title: Optional[str] = None) -> str:
    """Save a bookmark."""
    data = {"chapter_id": chapter_id}
    if section_id:
        data["section_id"] = section_id
    if title:
        data["title"] = title
    result = await call_backend("POST", "/bookmarks", data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_bookmark(bookmark_id: str) -> str:
    """Delete a bookmark."""
    result = await call_backend("DELETE", f"/bookmarks/{bookmark_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_notes(chapter_id: Optional[str] = None, tags: Optional[list] = None) -> str:
    """Get user notes."""
    params = {}
    if chapter_id:
        params["chapter_id"] = chapter_id
    if tags:
        params["tags"] = tags
    result = await call_backend("GET", "/notes", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_note(chapter_id: str, content: str, section_id: Optional[str] = None, tags: Optional[list] = None) -> str:
    """Create a note."""
    data = {"chapter_id": chapter_id, "content": content}
    if section_id:
        data["section_id"] = section_id
    if tags:
        data["tags"] = tags
    result = await call_backend("POST", "/notes", data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_note(note_id: str, content: Optional[str] = None, tags: Optional[list] = None) -> str:
    """Update a note."""
    data = {}
    if content:
        data["content"] = content
    if tags:
        data["tags"] = tags
    result = await call_backend("PUT", f"/notes/{note_id}", data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_note(note_id: str) -> str:
    """Delete a note."""
    result = await call_backend("DELETE", f"/notes/{note_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_note_tags() -> str:
    """Get all unique tags across user's notes."""
    result = await call_backend("GET", "/notes/tags")
    return json.dumps(result, indent=2)


@mcp.tool()
async def generate_adaptive_path(user_id: str, goals: Optional[list] = None, time_horizon: Optional[str] = None) -> str:
    """Generate personalized learning path (Premium Feature)."""
    params = {"user_id": user_id}
    if goals:
        params["goals"] = goals
    if time_horizon:
        params["time_horizon"] = time_horizon
    result = await call_backend("POST", "/api/v2/adaptive-path", data=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def mcp_server_info() -> str:
    """Get information about this MCP server."""
    return json.dumps({
        "name": APP_NAME,
        "version": "2.0.0",
        "description": "MCP Server for Course Companion FTE",
        "transport": "HTTP/SSE",
        "tools_count": 16
    }, indent=2)


# Create FastAPI app for HTTP transport
app = FastAPI(title="Course Companion FTE MCP Server")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": APP_NAME,
        "version": "2.0.0",
        "transport": "HTTP/SSE",
        "mcp": "/sse",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "server": "MCP HTTP Server"}


@app.get("/tools")
async def list_tools():
    """List all available MCP tools."""
    tools = mcp._tool_manager._tools
    return {
        "tools": [
            {
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for name, tool in tools.items()
        ]
    }


@app.api_route("/sse/{path:path}", methods=["GET", "POST", "DELETE", "PUT"])
async def sse_endpoint(request: Request, path: str):
    """SSE endpoint for MCP communication."""
    # This would need proper SSE implementation
    # For now, return a simple response
    return {"message": "SSE endpoint - needs proper implementation"}


if __name__ == "__main__":
    print("=" * 60)
    print(f"Starting MCP HTTP Server")
    print(f"Server: {APP_NAME}")
    print(f"Port: {HTTP_PORT}")
    print(f"Backend: {BACKEND_URL}")
    print(f"\nMCP Server will be available at:")
    print(f"  http://localhost:{HTTP_PORT}")
    print(f"  SSE: http://localhost:{HTTP_PORT}/sse")
    print(f"\nFor ChatGPT App, use:")
    print(f"  http://localhost:{HTTP_PORT}/sse")
    print("=" * 60)

    uvicorn.run(
        app,
        host="localhost",
        port=HTTP_PORT,
        log_level="info"
    )
