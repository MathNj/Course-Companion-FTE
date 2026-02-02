# ChatGPT App Setup Guide

This guide walks you through creating and deploying your ChatGPT App using the OpenAI Apps SDK.

## Prerequisites

1. **OpenAI Apps SDK Access** - You need access to the OpenAI Apps SDK (released October 2025)
2. **MCP Server Running** - Your MCP server should be running and accessible
3. **Cloudflare Tunnel** (for local testing) or production deployment

## Step 1: Prepare MCP Server

### Option A: Local Testing with Cloudflare Tunnel

Since you're using **Cloudflare R2** for content storage, use Cloudflare Tunnel for local testing:

```bash
# Install cloudflared
npm install -g cloudflared

# Start tunnel for your backend
cloudflared tunnel --url http://localhost:8000

# You'll get a public URL like:
# https://your-app-name.your-subdomain.dev
```

**Important:** Update your `chatgpt-app-config.yaml` with the tunnel URL:
```yaml
mcp_server:
  url: "https://your-app-name.your-subdomain.dev/mcp"
```

### Option B: Production Deployment

Deploy your backend to a cloud provider (AWS, GCP, Azure, Railway, Render, etc.) and get a public HTTPS URL.

Update your `chatgpt-app-config.yaml`:
```yaml
mcp_server:
  url: "https://your-production-domain.com/mcp"
```

## Step 2: Create ChatGPT App

### Using ChatGPT Interface (Recommended)

1. **Open ChatGPT**
   - Go to https://chat.openai.com
   - Navigate to "Explore" or "Apps" section

2. **Create New App**
   - Click "Create App" or "Build App"
   - Choose "From Scratch" or "Use Template"

3. **Configure App Settings**

   **Basic Information:**
   - App Name: `Course Companion FTE`
   - Description: `Conversational tutor that navigates course content, answers grounded questions, runs quizzes, and tracks progress.`
   - Category: `Education`

   **MCP Server:**
   - Server URL: Your Cloudflare Tunnel or production URL
   - Auth Type: `none` (for now, can add API key later)

   **Tools:**
   Copy the tool definitions from `chatgpt-app-config.yaml`:
   - get_chapters
   - get_chapter
   - search_content
   - get_quiz
   - submit_quiz
   - get_progress
   - get_bookmarks
   - create_bookmark
   - delete_bookmark
   - get_notes
   - create_note
   - update_note
   - delete_note
   - get_note_tags
   - generate_adaptive_path (Premium)
   - mcp_server_info

   **System Instructions:**
   Copy the `system_instructions` section from `chatgpt-app-config.yaml`

   **Conversation Starters:**
   Copy the `conversation_starters` from the config

4. **Test App**
   - Use the "Test" button in the ChatGPT interface
   - Try each conversation starter
   - Verify tools are being called correctly

5. **Publish App**
   - Click "Publish" or "Submit to App Store"
   - Add screenshots and detailed description
   - Set pricing (freemium)
   - Submit for review

## Step 3: Verify MCP Server Connection

### Test MCP Server Directly

```bash
# Start your backend
cd backend
uvicorn app.main:app --reload

# In another terminal, start MCP server in test mode
python -c "
from mcp_server import mcp
import asyncio

async def test():
    tools = mcp._tool_manager._tools
    print(f'Registered tools: {len(tools)}')
    for name, tool in tools.items():
        print(f'  - {name}')

asyncio.run(test())
"
```

Expected output:
```
Registered tools: 16
  - get_chapters
  - get_chapter
  - search_content
  - get_quiz
  - submit_quiz
  - get_progress
  - get_bookmarks
  - create_bookmark
  - delete_bookmark
  - get_notes
  - create_note
  - update_note
  - delete_note
  - get_note_tags
  - generate_adaptive_path
  - mcp_server_info
```

### Test Backend API

```bash
# Test backend is running
curl http://localhost:8000/

# Expected response:
# {"name":"Course Companion FTE","version":"1.0.0",...}

# Test MCP server endpoint (if using SSE transport)
curl http://localhost:8000/mcp
```

