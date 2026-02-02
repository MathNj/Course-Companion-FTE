@echo off
REM Deploy Cloudflare Worker using Wrangler CLI
REM This script automates the deployment process

echo ====================================
echo Cloudflare Worker Deployment Script
echo ====================================
echo.

REM Check if wrangler is installed
where wrangler >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Wrangler CLI is not installed.
    echo Installing Wrangler...
    npm install -g wrangler
    echo.
)

echo Step 1: Login to Cloudflare
echo ----------------------------
echo Please login to your Cloudflare account:
echo.
call wrangler login

echo.
echo Step 2: Deploy Worker
echo -----------------------
echo Deploying MCP Proxy Worker...
echo.

cd /d "%~dp0cloudflare-worker"

REM Create wrangler.toml if it doesn't exist
if not exist wrangler.toml (
    echo name = "course-companion-mcp-proxy" > wrangler.toml
    echo main = "mcp-proxy-worker.js" >> wrangler.toml
    echo compatibility_date = "2024-01-01" >> wrangler.toml
    echo.
    echo Created wrangler.toml configuration
)

REM Deploy the worker
call wrangler deploy

echo.
echo ====================================
echo Deployment Complete!
echo ====================================
echo.
echo Your Worker URL will be shown above.
echo Copy it and update your ChatGPT App configuration.
echo.
pause
