"""
Run MCP Server on separate port

This script starts the MCP server on port 8001 so it can be accessed
via Cloudflare Tunnel alongside the main FastAPI backend.
"""

import asyncio
import sys
from mcp_server import mcp

# MCP Server Configuration
MCP_HOST = "localhost"
MCP_PORT = 8001

async def main():
    """Run the MCP server using stdio transport."""
    print(f"Starting MCP Server on {MCP_HOST}:{MCP_PORT}...")
    print(f"MCP Server will be available at: http://{MCP_HOST}:{MCP_PORT}")
    print(f"\nFor Cloudflare Tunnel, use: http://localhost:8001")
    print(f"Or use SSE transport at: http://localhost:8001/sse")
    print("\n" + "="*60)
    print("IMPORTANT: For ChatGPT App integration")
    print("="*60)
    print("The MCP server uses stdio transport by default.")
    print("For ChatGPT Apps, you need to:")
    print("1. Keep this server running")
    print("2. Update Cloudflare Tunnel to: http://localhost:8001")
    print("3. Or use the SSE endpoint: http://localhost:8001/sse")
    print("="*60 + "\n")

    # Run MCP server with stdio (standard for MCP)
    # ChatGPT Apps will connect via MCP protocol
    await mcp.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nMCP Server stopped.")
        sys.exit(0)