## Step 4: Configure Authentication (Optional)

Currently using `auth: type: "none"`. For production, you may want to add authentication:

### Option A: API Key Authentication

```yaml
mcp_server:
  url: "https://your-domain.com/mcp"
  auth:
    type: "api_key"
    header_name: "X-API-Key"
    # Users will need to provide their API key
```

### Option B: OAuth2 Authentication

```yaml
mcp_server:
  url: "https://your-domain.com/mcp"
  auth:
    type: "oauth2"
    scopes:
      - "read"
      - "write"
    # Configure OAuth2 flow in your backend
```

## Step 5: Monitor App Usage

Once published, monitor:

1. **Tool Usage** - Which tools are called most frequently
2. **Error Rates** - Failed tool calls
3. **User Feedback** - Ratings and reviews
4. **Premium Conversion** - Free to paid upgrade rate

## Configuration Files

### Primary Files

- `chatgpt-app/chatgpt-app-config.yaml` - Main app configuration (YAML format)
- `chatgpt-app/app-manifest.json` - Alternative JSON format
- `backend/mcp_server.py` - MCP server implementation
- `backend/test_mcp_integration.py` - Test suite

### Quick Reference

```yaml
# Quick Config Summary
app:
  name: "Course Companion FTE"
  category: "Education"

mcp_server:
  url: "https://YOUR_DOMAIN.com/mcp"  # UPDATE THIS
  auth:
    type: "none"

tools: 16 tools total
  - 6 core tools (content, quizzes, progress)
  - 7 organization tools (bookmarks, notes)
  - 1 premium tool (adaptive learning)
  - 2 system tools (info, search)

pricing:
  tier: "freemium"
  free: "Chapters 1-3, quizzes, progress"
  premium: "$9.99/month - Chapters 4-6 + AI features"
```

## Testing Checklist

Before publishing, verify:

- [ ] Backend server running on port 8000
- [ ] MCP server starts without errors
- [ ] All 16 tools registered
- [ ] Cloudflare Tunnel or production URL accessible
- [ ] ChatGPT App can connect to MCP server
- [ ] Each tool can be called successfully
- [ ] Error handling works correctly
- [ ] Free vs Premium content access works
- [ ] Progress tracking updates
- [ ] Bookmarks and notes save/load correctly

## Troubleshooting

### Issue: "Cannot connect to MCP server"

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/`
2. Check Cloudflare Tunnel is active
3. Verify MCP server URL in config
4. Check firewall/network settings

### Issue: "Tool not found"

**Solution:**
1. Restart MCP server
2. Check tool names match config
3. Verify FastMCP registration: `mcp._tool_manager._tools`

### Issue: "Authentication error"

**Solution:**
1. Check auth type in config matches backend
2. Verify API keys if using `api_key` auth
3. Check OAuth2 flow if using `oauth2` auth

### Issue: "404 on backend endpoints"

**Solution:**
1. Verify backend routes are correct
2. Check `/api/v1` prefix in MCP server
3. Ensure user is authenticated for protected endpoints

## Next Steps

1. **Setup Cloudflare Tunnel** for local testing
2. **Create App** in ChatGPT interface
3. **Test thoroughly** with each tool
4. **Deploy to production** when ready
5. **Submit to App Store** for public access

## Support

- OpenAI Apps SDK Docs: https://platform.openai.com/docs/apps
- MCP Protocol Docs: https://modelcontextprotocol.io
- FastMCP Docs: https://github.com/jlowin/fastmcp

## Success Criteria

✅ App created in ChatGPT interface
✅ MCP server connected and accessible
✅ All tools working correctly
✅ Free tier content accessible
✅ Premium features properly gated
✅ Progress tracking functional
✅ Error handling working
✅ Ready for App Store submission

---

**Status:** Ready for ChatGPT App creation
**Confidence:** High
**Risk:** Low

The MCP server is tested and working. Follow this guide to create your ChatGPT App!
