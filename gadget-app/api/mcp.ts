import { getWidgets } from "vite-plugin-chatgpt-widgets";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { FastifyRequest } from "fastify";
import path from "path";
import { getViteHandle } from "gadget-server/vite";

/**
 * Create MCP server to be used by external clients
 *
 */
export const createMCPServer = async (request: FastifyRequest) => {
  const mcpServer = new McpServer({
    name: "course-companion-fte",
    version: "2.0.0",
  });

  // use actAsSession to access the API client with the permissions of the current session
  const api = request.api.actAsSession;
  const logger = request.logger;

  // get a handle to either the vite dev server in development or the manifest path in production
  const viteHandle = await getViteHandle(request.server);

  // Get the HTML snippet for each widget
  const widgets = await getWidgets("web/chatgpt", viteHandle);

  // Register each widget's HTML snippet as a resource for exposure to ChatGPT
  for (const widget of widgets) {
    const resourceName = `widget-${widget.name.toLowerCase()}`;
    const resourceUri = `ui://widget/${widget.name}.html`;

    mcpServer.registerResource(
      resourceName,
      resourceUri,
      {
        title: widget.name,
        description: `ChatGPT widget for ${widget.name}`,
      },
      async () => {
        return {
          contents: [
            {
              uri: resourceUri,
              mimeType: "text/html+skybridge",
              text: widget.content,
              _meta: getResourceMeta(),
            },
          ],
        };
      }
    );
  }

  // Course Companion FTE Tools

  // Get all chapters
  mcpServer.registerTool(
    "get_chapters",
    {
      title: "Get Chapters",
      description: "Get all available course chapters with access status and progress",
      annotations: { readOnlyHint: true },
    },
    async (params) => {
      try {
        // Use production backend (public endpoint, no auth required)
        const response = await fetch("https://course-companion-fte.fly.dev/api/v1/chapters", {
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Backend returned ${response.status}: ${errorText}`);
        }

        const chapters = await response.json();

        return {
          structuredContent: { chapters },
          content: [{ type: "text", text: JSON.stringify(chapters, null, 2) }],
        };
      } catch (error) {
        logger.error("Error fetching chapters:", error);
        return {
          structuredContent: { error: error.message },
          content: [{ type: "text", text: `Error: ${error.message}` }],
        };
      }
    }
  );

  // Get specific chapter
  mcpServer.registerTool(
    "get_chapter",
    {
      title: "Get Chapter",
      description: "Get full chapter content including all sections",
      annotations: { readOnlyHint: true },
    },
    async (params) => {
      const { chapter_id } = params.args || {};
      if (!chapter_id) {
        return {
          structuredContent: { error: "chapter_id is required" },
          content: [{ type: "text", text: "Error: chapter_id is required" }],
        };
      }

      try {
        const response = await fetch(`https://course-companion-fte.fly.dev/api/v1/chapters/${chapter_id}`, {
          headers: {
            "Content-Type": "application/json",
          },
        });
        const chapter = await response.json();

        return {
          structuredContent: { chapter },
          content: [{ type: "text", text: JSON.stringify(chapter, null, 2) }],
        };
      } catch (error) {
        logger.error("Error fetching chapter:", error);
        return {
          structuredContent: { error: error.message },
          content: [{ type: "text", text: `Error: ${error.message}` }],
        };
      }
    }
  );

  // Search content
  mcpServer.registerTool(
    "search_content",
    {
      title: "Search Content",
      description: "Search course content for relevant sections",
      annotations: { readOnlyHint: true },
    },
    async (params) => {
      const { query, limit = 5 } = params.args || {};
      if (!query) {
        return {
          structuredContent: { error: "query is required" },
          content: [{ type: "text", text: "Error: query is required" }],
        };
      }

      try {
        const response = await fetch(
          `https://course-companion-fte.fly.dev/api/v1/chapters/search?query=${encodeURIComponent(query)}&limit=${limit}`,
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        const results = await response.json();

        return {
          structuredContent: { results },
          content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
        };
      } catch (error) {
        logger.error("Error searching content:", error);
        return {
          structuredContent: { error: error.message },
          content: [{ type: "text", text: `Error: ${error.message}` }],
        };
      }
    }
  );

  // Get quiz
  mcpServer.registerTool(
    "get_quiz",
    {
      title: "Get Quiz",
      description: "Get quiz questions for a chapter",
      annotations: { readOnlyHint: true },
    },
    async (params) => {
      const { quiz_id } = params.args || {};
      if (!quiz_id) {
        return {
          structuredContent: { error: "quiz_id is required" },
          content: [{ type: "text", text: "Error: quiz_id is required" }],
        };
      }

      try {
        const response = await fetch(`https://course-companion-fte.fly.dev/api/v1/quizzes/${quiz_id}`, {
          headers: {
            "Content-Type": "application/json",
          },
        });
        const quiz = await response.json();

        return {
          structuredContent: { quiz },
          content: [{ type: "text", text: JSON.stringify(quiz, null, 2) }],
        };
      } catch (error) {
        logger.error("Error fetching quiz:", error);
        return {
          structuredContent: { error: error.message },
          content: [{ type: "text", text: `Error: ${error.message}` }],
        };
      }
    }
  );

  // Get progress
  mcpServer.registerTool(
    "get_progress",
    {
      title: "Get Progress",
      description: "Get comprehensive learning progress and completion status",
      annotations: { readOnlyHint: true },
    },
    async (params) => {
      try {
        const response = await fetch("https://course-companion-fte.fly.dev/api/v1/progress", {
          headers: {
            "Content-Type": "application/json",
          },
        });
        const progress = await response.json();

        return {
          structuredContent: { progress },
          content: [{ type: "text", text: JSON.stringify(progress, null, 2) }],
        };
      } catch (error) {
        logger.error("Error fetching progress:", error);
        return {
          structuredContent: { error: error.message },
          content: [{ type: "text", text: `Error: ${error.message}` }],
        };
      }
    }
  );

  // Get next chapter (Navigation)
  mcpServer.registerTool(
    "get_next_chapter",
    {
      title: "Get Next Chapter",
      description: "Get the next chapter in the learning sequence based on current progress",
      annotations: { readOnlyHint: true },
    },
    async (params) => {
      const { current_chapter_id } = params.args || {};

      try {
        const response = await fetch(
          `https://course-companion-fte.fly.dev/api/v1/chapters/${current_chapter_id}/next`,
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        const result = await response.json();

        return {
          structuredContent: { next_chapter: result },
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (error) {
        logger.error("Error getting next chapter:", error);
        return {
          structuredContent: { error: error.message },
          content: [{ type: "text", text: `Error: ${error.message}` }],
        };
      }
    }
  );

  // Get previous chapter (Navigation)
  mcpServer.registerTool(
    "get_previous_chapter",
    {
      title: "Get Previous Chapter",
      description: "Get the previous chapter in the learning sequence",
      annotations: { readOnlyHint: true },
    },
    async (params) => {
      const { current_chapter_id } = params.args || {};

      try {
        const response = await fetch(
          `https://course-companion-fte.fly.dev/api/v1/chapters/${current_chapter_id}/previous`,
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        const result = await response.json();

        return {
          structuredContent: { previous_chapter: result },
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (error) {
        logger.error("Error getting previous chapter:", error);
        return {
          structuredContent: { error: error.message },
          content: [{ type: "text", text: `Error: ${error.message}` }],
        };
      }
    }
  );

  // Submit quiz (Rule-Based Quizzes)
  mcpServer.registerTool(
    "submit_quiz",
    {
      title: "Submit Quiz",
      description: "Submit quiz answers for rule-based grading and immediate feedback",
      annotations: {
        readOnlyHint: false,
        destructiveHint: false
      },
    },
    async (params) => {
      const { quiz_id, answers } = params.args || {};

      if (!quiz_id || !answers) {
        return {
          structuredContent: { error: "quiz_id and answers are required" },
          content: [{ type: "text", text: "Error: quiz_id and answers are required" }],
        };
      }

      try {
        const response = await fetch(
          `https://course-companion-fte.fly.dev/api/v1/quizzes/${quiz_id}/submit`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(answers),
          }
        );
        const result = await response.json();

        return {
          structuredContent: { quiz_result: result },
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (error) {
        logger.error("Error submitting quiz:", error);
        return {
          structuredContent: { error: error.message },
          content: [{ type: "text", text: `Error: ${error.message}` }],
        };
      }
    }
  );

  // Update progress (Progress Tracking)
  mcpServer.registerTool(
    "update_progress",
    {
      title: "Update Progress",
      description: "Update learning progress, mark chapter as complete, or track activity",
      annotations: {
        readOnlyHint: false,
        destructiveHint: false
      },
    },
    async (params) => {
      const { chapter_id, activity_type } = params.args || {};

      try {
        const response = await fetch(
          "https://course-companion-fte.fly.dev/api/v1/progress/activity",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              chapter_id,
              activity_type: activity_type || "view"
            }),
          }
        );
        const result = await response.json();

        return {
          structuredContent: { progress_updated: result },
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (error) {
        logger.error("Error updating progress:", error);
        return {
          structuredContent: { error: error.message },
          content: [{ type: "text", text: `Error: ${error.message}` }],
        };
      }
    }
  );

  // Check access (Freemium Gate)
  mcpServer.registerTool(
    "check_access",
    {
      title: "Check Access",
      description: "Check if user has access to premium content or features (freemium gate)",
      annotations: { readOnlyHint: true },
    },
    async (params) => {
      try {
        const response = await fetch("https://course-companion-fte.fly.dev/api/v2/access/check", {
          headers: {
            "Content-Type": "application/json",
          },
        });
        const result = await response.json();

        return {
          structuredContent: { access: result },
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (error) {
        logger.error("Error checking access:", error);
        return {
          structuredContent: { error: error.message },
          content: [{ type: "text", text: `Error: ${error.message}` }],
        };
      }
    }
  );

  // power the @gadgetinc/react-chatgpt-apps Provider to make auth'd requests from widgets using the 'api' client
  mcpServer.registerTool(
    "__getGadgetAuthTokenV1",
    {
      title: "Get the gadget auth token",
      description:
        "Gets the gadget auth token. Should never be called by LLMs or ChatGPT -- only used for internal auth machinery.",
      _meta: {
        // ensure widgets can invoke this tool to get the token
        "openai/widgetAccessible": true,
      },
    },
    async () => {
      if (!request.headers["authorization"]) {
        return {
          structuredContent: { token: null },
          content: [],
        };
      }

      const [scheme, token] = request.headers["authorization"].split(" ", 2);
      if (scheme !== "Bearer") {
        return {
          structuredContent: { error: "incorrect token scheme", token: null },
          content: [],
        };
      }

      return {
        structuredContent: { token, scheme },
        content: [],
      };
    }
  );

  return mcpServer;
};

type ResourceMeta = {
  "openai/widgetPrefersBorder": boolean;
  "openai/widgetDomain": string;
  "openai/widgetCSP"?: {
    connect_domains: string[];
    resource_domains: string[];
  };
};

const getResourceMeta = () => {
  const _meta: ResourceMeta = {
    "openai/widgetPrefersBorder": true,
    "openai/widgetDomain": process.env.GADGET_APP_URL!,
  };

  if (process.env.NODE_ENV == "production") {
    _meta["openai/widgetCSP"] = {
      // Maps to `connect-src` rule in the iframe CSP
      connect_domains: [process.env.GADGET_APP_URL!],
      // Maps to style-src, style-src-elem, img-src, font-src, media-src etc. in the iframe CSP
      resource_domains: [process.env.GADGET_APP_URL!, "https://assets.gadget.dev", "https://app-assets.gadget.dev"],
    };
  }

  return _meta;
};