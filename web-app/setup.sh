#!/bin/bash

# Course Companion Web App - Setup Script
# This script helps you get started with the Phase 3 web application

echo "🚀 Course Companion Web App - Setup"
echo "=================================="
echo ""

# Check Node.js version
echo "📦 Checking Node.js version..."
NODE_VERSION=$(node -v 2>/dev/null)
if [ -z "$NODE_VERSION" ]; then
    echo "❌ Node.js is not installed. Please install Node.js 20+ from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $NODE_VERSION"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ npm version: $(npm -v)"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Create environment file
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local file..."
    cp .env.local.example .env.local
    echo "✅ Created .env.local"
    echo ""
    echo "⚠️  Please edit .env.local and set NEXT_PUBLIC_API_URL to your backend URL"
    echo "   Default: http://localhost:8000"
    echo ""
else
    echo "✅ .env.local already exists"
    echo ""
fi

# Create public directory if it doesn't exist
mkdir -p public

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo ""
echo "1. Edit .env.local to configure your API URL"
echo "2. Make sure your backend is running (Phase 1 + 2)"
echo "3. Start the development server:"
echo ""
echo "   npm run dev"
echo ""
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For more information, see README.md"
echo ""
