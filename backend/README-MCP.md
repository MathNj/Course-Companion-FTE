# MCP Server for Course Companion FTE

## Overview

This MCP (Model Context Protocol) server wraps the Course Companion FTE backend and exposes it as tools for ChatGPT Apps built with the OpenAI Apps SDK.

## What is MCP?

The **Model Context Protocol (MCP)** is a protocol that allows ChatGPT Apps to:
- Call tools (functions) on your backend
- Access resources from your system
- Maintain stateful conversations

The **OpenAI Apps SDK** uses MCP to connect ChatGPT Apps to your backend.

## Architecture

```
ChatGPT App (built with Apps SDK)
    ↓ (MCP Protocol)
MCP Server (this file)
    ↓ (HTTP)
FastAPI Backend (your existing API)
```

## Available Tools

### Core Content Tools
- `get_chapters` - List all available chapters
- `get_chapter` - Get full chapter content
- `search_content` - Search course content

### Assessment Tools
- `get_quiz` - Get quiz questions
- `submit_quiz` - Submit answers for grading

### Progress Tools
- `get_progress` - Get comprehensive progress summary

### Organization Tools
- `get_bookmarks` - Get user's bookmarks
- `create_bookmark` - Save a bookmark
- `delete_bookmark` - Remove a bookmark
- `get_notes` - Get user's notes
- `create_note` - Create a note
- `update_note` - Update a note
- `delete_note` - Delete a note
- `get_note_tags` - Get all note tags

### Premium Tools (Phase 2)
- `generate_adaptive_path` - AI-powered learning paths (costs ~$0.01)

## Setup

### 1. Install Dependencies

```bash
pip install mcp httpx
```

### 2. Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start the MCP Server

#### Option A: Stdio Transport (for local testing)
```bash
python mcp_server.py
```

#### Option B: SSE Transport (for HTTP/production)
```bash
python mcp_server.py --sse --port=8001
```

The MCP server will start on port 8001 with SSE transport.

### 4. Test the MCP Server

```bash
python test_mcp_server.py
```

This will test all tools and verify connectivity.

## Configuration

### Backend URL

The `BACKEND_URL` constant in `mcp_server.py` points to your FastAPI backend:

```python
BACKEND_URL = "http://localhost:8000/api/v1"
```

For production, update this to your production URL.

### Authentication

Currently, the MCP server doesn't include authentication. To add authentication:

1. Get user's API key or token
2. Add it to HTTP headers:
```python
headers = {"Authorization": f"Bearer {token}"}
response = await client.get(url, headers=headers)
```

## Usage with ChatGPT Apps

### Creating the App

1. Go to https://chat.openai.com
2. Click **Create** → **App**
3. Choose **Build with Apps SDK**
4. Configure:
   - **Name**: Course Companion FTE
   - **Description**: AI learning companion for Generative AI
   - **Category**: Education
   - **MCP Server**: Your deployed MCP server URL
   - **Transport**: SSE or stdio

### Testing in ChatGPT

Once configured, test with these prompts:

**Basic Usage:**
```
User: "What chapters are available?"
ChatGPT: [Calls get_chapters()] → Lists chapters

User: "Show me Chapter 1"
ChatGPT: [Calls get_chapter("chapter-1")] → Presents content

User: "Quiz me"
ChatGPT: [Calls get_quiz() + submit_quiz()] → Runs quiz
```

**Advanced Usage:**
```
User: "Search for neural networks"
ChatGPT: [Calls search_content("neural networks")] → Finds relevant sections

User: "How am I doing?"
ChatGPT: [Calls get_progress()] → Shows progress, streaks, milestones

User: "Bookmark this section"
ChatGPT: [Calls create_bookmark()] → Saves bookmark

User: "Take a note about this"
ChatGPT: [Calls create_note()] → Saves note
```

## Deployment

### Local Development

For local testing with ChatGPT, you'll need to expose your MCP server publicly:

1. **Use ngrok** (recommended for testing):
```bash
ngrok http 8001
```

2. **Deploy to production**:
   - Fly.io, Railway, Render, AWS, etc.
   - Ensure HTTPS is enabled
   - Note the public URL

### Production Deployment

1. **Deploy Backend**: Follow `backend/README.md`
2. **Deploy MCP Server**: Deploy `mcp_server.py`
   - Can be same server as backend (use SSE mode)
   - Or separate server
3. **Update ChatGPT App**: Point to production MCP URL

## Monitoring

### Logs

The MCP server logs all tool calls:

```
2025-01-31 12:00:00 INFO [get_chapters] Called
2025-01-31 12:00:01 INFO [get_chapter] Retrieved chapter-1
2025-01-31 12:00:02 INFO [submit_quiz] Graded quiz, score: 85%
```

### Analytics

Track which tools are most used:

```python
# Add to your backend analytics
tool_calls_counter = {
    "get_chapters": 1234,
    "get_chapter": 5678,
    "get_quiz": 2345,
    "submit_quiz": 2101,
    "get_progress": 890,
    "search_content": 456,
    # ...
}
```

## Compliance

### Zero-Backend-LLM Architecture ✓

This MCP server maintains compliance because:

1. **No LLM in MCP server** - Just proxies to backend
2. **Backend remains deterministic** - No LLM calls in Phase 1
3. **ChatGPT does all reasoning** - Using tools to fetch content
4. **Hybrid features isolated** - Separate `/v2/*` endpoints
5. **Cost tracking** - Premium features track token usage

### Architecture Requirements Met

- ✓ Phase 1: Zero-LLM backend
- ✓ Dual Frontend: ChatGPT App + Web App
- ✓ Same API for both frontends
- ✓ Freemium gating functional
- ✓ Progress tracking persists

## Troubleshooting

### MCP Server Won't Start

**Problem**: `ImportError: No module named 'mcp'`

**Solution**:
```bash
pip install mcp
```

### Backend Connection Refused

**Problem**: `Connection refused` error

**Solution**: Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Tools Return Errors

**Problem**: All tools return 500 errors

**Solution**:
1. Check backend logs: `tail -f backend/logs/*.log`
2. Verify CORS is configured
3. Check authentication

### ChatGPT Can't Connect

**Problem**: ChatGPT says "Can't reach your server"

**Solution**:
1. Ensure server is publicly accessible (not localhost)
2. Use ngrok for testing: `ngrok http 8001`
3. Check firewall settings
4. Verify SSL certificate (HTTPS required)

## Development

### Adding New Tools

To add a new tool:

1. Add backend endpoint:
```python
@server.tool("my_new_tool")
async def my_new_tool(param1: str) -> str:
    """Tool description."""
    result = await call_backend("GET", f"/my-endpoint/{param1}")
    return json.dumps(result)
```

2. Update `app-manifest.json` with tool info
3. Test with `test_mcp_server.py`

### Updating Instructions

To update the system instructions that ChatGPT follows:

1. Edit `systemInstructions` in `app-manifest.json`
2. Resubmit/republish the app in ChatGPT

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Apps SDK Documentation](https://developers.openai.com/apps-sdk/)
- [Quickstart Guide](https://developers.openai.com/apps-sdk/quickstart/)
- [App Submission](https://openai.com/index/developers-can-now-submit-apps-to-chatgpt/)

## Support

For issues or questions:
- Check `backend/README.md` for backend issues
- Check `chatgpt-app/README.md` for ChatGPT App configuration
- Review `Course-Companion-FTE.md` for requirements

## License

[Your License]
