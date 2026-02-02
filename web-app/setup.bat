@echo off
REM Course Companion Web App - Setup Script for Windows

echo ==================================
echo Course Companion Web App - Setup
echo ==================================
echo.

REM Check Node.js version
echo [1/3] Checking Node.js version...
node -v >nul 2>&1
if errorlevel 1 (
    echo X Node.js is not installed. Please install Node.js 20+ from https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
echo OK Node.js version: %NODE_VERSION%
echo.

REM Check npm
echo [2/3] Checking npm...
npm -v >nul 2>&1
if errorlevel 1 (
    echo X npm is not installed. Please install npm.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm -v') do set NPM_VERSION=%%i
echo OK npm version: %NPM_VERSION%
echo.

REM Install dependencies
echo [3/3] Installing dependencies...
call npm install
if errorlevel 1 (
    echo X Failed to install dependencies
    pause
    exit /b 1
)

echo OK Dependencies installed
echo.

REM Create environment file
if not exist .env.local (
    echo Creating .env.local file...
    copy .env.local.example .env.local >nul
    echo OK Created .env.local
    echo.
    echo WARNING: Please edit .env.local and set NEXT_PUBLIC_API_URL to your backend URL
    echo         Default: http://localhost:8000
    echo.
) else (
    echo OK .env.local already exists
    echo.
)

REM Create public directory
if not exist public mkdir public

echo ==================================
echo Setup complete!
echo ==================================
echo.
echo Next steps:
echo.
echo 1. Edit .env.local to configure your API URL
echo 2. Make sure your backend is running (Phase 1 + 2)
echo 3. Start the development server:
echo.
echo    npm run dev
echo.
echo 4. Open http://localhost:3000 in your browser
echo.
echo For more information, see README.md
echo.
pause
