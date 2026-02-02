"""
SSE MCP Server for ChatGPT App Integration

This server provides proper SSE (Server-Sent Events) transport for MCP protocol,
allowing ChatGPT Apps to connect via HTTP with text/event-stream content type.
"""

import asyncio
import json
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
APP_NAME = "course-companion-fte"
HTTP_PORT = 8001

# Create FastAPI app
app = FastAPI(title="Course Companion FTE MCP Server (SSE)")


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

TOOLS_LIST = {
    "get_chapters": {
        "name": "get_chapters",
        "description": "Get all available course chapters with access status and progress",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "get_chapter": {
        "name": "get_chapter",
        "description": "Get full chapter content including all sections",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_id": {"type": "string"}
            },
            "required": ["chapter_id"]
        }
    },
    "search_content": {
        "name": "search_content",
        "description": "Search course content for relevant sections",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    "get_quiz": {
        "name": "get_quiz",
        "description": "Get quiz questions for a chapter",
        "inputSchema": {
            "type": "object",
            "properties": {
                "quiz_id": {"type": "string"}
            },
            "required": ["quiz_id"]
        }
    },
    "submit_quiz": {
        "name": "submit_quiz",
        "description": "Submit quiz answers for grading",
        "inputSchema": {
            "type": "object",
            "properties": {
                "quiz_id": {"type": "string"},
                "answers": {"type": "object"}
            },
            "required": ["quiz_id", "answers"]
        }
    },
    "get_progress": {
        "name": "get_progress",
        "description": "Get comprehensive learning progress",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"}
            }
        }
    },
    "get_bookmarks": {
        "name": "get_bookmarks",
        "description": "Get all saved bookmarks",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "create_bookmark": {
        "name": "create_bookmark",
        "description": "Save a bookmark",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_id": {"type": "string"},
                "section_id": {"type": "string"},
                "title": {"type": "string"}
            },
            "required": ["chapter_id"]
        }
    },
    "delete_bookmark": {
        "name": "delete_bookmark",
        "description": "Delete a bookmark",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bookmark_id": {"type": "string"}
            },
            "required": ["bookmark_id"]
        }
    },
    "get_notes": {
        "name": "get_notes",
        "description": "Get user notes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_id": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            }
        }
    },
    "create_note": {
        "name": "create_note",
        "description": "Create a note",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_id": {"type": "string"},
                "content": {"type": "string"},
                "section_id": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["chapter_id", "content"]
        }
    },
    "update_note": {
        "name": "update_note",
        "description": "Update a note",
        "inputSchema": {
            "type": "object",
            "properties": {
                "note_id": {"type": "string"},
                "content": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["note_id"]
        }
    },
    "delete_note": {
        "name": "delete_note",
        "description": "Delete a note",
        "inputSchema": {
            "type": "object",
            "properties": {
                "note_id": {"type": "string"}
            },
            "required": ["note_id"]
        }
    },
    "get_note_tags": {
        "name": "get_note_tags",
        "description": "Get all unique tags across user's notes",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "generate_adaptive_path": {
        "name": "generate_adaptive_path",
        "description": "Generate personalized learning path (Premium Feature)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "goals": {"type": "array", "items": {"type": "string"}},
                "time_horizon": {"type": "string"}
            },
            "required": ["user_id"]
        }
    }
}


