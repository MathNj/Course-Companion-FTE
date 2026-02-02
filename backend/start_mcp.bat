@echo off
REM Start MCP Server with stdio transport
REM This server can be connected by ChatGPT Apps

echo ====================================
echo Starting MCP Server
echo ====================================
echo.
echo Backend URL: http://localhost:8000
echo MCP Server will communicate via stdio
echo.
echo IMPORTANT: Keep this window open!
echo ChatGPT App will connect to this server.
echo.
echo Press Ctrl+C to stop the server
echo ====================================
echo.

cd /d "%~dp0backend"
python mcp_server.py
