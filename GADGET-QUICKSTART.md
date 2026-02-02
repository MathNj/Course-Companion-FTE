# Gadget App - Simple Guide

## What is this?

Gadget is a platform that makes it easy to build ChatGPT Apps. Think of it like:
- A hosting service for your ChatGPT App
- A database to store your data
- An API server - already set up for you
- A place to build custom UI components

**The best part:** It already works with ChatGPT's MCP protocol - no complicated setup needed!

---

## How to Use It

### Step 1: Install the Tools

Open your terminal and run:

```bash
npm install -g gadget-inc/ggt yarn
```

### Step 2: Login

```bash
npx ggt login
```

This opens your browser. Log in to your Gadget account.

### Step 3: Get the App Files

```bash
mkdir gadget-app
cd gadget-app
npx ggt pull --app course-companion-fte-1 --env development --force
```

### Step 4: Start Coding

```bash
npx ggt dev --app course-companion-fte-1
```

Now your app is running at:
- **Development**: https://course-companion-fte-1--development.gadget.app
- **Editor**: https://course-companion-fte-1.gadget.app/edit/development

---

## Your App's URLs

### Development (for testing)
```
https://course-companion-fte-1--development.gadget.app/mcp
```

### Production (for ChatGPT)
```
https://course-companion-fte-1.gadget.app/mcp
```

---

## File Structure (Where Things Are)

```
gadget-app/
├── api/
│   ├── mcp.ts              ⭐ Add your tools here
│   └── routes/
│       └── mcp/            ⭐ MCP endpoint setup
├── web/
│   └── chatgpt/            ⭐ Build ChatGPT UI components
└── settings.gadget.ts      ⭐ App configuration
```

---

## Adding a New Tool

Open `api/mcp.ts` and add your tool:

```typescript
mcpServer.registerTool(
  "getChapters",                    // Tool name
  {
    title: "Get Course Chapters",
    description: "Shows all chapters",
    annotations: { readOnlyHint: true },
  },
  async (params) => {
    // Get data from Gadget's database
    const chapters = await api.chapter.findMany();

    // Return the data
    return {
      structuredContent: { chapters },
      content: [],
    };
  }
);
```

---

## Making It Work with ChatGPT

### 1. Add Your Tool

Edit `api/mcp.ts` and add your tools (see example above)

### 2. Test It

```bash
# Test that your tool works
curl -X POST https://course-companion-fte-1--development.gadget.app/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

### 3. Deploy It

```bash
npx ggt push --app course-companion-fte-1
```

### 4. Connect to ChatGPT

In ChatGPT, create a new App and use:
- **MCP Server URL**: `https://course-companion-fte-1.gadget.app/mcp`

---

## Database (Storing Data)

Gadget has a built-in database. Here's how to use it:

### Find Things
```typescript
const chapters = await api.chapter.findMany();
const oneChapter = await api.chapter.findOne(123);
```

### Create Things
```typescript
const newChapter = await api.chapter.create({
  data: {
    title: "Chapter 1",
    content: "Introduction..."
  }
});
```

### Update Things
```typescript
await api.chapter.update(123, {
  data: {
    title: "Updated Title"
  }
});
```

### Delete Things
```typescript
await api.chapter.delete(123);
```

---

## Creating Custom UI (Widgets)

You can build custom UI that shows up inside ChatGPT!

### Step 1: Create a Widget

Create `web/chatgpt/MyWidget.tsx`:

```typescript
import { useGadget } from "@gadgetinc/react-chatgpt-apps";

export const MyWidget = () => {
  const api = useGadget();

  return (
    <div style={{ padding: '20px' }}>
      <h2>My Custom Widget</h2>
      <p>This shows up in ChatGPT!</p>
    </div>
  );
};
```

### Step 2: Use It in Your Tool

```typescript
mcpServer.registerTool(
  "showMyWidget",
  {
    title: "Show My Widget",
    _meta: {
      "openai/outputTemplate": "ui://widget/MyWidget.html",
    },
  },
  async (params) => {
    return {
      structuredContent: { message: "Loading widget..." },
      content: [],
    };
  }
);
```

---

## Common Commands

```bash
# Start the dev server
npx ggt dev --app course-companion-fte-1

# Save your changes
npx ggt push --app course-companion-fte-1

# Get the latest files
npx ggt pull --app course-companion-fte-1

# See what's changed
npx ggt status --app course-companion-fte-1

# View logs
npx ggt logs --app course-companion-fte-1

# Open in browser
npx ggt open --app course-companion-fte-1
```

---

## Quick Reference

| What You Want to Do | Where to Go |
|---------------------|-------------|
| Add a new tool | `api/mcp.ts` |
| Create UI for ChatGPT | `web/chatgpt/` |
| Configure the app | `settings.gadget.ts` |
| Change permissions | `accessControl/permissions.gadget.ts` |
| Test the API | Use the API Playground link from `npx ggt dev` |

---

## Why Use Gadget?

✅ **It Just Works** - No need to set up servers, databases, or APIs
✅ **ChatGPT Ready** - Already has the correct format for ChatGPT Apps
✅ **Fast Development** - Push code and it's live instantly
✅ **Built-in Database** - Store your data without any setup
✅ **Custom UI** - Build widgets that show up inside ChatGPT
✅ **TypeScript** - Get autocomplete and catch errors early

---

## Need Help?

- **Gadget Docs**: https://docs.gadget.dev
- **Your App Editor**: https://course-companion-fte-1.gadget.app/edit/development
- **API Playground**: https://course-companion-fte-1.gadget.app/api/playground/javascript

---

## Example: Complete Tool

Here's a complete example of a tool that gets course chapters:

```typescript
// In api/mcp.ts

mcpServer.registerTool(
  "getChapters",
  {
    title: "Get Course Chapters",
    description: "Get all available chapters with progress",
    annotations: {
      readOnlyHint: true,      // This only reads data
      destructiveHint: false,   // Doesn't delete anything
    },
  },
  async (params) => {
    // Use Gadget's API (already authenticated)
    const api = request.api.actAsSession;

    // Get chapters from database
    const chapters = await api.chapter.findMany({
      filter: {
        published: { equals: true }
      },
      sort: {
        order: "Ascending"
      }
    });

    // Return to ChatGPT
    return {
      structuredContent: {
        chapters: chapters.map(ch => ({
          id: ch.id,
          title: ch.title,
          description: ch.description,
          order: ch.order
        }))
      },
      content: [],
    };
  }
);
```

That's it! When you save and push, ChatGPT can call this tool.

---

## What's Next?

1. ✅ You have the Gadget app set up
2. ✅ The MCP server is working
3. 📝 Add your Course Companion tools
4. 🚨 Create widgets for ChatGPT UI
5. 🚀 Deploy to production
6. 🤖 Connect to ChatGPT

**Ready to build?** Start editing `api/mcp.ts` and add your tools!