async def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a tool call."""
    try:
        if tool_name == "get_chapters":
            result = await call_backend("GET", "/chapters")
        elif tool_name == "get_chapter":
            chapter_id = arguments.get("chapter_id")
            result = await call_backend("GET", f"/chapters/{chapter_id}")
        elif tool_name == "search_content":
            query = arguments.get("query")
            limit = arguments.get("limit", 5)
            result = await call_backend("GET", "/chapters/search", params={"query": query, "limit": limit})
        elif tool_name == "get_quiz":
            quiz_id = arguments.get("quiz_id")
            result = await call_backend("GET", f"/quizzes/{quiz_id}")
        elif tool_name == "submit_quiz":
            quiz_id = arguments.get("quiz_id")
            answers = arguments.get("answers")
            result = await call_backend("POST", f"/quizzes/{quiz_id}/submit", data=answers)
        elif tool_name == "get_progress":
            result = await call_backend("GET", "/progress")
        elif tool_name == "get_bookmarks":
            result = await call_backend("GET", "/bookmarks")
        elif tool_name == "create_bookmark":
            chapter_id = arguments.get("chapter_id")
            section_id = arguments.get("section_id")
            title = arguments.get("title")
            data = {"chapter_id": chapter_id}
            if section_id:
                data["section_id"] = section_id
            if title:
                data["title"] = title
            result = await call_backend("POST", "/bookmarks", data=data)
        elif tool_name == "delete_bookmark":
            bookmark_id = arguments.get("bookmark_id")
            result = await call_backend("DELETE", f"/bookmarks/{bookmark_id}")
        elif tool_name == "get_notes":
            params = {}
            if arguments.get("chapter_id"):
                params["chapter_id"] = arguments["chapter_id"]
            if arguments.get("tags"):
                params["tags"] = arguments["tags"]
            result = await call_backend("GET", "/notes", params=params)
        elif tool_name == "create_note":
            chapter_id = arguments.get("chapter_id")
            content = arguments.get("content")
            section_id = arguments.get("section_id")
            tags = arguments.get("tags")
            data = {"chapter_id": chapter_id, "content": content}
            if section_id:
                data["section_id"] = section_id
            if tags:
                data["tags"] = tags
            result = await call_backend("POST", "/notes", data=data)
        elif tool_name == "update_note":
            note_id = arguments.get("note_id")
            content = arguments.get("content")
            tags = arguments.get("tags")
            data = {}
            if content:
                data["content"] = content
            if tags:
                data["tags"] = tags
            result = await call_backend("PUT", f"/notes/{note_id}", data=data)
        elif tool_name == "delete_note":
            note_id = arguments.get("note_id")
            result = await call_backend("DELETE", f"/notes/{note_id}")
        elif tool_name == "get_note_tags":
            result = await call_backend("GET", "/notes/tags")
        elif tool_name == "generate_adaptive_path":
            user_id = arguments.get("user_id")
            goals = arguments.get("goals")
            time_horizon = arguments.get("time_horizon")
            params = {"user_id": user_id}
            if goals:
                params["goals"] = goals
            if time_horizon:
                params["time_horizon"] = time_horizon
            result = await call_backend("POST", "/api/v2/adaptive-path", data=params)
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return {
            "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
            "isError": False
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": str(e)})}],
            "isError": True
        }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": APP_NAME,
        "version": "2.0.0",
        "transport": "SSE",
        "endpoints": {
            "sse": "/sse",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "server": "MCP SSE Server"}


@app.get("/tools")
async def list_tools():
    """List all available MCP tools."""
    return {
        "tools": list(TOOLS_LIST.values())
    }


@app.post("/tools/{tool_name}")
async def call_tool_endpoint(tool_name: str, request: Request):
    """HTTP endpoint for calling tools (for testing)."""
    arguments = await request.json()
    result = await execute_tool(tool_name, arguments)
    return result


@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP protocol communication."""

    async def event_generator():
        """Generate SSE events for MCP communication."""
        # Send initialization event
        yield {
            "event": "message",
            "data": json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": APP_NAME,
                        "version": "2.0.0"
                    }
                }
            })
        }

        # Keep connection open for incoming requests
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                # Send keepalive comments every 15 seconds
                await asyncio.sleep(15)
                yield {
                    "event": "keepalive",
                    "data": ""
                }
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    print("=" * 60)
    print(f"Starting MCP SSE Server")
    print(f"Server: {APP_NAME}")
    print(f"Port: {HTTP_PORT}")
    print(f"Backend: {BACKEND_URL}")
    print(f"\nMCP Server will be available at:")
    print(f"  http://localhost:{HTTP_PORT}")
    print(f"  SSE Endpoint: http://localhost:{HTTP_PORT}/sse")
    print(f"\nFor ChatGPT App, use:")
    print(f"  http://localhost:{HTTP_PORT}/sse")
    print("=" * 60)

    uvicorn.run(
        app,
        host="localhost",
        port=HTTP_PORT,
        log_level="info"
    )
