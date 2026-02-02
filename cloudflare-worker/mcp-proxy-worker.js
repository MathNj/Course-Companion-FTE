/**
 * Cloudflare Worker for MCP Server SSE Proxy
 *
 * This worker properly proxies Server-Sent Events (SSE) connections
 * from ChatGPT Apps to your local MCP server.
 *
 * Deployment:
 * 1. Go to https://dash.cloudflare.com
 * 2. Navigate to Workers & Pages
 * 3. Create new Worker
 * 4. Paste this code
 * 5. Deploy
 * 6. Add custom domain or use worker URL
 */

// Your local MCP server URL (when using Cloudflare Tunnel)
// Or use localhost with cloudflared
const MCP_SERVER_URL = "https://course-companion-mcp.fly.dev";

// CORS headers for ChatGPT Apps
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-ID",
};

export default {
  async fetch(request, env, ctx) {
    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    console.log(`[${request.method}] ${path}`);

    // Handle OAuth config discovery (ChatGPT Apps checks this)
    if (path === "/.well-known/oauth-authorization-server" ||
        path.includes("/oauth_config") ||
        path.includes("/oauth")) {
      return new Response(JSON.stringify({
        issuer: url.origin,
        authorization_endpoint: `${url.origin}/oauth/authorize`,
        token_endpoint: `${url.origin}/oauth/token`,
        response_types_supported: ["code"],
        grant_types_supported: ["authorization_code"],
        token_endpoint_auth_methods_supported: ["none"],
        scopes_supported: ["openid", "profile", "email"]
      }), {
        status: 200,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json"
        }
      });
    }

    try {
      // Root endpoint - return server info (like test server)
      if (path === "/") {
        return new Response(JSON.stringify({
          status: "Course Companion FTE MCP Server",
          version: "2.0.0",
          endpoints: {
            "/mcp": "MCP JSON-RPC endpoint",
            "/sse": "SSE endpoint (alternative)",
            "/messages": "JSON-RPC POST endpoint"
          }
        }), {
          status: 200,
          headers: {
            ...corsHeaders,
            "Content-Type": "application/json"
          }
        });
      }

      // MCP endpoint - POST for JSON-RPC (primary method like test server)
      if (path === "/mcp") {
        return handleProxy(request, path);
      }

      // SSE endpoint - special handling (with and without trailing slash)
      if (path === "/sse" || path === "/sse/" || path.startsWith("/sse")) {
        return handleSSE(request);
      }

      // All other endpoints - standard proxy
      return handleProxy(request, path);
    } catch (error) {
      console.error("Error:", error);
      return new Response(
        JSON.stringify({
          error: "Internal Server Error",
          message: error.message
        }),
        {
          status: 500,
          headers: {
            ...corsHeaders,
            "Content-Type": "application/json"
          }
        }
      );
    }
  }
};

/**
 * Handle SSE connections with proper streaming
 */
async function handleSSE(request) {
  // Forward the SSE request to your MCP server
  const targetUrl = `${MCP_SERVER_URL}/sse/`;

  // Create a new request with proper headers for SSE
  const sseRequest = new Request(targetUrl, {
    method: "GET",
    headers: {
      "Accept": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "User-Agent": request.headers.get("User-Agent") || "cloudflare-worker",
    },
  });

  try {
    // Fetch from MCP server
    const response = await fetch(sseRequest);

    // Create a readable stream from the response
    const { readable, writable } = new TransformStream();

    // Pipe the SSE data through
    response.body.pipeTo(writable);

    // Return SSE response with proper headers
    return new Response(readable, {
      status: 200,
      headers: {
        ...corsHeaders,
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no", // Disable buffering
      },
    });
  } catch (error) {
    console.error("SSE Error:", error);
    return new Response(
      `event: error\ndata: ${JSON.stringify({ error: error.message })}\n\n`,
      {
        status: 500,
        headers: {
          ...corsHeaders,
          "Content-Type": "text/event-stream",
        },
      }
    );
  }
}

/**
 * Handle regular proxy requests (POST to /messages, etc.)
 */
async function handleProxy(request, path) {
  const targetUrl = `${MCP_SERVER_URL}${path}`;

  // Copy the original request
  const proxyRequest = new Request(targetUrl, request);

  // Add CORS headers
  const response = await fetch(proxyRequest);

  // Clone the response and add CORS headers
  const modifiedResponse = new Response(response.body, response);
  Object.entries(corsHeaders).forEach(([key, value]) => {
    modifiedResponse.headers.set(key, value);
  });

  return modifiedResponse;
}
