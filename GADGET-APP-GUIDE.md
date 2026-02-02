# Gadget App Integration Guide

## Overview

The Course Companion FTE project now includes a Gadget app template for building ChatGPT Apps with MCP (Model Context Protocol) integration. Gadget provides a production-ready platform for hosting ChatGPT Apps with proper OpenAI Apps SDK integration.

## What is Gadget?

Gadget is a full-stack development platform that provides:
- **Built-in MCP Server**: Native support for Model Context Protocol
- **OpenAI Apps SDK Integration**: Proper format and structure for ChatGPT Apps
- **Instant Deployment**: Development and production environments
- **Database & API**: Built-in backend with models, actions, and routes
- **Authentication**: Session management and OAuth support

## Quick Start

### 1. Install Dependencies

```bash
# Install ggt CLI
npm install -g gadget-inc/ggt

# Install yarn (required by Gadget)
npm install -g yarn
```

### 2. Login to Gadget

```bash
npx ggt login
```

This will open a browser window. Log in with your Gadget account.

### 3. Pull the App Files

```bash
# Create directory and pull files
mkdir gadget-app
cd gadget-app
npx ggt pull --app course-companion-fte-1 --env development --force
```

### 4. Start Development Server

```bash
npx ggt dev --app course-companion-fte-1
```

This will start the development server and provide you with:
- **Preview URL**: https://course-companion-fte-1--development.gadget.app
- **Editor URL**: https://course-companion-fte-1.gadget.app/edit/development
- **API Playground**: https://course-companion-fte-1.gadget.app/api/playground/javascript?environment=development

## MCP Endpoint

### Development
```
https://course-companion-fte-1--development.gadget.app/mcp
```

### Production
```
https://course-companion-fte-1.gadget.app/mcp
```

## Testing the MCP Server

### Initialize Connection

```bash
curl -X POST https://course-companion-fte-1--development.gadget.app/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {
        "tools": {}
      },
      "clientInfo": {
        "name": "test",
        "version": "1.0.0"
      }
    }
  }'
```

### List Tools

```bash
curl -X POST https://course-companion-fte-1--development.gadget.app/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

## Project Structure

```
gadget-app/
├── api/
│   ├── mcp.ts                    # MCP server configuration
│   ├── actions/                  # Custom actions
│   ├── models/                   # Database models
│   └── routes/
│       ├── mcp/
│       │   ├── GET.ts           # MCP GET endpoint
│       │   ├── POST.ts          # MCP POST endpoint (JSON-RPC)
│       │   └── +scope.ts        # Route scope configuration
│       └── GET-hello.ts         # Example route
├── web/
│   ├── chatgpt/                  # ChatGPT widget components
│   │   ├── HelloGadget.tsx      # Example widget
│   │   ├── root.tsx
│   │   └── utils/
│   ├── components/               # React components
│   │   ├── ui/                  # UI components
│   │   ├── shared/              # Shared components
│   │   └── public/              # Public components
│   ├── routes/                   # App routes
│   └── assets/                   # Static assets
├── accessControl/
│   └── permissions.gadget.ts     # Permission configuration
├── settings.gadget.ts            # App settings
├── package.json
└── tsconfig.json
```

## Key Files

### `api/mcp.ts`

Defines the MCP server, tools, and resources. This is where you:

1. **Register Tools**: Add your custom tools
2. **Register Resources**: Expose data to ChatGPT
3. **Configure Widgets**: Set up UI components

Example tool registration:

```typescript
mcpServer.registerTool(
  "getChapters",
  {
    title: "Get Course Chapters",
    description: "Retrieve all available course chapters",
    annotations: { readOnlyHint: true },
    _meta: {
      "openai/outputTemplate": "ui://widget/ChaptersList.html",
      "openai/toolBehavior": "interactive",
    },
  },
  async (params) => {
    // Your tool logic here
    const chapters = await api.chapter.findMany();
    return {
      structuredContent: { chapters },
      content: [],
    };
  }
);
```

### `api/routes/mcp/POST.ts`

Handles MCP JSON-RPC requests. Uses `StreamableHTTPServerTransport` for proper OpenAI integration.

### `web/chatgpt/`

Contains ChatGPT widget components that can be rendered in ChatGPT's UI.

## Connecting to ChatGPT

### 1. Use the MCP URL in ChatGPT App Configuration

```
https://course-companion-fte-1--development.gadget.app/mcp
```

### 2. Required Headers

When testing with curl, always include:
```
Accept: application/json, text/event-stream
```

### 3. Authentication

The Gadget app includes built-in session management. The `__getGadgetAuthTokenV1` tool handles authentication for widgets.

## Adding Custom Tools

### Step 1: Define the Tool in `api/mcp.ts`

```typescript
mcpServer.registerTool(
  "yourToolName",
  {
    title: "Your Tool Title",
    description: "What your tool does",
    annotations: {
      readOnlyHint: true,
      openWorldHint: false,
      destructiveHint: false
    },
    _meta: {
      "openai/outputTemplate": "ui://widget/YourWidget.html",
      "openai/toolBehavior": "interactive",
    },
  },
  async (params) => {
    // Access Gadget API
    const api = request.api.actAsSession;

    // Your logic here
    const result = await api.yourModel.findMany();

    return {
      structuredContent: { data: result },
      content: [],
    };
  }
);
```

### Step 2: Create a Widget (Optional)

If you want custom UI in ChatGPT, create a widget in `web/chatgpt/`:

```typescript
// web/chatgpt/YourWidget.tsx
import { useGadget } from "@gadgetinc/react-chatgpt-apps";

