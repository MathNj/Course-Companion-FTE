#!/bin/bash
# Quick deployment script for Fly.io
# Usage: bash deploy-to-flyio.sh

set -e

echo "============================================"
echo "Course Companion FTE - Fly.io Deployment"
echo "============================================"
echo ""

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl not installed"
    echo "Install from: https://fly.io/docs/getting-started/installing-flyctl/"
    echo ""
    echo "Windows: powershell -Command \"iwr https://fly.io/install.ps1 -useb | iex\""
    echo "macOS: brew install flyctl"
    echo "Linux: curl -L https://fly.io/install.sh | sh"
    exit 1
fi

echo "✅ flyctl installed"
echo ""

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "Please login to Fly.io:"
    flyctl auth login
fi

echo "✅ Logged in to Fly.io"
echo ""

# Generate JWT secret if not exists
if [ ! -f ".jwt_secret" ]; then
    echo "Generating JWT secret..."
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" > .jwt_secret
    echo "✅ JWT secret generated and saved to .jwt_secret"
    echo ""
fi

JWT_SECRET=$(cat .jwt_secret)

# Navigate to backend
cd backend

echo "Step 1: Creating Fly.io app..."
echo "-------------------------------"

# Check if app already exists
if flyctl apps list | grep -q "course-companion-fte"; then
    echo "App already exists, skipping creation"
else
    flyctl launch --name course-companion-fte --region iad --no-deploy --copy-config
fi

echo ""
echo "Step 2: Creating PostgreSQL database..."
echo "----------------------------------------"

# Check if database exists
if flyctl postgres list | grep -q "course-companion-db"; then
    echo "Database already exists"
else
    flyctl postgres create \
      --name course-companion-db \
      --region iad \
      --initial-cluster-size 1 \
      --vm-size shared-cpu-1x \
      --volume-size 1

    echo "Attaching database to app..."
    flyctl postgres attach course-companion-db
fi

echo ""
echo "Step 3: Setting secrets..."
echo "-------------------------"

flyctl secrets set \
  JWT_SECRET_KEY="$JWT_SECRET" \
  APP_ENV="production" \
  CORS_ORIGINS="https://chat.openai.com,https://chatgpt.com" \
  LOG_LEVEL="INFO"

echo ""
echo "Step 4: Deploying application..."
echo "--------------------------------"

flyctl deploy --dockerfile Dockerfile.production

echo ""
echo "Step 5: Running database migrations..."
echo "---------------------------------------"

flyctl ssh console -C "alembic upgrade head"

echo ""
echo "============================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo "Your app is now live at:"
flyctl apps info | grep "Hostname"
echo ""
echo "Next steps:"
echo "1. Test the API:"
echo "   curl https://course-companion-fte.fly.dev/health"
echo "   curl https://course-companion-fte.fly.dev/api/v1/chapters"
echo ""
echo "2. Update ChatGPT Custom GPT:"
echo "   - Edit Actions in ChatGPT"
echo "   - Import from: https://course-companion-fte.fly.dev/api/openapi.json"
echo ""
echo "3. Monitor logs:"
echo "   flyctl logs"
echo ""
echo "Useful commands:"
echo "  flyctl status      # Check app status"
echo "  flyctl logs        # View logs"
echo "  flyctl ssh console # SSH into app"
echo "  flyctl open        # Open in browser"
echo ""
