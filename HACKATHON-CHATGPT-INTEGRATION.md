# Hackathon Learn Flow - OpenAI Apps SDK Integration Guide

## Overview

This guide shows you how to integrate ChatGPT with your Course Companion FTE platform for an amazing hackathon learning experience!

## What You'll Build

A **ChatGPT App** that helps hackers:
1. **Learn course content** interactively
2. **Take quizzes** with AI assistance
3. **Track progress** in real-time
4. **Get personalized recommendations**
5. **Access notes and bookmarks** through ChatGPT

---

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   ChatGPT       │─────▶│  Gadget App      │─────▶│  Backend API    │
│   (User Interface)│      │  (MCP Server)    │      │  (PostgreSQL)    │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  ▼
                          ┌──────────────────┐
                          │  Your Frontend   │
                          │  (Dashboard)     │
                          └──────────────────┘
```

**How it works:**
1. User interacts with ChatGPT
2. ChatGPT calls your MCP tools via Gadget
3. Gadget fetches data from your backend
4. User sees results in ChatGPT

---

## Step-by-Step Integration

### Step 1: Add Your Tools to Gadget

Open `gadget-app/api/mcp.ts` and add your course tools:

```typescript
// In gadget-app/api/mcp.ts

// 1. Get Chapters Tool
mcpServer.registerTool(
  "getChapters",
  {
    title: "Get Course Chapters",
    description: "Get all available course chapters with progress",
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      openWorldHint: false
    },
  },
  async (params) => {
    const api = request.api.actAsSession;

    // Fetch from your backend
    const response = await fetch(
      'http://localhost:8001/api/v1/chapters',
      {
        headers: {
          'Authorization': request.headers['authorization'] || ''
        }
      }
    );

    const chapters = await response.json();

    return {
      structuredContent: { chapters },
      content: [],
    };
  }
);

// 2. Get Chapter Content Tool
mcpServer.registerTool(
  "getChapter",
  {
    title: "Get Chapter Content",
    description: "Get full chapter content including all sections",
    annotations: { readOnlyHint: true },
  },
  async (params) => {
    const { chapterId } = params.arguments;
    const api = request.api.actAsSession;

    const response = await fetch(
      `http://localhost:8001/api/v1/chapters/${chapterId}`,
      {
        headers: {
          'Authorization': request.headers['authorization'] || ''
        }
      }
    );

    const chapter = await response.json();

    return {
      structuredContent: { chapter },
      content: [],
    };
  }
);

// 3. Get Quiz Tool
mcpServer.registerTool(
  "getQuiz",
  {
    title: "Get Chapter Quiz",
    description: "Get quiz questions for a chapter",
    annotations: { readOnlyHint: true },
  },
  async (params) => {
    const { chapterId } = params.arguments;
    const api = request.api.actAsSession;

    const response = await fetch(
      `http://localhost:8001/api/v1/quizzes/${chapterId}`,
      {
        headers: {
          'Authorization': request.headers['authorization'] || ''
        }
      }
    );

    const quiz = await response.json();

    return {
      structuredContent: { quiz },
      content: [],
    };
  }
);