export const YourWidget = () => {
  const api = useGadget();

  return (
    <div>
      <h2>Your Widget</h2>
      {/* Your UI here */}
    </div>
  );
};
```

### Step 3: Deploy Changes

```bash
# From gadget-app directory
npx ggt push --app course-companion-fte-1
```

## Database Models

### Accessing Built-in Models

```typescript
// In your tool handler
const api = request.api.actAsSession;

// Find records
const records = await api.yourModel.findMany({
  filter: {
    status: { equals: "active" }
  },
  sort: {
    createdAt: "Descending"
  }
});

// Get single record
const record = await api.yourModel.findOne(id);

// Create record
const newRecord = await api.yourModel.create({
  data: {
    name: "Example",
    status: "active"
  }
});

// Update record
const updated = await api.yourModel.update(id, {
  data: {
    status: "inactive"
  }
});

// Delete record
await api.yourModel.delete(id);
```

## Deployment

### Development Environment

Changes are automatically deployed when you push:

```bash
npx ggt push --app course-companion-fte-1 --env development
```

Access at: `https://course-companion-fte-1--development.gadget.app`

### Production Environment

```bash
npx ggt push --app course-companion-fte-1 --env production
```

Access at: `https://course-companion-fte-1.gadget.app`

## API Playground

Use the built-in API playground to test your backend:

```
https://course-companion-fte-1.gadget.app/api/playground/javascript?environment=development
```

## Environment Variables

Access environment variables in your code:

```typescript
process.env.GADGET_APP_URL  // Your app URL
process.env.NODE_ENV        // development or production
```

## Monitoring & Logs

### View Logs

```bash
npx ggt logs --app course-companion-fte-1 --env development
```

### Check Status

```bash
npx ggt status --app course-companion-fte-1
```

## Common Commands

```bash
# Login
npx ggt login

# List your apps
npx ggt list

# Pull latest files
npx ggt pull --app course-companion-fte-1 --env development

# Push changes
npx ggt push --app course-companion-fte-1 --env development

# Start dev server
npx ggt dev --app course-companion-fte-1

# View logs
npx ggt logs --app course-companion-fte-1 --env development

# Open in browser
npx ggt open --app course-companion-fte-1
```

## ChatGPT App Configuration

When creating a ChatGPT App in ChatGPT:

1. **Name**: Course Companion FTE
2. **Description**: Your course companion with full learning management
3. **MCP Server URL**: `https://course-companion-fte-1.gadget.app/mcp`
4. **Authentication**: No Auth (Gadget handles sessions internally)

## Advantages of Using Gadget

1. ✅ **Proper OpenAI Format**: Uses official `@modelcontextprotocol/sdk`
2. ✅ **StreamableHTTPServerTransport**: Supports both JSON and SSE
3. ✅ **Widget Support**: Render custom UI in ChatGPT
4. ✅ **Built-in Database**: No need for external databases
5. ✅ **Instant Deployment**: Push code, it's live
6. ✅ **Session Management**: Built-in authentication and permissions
7. ✅ **TypeScript**: Full type safety
8. ✅ **Auto-generated Docs**: API playground and documentation

## Next Steps

1. **Explore the Template**: Check out the example `helloGadget` tool
2. **Add Your Tools**: Implement your course companion features
3. **Create Widgets**: Build custom UI components for ChatGPT
4. **Deploy to Production**: Push to production environment
5. **Connect to ChatGPT**: Add the MCP URL to your ChatGPT App

## Resources

- **Gadget Documentation**: https://docs.gadget.dev
- **MCP Specification**: https://modelcontextprotocol.io
- **OpenAI Apps SDK**: https://platform.openai.com/docs/mcp
- **Your App Editor**: https://course-companion-fte-1.gadget.app/edit/development
- **Community**: https://gadget.dev/community
