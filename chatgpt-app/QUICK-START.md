# ChatGPT App Quick Reference

## One-Line Summary

Conversational tutor that navigates course content, answers grounded questions, runs quizzes, and tracks progress.

## App Configuration

```yaml
name: "Course Companion FTE"
category: "Education"
mcp_server_url: "https://YOUR_DOMAIN.com/mcp"
auth: "none"
```

## Tool Summary (16 Total)

### Core Tools (6)
| Tool | Purpose | Read-Only |
|------|---------|-----------|
| `get_chapters` | List all chapters | ✅ |
| `get_chapter` | Get chapter content | ✅ |
| `search_content` | Search course content | ✅ |
| `get_quiz` | Get quiz questions | ✅ |
| `submit_quiz` | Submit answers | ❌ |
| `get_progress` | Get learning progress | ✅ |

### Organization Tools (7)
| Tool | Purpose | Read-Only |
|------|---------|-----------|
| `get_bookmarks` | List bookmarks | ✅ |
| `create_bookmark` | Save bookmark | ❌ |
| `delete_bookmark` | Remove bookmark | ❌ |
| `get_notes` | List notes | ✅ |
| `create_note` | Save note | ❌ |
| `update_note` | Update note | ❌ |
| `delete_note` | Remove note | ❌ |

### Premium Tools (1)
| Tool | Purpose | Cost |
|------|---------|------|
| `generate_adaptive_path` | Personalized learning path | ~$0.01 |

### System Tools (2)
| Tool | Purpose |
|------|---------|
| `mcp_server_info` | Server information |
| `get_note_tags` | List note tags |

## System Instructions

```
You are Course Companion FTE, a friendly and encouraging teaching assistant.

Core Rules:
- ALWAYS use tools to get content
- NEVER generate your own explanations
- Call get_chapter() before explaining topics
- Celebrate progress and achievements
- Warn about costs before using premium features
```

## Conversation Starters

- "What chapters can I learn?"
- "Start with Chapter 1"
- "Quiz me on what I've learned"
- "How's my progress?"
- "Search for: neural networks"
- "Show my bookmarks"
- "Create a learning path (Premium)"

## Pricing

**Free Tier:**
- Chapters 1-3
- All quizzes
- Progress tracking
- Bookmarks & notes
- Search

**Premium ($9.99/mo):**
- Chapters 4-6
- AI-powered learning paths
- Advanced topics
- Priority support

## Setup Steps

### 1. Start MCP Server
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Create Cloudflare Tunnel
```bash
npm install -g cloudflared
cloudflared tunnel --url http://localhost:8000
# Get URL: https://your-app.your-subdomain.dev
```

### 3. Create ChatGPT App
- Open ChatGPT → Apps → Create App
- Copy config from `chatgpt-app-config.yaml`
- Test all tools
- Publish

### 4. Test
```bash
# Test backend
curl http://localhost:8000/

# Test MCP server
cd backend
python test_mcp_integration.py
```

## Tool Examples

### Get Chapter Content
```
User: "Tell me about Chapter 1"
→ get_chapter(chapter_id="chapter-1")
→ Presents content from tool
```

### Search Content
```
User: "What are neural networks?"
→ search_content(query="neural networks", limit=5)
→ Presents relevant sections
```

### Quiz
```
User: "Quiz me on Chapter 1"
→ get_quiz(quiz_id="chapter-1")
→ Presents questions
→ submit_quiz(quiz_id="chapter-1", answers={...})
→ Shows score and feedback
```

### Progress
```
User: "How am I doing?"
→ get_progress()
→ Shows completion %, streak, milestones
```

### Premium
```
User: "Create a learning path"
→ "This will cost ~$0.01. Proceed?"
→ generate_adaptive_path(user_id="...", goals=[...])
→ Shows personalized path
```

## Compliance

✅ Zero-Backend-LLM - No LLM calls in backend
✅ Phase 1 Compliant - All free features deterministic
✅ Phase 2 Compliant - Premium features track costs
✅ ChatGPT Reasoning - All AI happens in ChatGPT

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't connect | Check backend running, tunnel active |
| Tool not found | Restart MCP server, verify registration |
| Auth error | Check auth type matches backend |
| 404 errors | Verify /api/v1 prefix in routes |

## Files

- `chatgpt-app/chatgpt-app-config.yaml` - App configuration
- `chatgpt-app/app-manifest.json` - JSON format
- `chatgpt-app/SETUP-GUIDE.md` - Detailed setup
- `backend/mcp_server.py` - MCP server
- `backend/test_mcp_integration.py` - Tests

## Status

✅ MCP Server: Tested and working
✅ App Config: Complete
✅ Tools: 16 registered
✅ Documentation: Complete
⏳ App Creation: Ready to create in ChatGPT

## Next Steps

1. ☐ Setup Cloudflare Tunnel
2. ☐ Create app in ChatGPT interface
3. ☐ Test all tools
4. ☐ Deploy to production
5. ☐ Submit to App Store

---

**Ready to create your ChatGPT App!** 🚀
