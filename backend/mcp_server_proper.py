"""
Proper MCP Server with SSE transport for ChatGPT App

This implements the Model Context Protocol (MCP) specification correctly
with Server-Sent Events (SSE) transport for ChatGPT App integration.
"""

import asyncio
import json
import os
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")
APP_NAME = "course-companion-fte"
HTTP_PORT = int(os.getenv("MCP_PORT", "8001"))

# Create FastAPI app
app = FastAPI(title="Course Companion FTE MCP Server")


# Server metadata for MCP discovery
@app.get("/")
async def root():
    """Root endpoint with MCP server metadata."""
    return {
        "name": APP_NAME,
        "version": "2.0.0",
        "description": "MCP Server for Course Companion FTE",
        "protocol_version": "2024-11-05",
        "capabilities": {
            "tools": {},
            "resources": {}
        },
        "endpoints": {
            "mcp": "/mcp",  # This is what ChatGPT Apps expects!
            "sse": "/sse",
            "messages": "/messages"
        }
    }


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


# MCP Tools definitions
MCP_TOOLS = [
    {
        "name": "get_chapters",
        "description": "Get all available course chapters with access status and progress",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "annotations": {
            "readOnlyHint": True,
            "openWorldHint": False,
            "destructiveHint": False
        }
    },
    {
        "name": "get_chapter",
        "description": "Get full chapter content including all sections",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_id": {"type": "string", "description": "Chapter ID"}
            },
            "required": ["chapter_id"]
        },
        "annotations": {
            "readOnlyHint": True,
            "openWorldHint": False,
            "destructiveHint": False
        }
    },
    {
        "name": "search_content",
        "description": "Search course content for relevant sections",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        },
        "annotations": {
            "readOnlyHint": True,
            "openWorldHint": False,
            "destructiveHint": False
        }
    },
    {
        "name": "get_quiz",
        "description": "Get quiz questions for a chapter",
        "inputSchema": {
            "type": "object",
            "properties": {
                "quiz_id": {"type": "string", "description": "Quiz ID"}
            },
            "required": ["quiz_id"]
        },
        "annotations": {
            "readOnlyHint": True,
            "openWorldHint": False,
            "destructiveHint": False
        }
    },
    {
        "name": "submit_quiz",
        "description": "Submit quiz answers for grading",
        "inputSchema": {
            "type": "object",
            "properties": {
                "quiz_id": {"type": "string"},
                "answers": {"type": "object"}
            },
            "required": ["quiz_id", "answers"]
        },
        "annotations": {
            "readOnlyHint": False,
            "openWorldHint": False,
            "destructiveHint": False
        }
    },
    {
        "name": "get_progress",
        "description": "Get comprehensive learning progress",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"}
            },
            "required": ["user_id"]
        },
        "annotations": {
            "readOnlyHint": True,
            "openWorldHint": False,
            "destructiveHint": False
        }
    }
]


async def execute_tool(tool_name: str, arguments: dict) -> Any:
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


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "server": "MCP Server (SSE + POST)"}


@app.get("/mcp")
async def mcp_get():
    """MCP endpoint info - returns metadata on GET like test server."""
    return {
        "status": "healthy",
        "service": "Course Companion FTE MCP Server",
        "version": "2.0.0",
        "protocol": "jsonrpc-2.0",
        "endpoints": {
            "mcp": "/mcp (POST for JSON-RPC)",
            "messages": "/messages (POST for JSON-RPC)",
            "sse": "/sse (SSE transport)"
        }
    }


@app.post("/mcp")
async def handle_mcp_post(request: Request):
    """
    Handle MCP JSON-RPC messages via POST to /mcp.
    This is the primary endpoint like the test server.
    """
    return await handle_message(request)


@app.post("/messages")
async def handle_message(request: Request):
    """
    Handle MCP JSON-RPC messages via POST.
    This is the standard MCP HTTP endpoint.
    """
    body = await request.json()

    # Validate JSON-RPC request
    if not isinstance(body, dict):
        return {"error": "Invalid request"}

    jsonrpc = body.get("jsonrpc", "2.0")
    request_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})

    # Handle initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": APP_NAME,
                    "version": "2.0.0"
                }
            }
        }

    # Handle tools/list
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": MCP_TOOLS
            }
        }

    # Handle tools/call
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        result = await execute_tool(tool_name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }

    # Handle ping
    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {}
        }

    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }


async def sse_generator():
    """Generate SSE events."""
    # Send initial endpoint event
    data = json.dumps({
        "jsonrpc": "2.0",
        "method": "notifications/endpoint",
        "params": {
            "endpoint": "/messages"
        }
    })
    yield f"event: message\n"
    yield f"data: {data}\n\n"

    # Keep connection alive with comments
    try:
        while True:
            await asyncio.sleep(15)
            yield ": keepalive\n\n"
    except asyncio.CancelledError:
        pass


@app.get("/sse")
async def sse_endpoint():
    """
    SSE endpoint for MCP.
    Returns the proper content-type: text/event-stream
    """
    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/sse/")
async def sse_endpoint_trailing():
    """
    SSE endpoint for MCP with trailing slash (OpenAI standard format).
    Returns the proper content-type: text/event-stream
    """
    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/mcp")
async def mcp_endpoint():
    """
    Main MCP endpoint for ChatGPT Apps.
    This is the endpoint ChatGPT Apps connect to.
    Returns Server-Sent Events (SSE) for MCP protocol.
    """
    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    print("=" * 60)
    print(f"Starting MCP Server (Proper SSE + POST)")
    print(f"Server: {APP_NAME}")
    print(f"Port: {HTTP_PORT}")
    print(f"Backend: {BACKEND_URL}")
    print(f"\nEndpoints:")
    print(f"  SSE (ChatGPT): http://0.0.0.0:{HTTP_PORT}/sse/")
    print(f"  SSE (alt): http://0.0.0.0:{HTTP_PORT}/sse")
    print(f"  MCP (alt): http://0.0.0.0:{HTTP_PORT}/mcp")
    print(f"  POST: http://0.0.0.0:{HTTP_PORT}/messages")
    print(f"\nFor ChatGPT App, use:")
    print(f"  http://0.0.0.0:{HTTP_PORT}/sse/")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=HTTP_PORT,
        log_level="info"
    )