// 4. Submit Quiz Tool
mcpServer.registerTool(
  "submitQuiz",
  {
    title: "Submit Quiz Answers",
    description: "Submit quiz answers for grading",
    annotations: {
      readOnlyHint: false,
      destructiveHint: false
    },
  },
  async (params) => {
    const { quizId, answers } = params.arguments;
    const api = request.api.actAsSession;

    const response = await fetch(
      `http://localhost:8001/api/v1/quizzes/${quizId}/submit`,
      {
        method: 'POST',
        headers: {
          'Authorization': request.headers['authorization'] || '',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(answers)
      }
    );

    const result = await response.json();

    return {
      structuredContent: { result },
      content: [],
    };
  }
);

// 5. Get Progress Tool
mcpServer.registerTool(
  "getProgress",
  {
    title: "Get Learning Progress",
    description: "Get comprehensive learning progress and stats",
    annotations: { readOnlyHint: true },
  },
  async (params) => {
    const api = request.api.actAsSession;

    const response = await fetch(
      'http://localhost:8001/api/v1/progress',
      {
        headers: {
          'Authorization': request.headers['authorization'] || ''
        }
      }
    );

    const progress = await response.json();

    return {
      structuredContent: { progress },
      content: [],
    };
  }
);

// 6. Search Content Tool
mcpServer.registerTool(
  "searchContent",
  {
    title: "Search Course Content",
    description: "Search across all course content for specific topics",
    annotations: { readOnlyHint: true },
  },
  async (params) => {
    const { query, limit = 5 } = params.arguments;
    const api = request.api.actAsSession;

    const response = await fetch(
      `http://localhost:8001/api/v1/chapters/search?q=${encodeURIComponent(query)}&limit=${limit}`,
      {
        headers: {
          'Authorization': request.headers['authorization'] || ''
        }
      }
    );

    const results = await response.json();

    return {
      structuredContent: { results },
      content: [],
    };
  }
);
```

### Step 2: Handle Authentication

The Gadget app needs to pass authentication tokens to your backend. Update the tools to handle this:

```typescript
// In gadget-app/api/mcp.ts

// Get token from request
const getAuthToken = (request: FastifyRequest) => {
  const authHeader = request.headers['authorization'];
  if (!authHeader) return null;

  // For development, you might use a fixed token
  // For production, use the session token
  return authHeader; // Returns "Bearer <token>"
};

// Use in your tools
const response = await fetch(
  'http://localhost:8001/api/v1/chapters',
  {
    headers: {
      'Authorization': getAuthToken(request) || 'Bearer dev-token'
    }
  }
);
```

### Step 3: Deploy to Gadget

```bash
# From gadget-app directory
npx ggt push --app course-companion-fte-1 --env production
```

This will deploy your MCP tools to production at:
```
https://course-companion-fte-1.gadget.app/mcp
```

### Step 4: Create ChatGPT App

1. Go to ChatGPT
2. Create a new App
3. Configure:
   - **Name**: Hackathon Learning Assistant
   - **Description**: Your AI-powered learning companion for the hackathon
   - **MCP Server URL**: `https://course-companion-fte-1.gadget.app/mcp`
   - **Instructions**:
   ```
   You are a helpful learning assistant for a hackathon course.
   Help learners:
   - Navigate course content
   - Understand chapter material
   - Practice with quizzes
   - Track their progress
   - Find relevant information quickly

   Always be encouraging and break down complex topics.
   ```

### Step 5: Test in ChatGPT

Once connected, try these conversations:

**Example 1: Browse Chapters**
```
You: What chapters are available?
ChatGPT: Let me check the course chapters...
[Uses getChapters tool]
ChatGPT: I found 6 chapters:
1. Introduction to GenAI
2. Large Language Models
3. Prompt Engineering
...
```

**Example 2: Study a Chapter**
```
You: Help me study Chapter 1
ChatGPT: Let me get the content for Chapter 1...
[Uses getChapter tool]
ChatGPT: Great! Chapter 1 covers "Introduction to GenAI".
Here's what you'll learn...
```

**Example 3: Take a Quiz**
```
You: Give me a quiz for Chapter 1
ChatGPT: I'll fetch the quiz for Chapter 1...
[Uses getQuiz tool]
ChatGPT: Here are the questions:
1. What is Generative AI?
...
```

**Example 4: Check Progress**
```
You: How am I doing in the course?
ChatGPT: Let me check your progress...
[Uses getProgress tool]
ChatGPT: Great progress! You've completed 2/6 chapters (33%).
Your streak is 7 days. Keep it up!
```

---

## Advanced: Add Custom Widgets

Create interactive UI that shows up in ChatGPT!

### Create a Progress Widget

```typescript
// In web/chatgpt/ProgressWidget.tsx
import { useGadget } from "@gadgetinc/react-chatgpt-apps";

export const ProgressWidget = () => {
  const api = useGadget();
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    // Fetch progress from Gadget backend
    api.progress.get().then(setProgress);
  }, [api]);

  if (!progress) return <div>Loading...</div>;

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>📊 Your Progress</h2>
      <div style={{
        background: '#f0f0f0',
        borderRadius: '10px',
        padding: '15px',
        margin: '10px 0'
      }}>
        <p><strong>Chapters Completed:</strong> {progress.chapters_completed}/{progress.total_chapters}</p>
        <p><strong>Completion:</strong> {progress.completion_percentage}%</p>
        <p><strong>Current Streak:</strong> 🔥 {progress.current_streak} days</p>
      </div>

      {/* Progress bar */}
      <div style={{
        width: '100%',
        height: '20px',
        background: '#e0e0e0',
        borderRadius: '10px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${progress.completion_percentage}%`,
          height: '100%',
          background: 'linear-gradient(90deg, #4CAF50, #8BC34A)',
          transition: 'width 0.3s'
        }} />
      </div>
    </div>
  );
};
```

### Use the Widget in a Tool

```typescript
// In api/mcp.ts
mcpServer.registerTool(
  "showProgress",
  {
    title: "Show Progress Dashboard",
    description: "Display your learning progress",
    _meta: {
      "openai/outputTemplate": "ui://widget/ProgressWidget.html",
      "openai/toolBehavior": "interactive",
    },
  },
  async (params) => {
    return {
      structuredContent: { message: "Loading your progress..." },
      content: [],
    };
  }
);
```

Now when users ask "Show my progress", they'll see a beautiful interactive widget right in ChatGPT!

---

## Hackathon Use Cases

### 1. Quick Learning Sprints
```
Hacker: "I have 30 minutes. What should I learn?"
ChatGPT: [Checks progress] "Based on your progress, I recommend
completing Chapter 3: Prompt Engineering. You're 50% through it.
Want me to get the content?"
```

### 2. Pre-Hackathon Prep
```
Hacker: "What do I need to know for the hackathon?"
ChatGPT: [Searches content] "Here are the key topics:
- Prompt engineering patterns
- LLM capabilities
- API integration
...
Want me to create a study plan?"
```

### 3. During the Hackathon
```
Hacker: "How do I integrate with the OpenAI API?"
ChatGPT: [Searches and finds relevant section] "I found the answer
in Chapter 4. Here's how to set up the API integration..."
```

### 4. Quick Quizzes
```
Hacker: "Quiz me on Chapter 2"
ChatGPT: [Gets quiz] "Here's a quick quiz:
1. What are the three main types of LLMs?
...
[After hacker answers]
Great! You got 4/5 correct. Want me to explain the answer you missed?"
```

### 5. Progress Tracking
```
Hacker: "Am I on track for the hackathon?"
ChatGPT: [Checks progress] "You're doing well! You've completed
4/6 chapters and have a 7-day streak. At this pace, you'll finish
2 days before the hackathon. Keep it up! 🔥"
```

---

## Production Checklist

### Before the Hackathon:

- [ ] Deploy Gadget app to production
- [ ] Test all MCP tools with curl
- [ ] Create ChatGPT App with production URL
- [ ] Write clear instructions for the App
- [ ] Test authentication flow
- [ ] Create widgets for better UX
- [ ] Test with sample users
- [ ] Document common use cases

### Day of Hackathon:

- [ ] Share ChatGPT App URL with participants
- [ ] Provide quick start guide
- [ ] Monitor for issues
- [ ] Have backup plan ready

---

## Troubleshooting

### "Not Authenticated" Error

**Problem:** Tools return 401 Unauthorized

**Solution:**
1. Check that Gadget is passing auth token
2. Verify token format: `Bearer <token>`
3. Check backend CORS settings

### Tools Not Showing in ChatGPT

**Problem:** ChatGPT doesn't use your tools

**Solution:**
1. Make sure tool descriptions are clear
2. Check tool annotations are correct
3. Verify MCP server is responding
4. Test with curl first

### Slow Responses

**Problem:** ChatGPT takes too long to respond

**Solution:**
1. Check backend response times
2. Add caching in Gadget
3. Optimize database queries
4. Use CDN for static content

---

## Next Steps

1. ✅ **Test the tools** - Use curl to verify each tool works
2. ✅ **Deploy to Gadget** - Push to production
3. ✅ **Create ChatGPT App** - Configure with production URL
4. ✅ **Test with users** - Get feedback before hackathon
5. ✅ **Monitor usage** - See which tools are most popular

---

## Resources

- **Your Gadget App**: https://course-companion-fte-1.gadget.app/edit/development
- **Gadget Documentation**: https://docs.gadget.dev
- **OpenAI Apps SDK**: https://platform.openai.com/docs/mcp
- **Quick Start Guide**: `GADGET-QUICKSTART.md`

---

## Support

If you run into issues:
1. Check the Gadget logs: `npx ggt logs --app course-companion-fte-1`
2. Test tools with curl (see examples above)
3. Check backend logs for authentication errors
4. Verify the MCP server is accessible

Good luck with your hackathon! 🚀
