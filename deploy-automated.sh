#!/bin/bash
# Automated deployment script
# Run this AFTER authenticating with flyctl auth login

set -e

echo "============================================"
echo "Course Companion FTE - Auto Deployment"
echo "============================================"
echo ""

# Check authentication
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Not authenticated. Please run: flyctl auth login"
    exit 1
fi

echo "✅ Authenticated as: $(flyctl auth whoami)"
echo ""

# Navigate to backend
cd backend

echo "Step 1: Creating Fly.io app..."
if flyctl apps list | grep -q "course-companion-fte"; then
    echo "   App already exists, skipping creation"
else
    flyctl launch --name course-companion-fte --region iad --no-deploy --copy-config
fi
echo "✅ App ready"
echo ""

echo "Step 2: Creating PostgreSQL database..."
if flyctl postgres list | grep -q "course-companion-db"; then
    echo "   Database already exists"
else
    flyctl postgres create --name course-companion-db --region iad --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1
    echo "   Attaching database..."
    flyctl postgres attach course-companion-db
fi
echo "✅ Database ready"
echo ""

echo "Step 3: Setting secrets..."
JWT_SECRET="nFpDpFougSl6BkqqXwzsDmKHA6keETfSytpB8nPQlfw"
flyctl secrets set JWT_SECRET_KEY="$JWT_SECRET" APP_ENV="production" CORS_ORIGINS="https://chat.openai.com,https://chatgpt.com" LOG_LEVEL="INFO"
echo "✅ Secrets set"
echo ""

echo "Step 4: Deploying application..."
echo "   This will take 3-5 minutes..."
flyctl deploy --dockerfile Dockerfile.production
echo "✅ Deployment complete"
echo ""

echo "Step 5: Running database migrations..."
flyctl ssh console -C "alembic upgrade head"
echo "✅ Migrations complete"
echo ""

echo "============================================"
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "============================================"
echo ""
echo "Your production URLs:"
flyctl apps info | grep "Hostname"
echo ""
echo "Test your API:"
echo "  curl https://course-companion-fte.fly.dev/health"
echo ""
echo "OpenAPI Spec for ChatGPT:"
echo "  https://course-companion-fte.fly.dev/api/openapi.json"
echo ""
echo "Monitor logs:"
echo "  flyctl logs"
echo ""
