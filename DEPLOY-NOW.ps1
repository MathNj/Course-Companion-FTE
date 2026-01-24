# ===================================================================
# DEPLOY TO PRODUCTION - STEP BY STEP
# ===================================================================
# Run these commands in PowerShell (as Administrator)
# ===================================================================

# STEP 1: Install flyctl (if not installed)
Write-Host "Step 1: Installing flyctl..." -ForegroundColor Cyan
iwr https://fly.io/install.ps1 -useb | iex

# STEP 2: Login to Fly.io
Write-Host "Step 2: Login to Fly.io..." -ForegroundColor Cyan
flyctl auth login

# STEP 3: Navigate to backend directory
Write-Host "Step 3: Navigate to backend..." -ForegroundColor Cyan
cd backend

# STEP 4: Initialize Fly.io app
Write-Host "Step 4: Creating Fly.io app..." -ForegroundColor Cyan
flyctl launch --name course-companion-fte --region iad --no-deploy --copy-config

# STEP 5: Create PostgreSQL database
Write-Host "Step 5: Creating PostgreSQL database..." -ForegroundColor Cyan
flyctl postgres create --name course-companion-db --region iad --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1

# STEP 6: Attach database to app
Write-Host "Step 6: Attaching database..." -ForegroundColor Cyan
flyctl postgres attach course-companion-db

# STEP 7: Set secrets
Write-Host "Step 7: Setting environment secrets..." -ForegroundColor Cyan
flyctl secrets set JWT_SECRET_KEY="nFpDpFougSl6BkqqXwzsDmKHA6keETfSytpB8nPQlfw" APP_ENV="production" CORS_ORIGINS="https://chat.openai.com,https://chatgpt.com" LOG_LEVEL="INFO"

# STEP 8: Deploy application
Write-Host "Step 8: Deploying application (this takes 3-5 minutes)..." -ForegroundColor Cyan
flyctl deploy --dockerfile Dockerfile.production

# STEP 9: Run migrations
Write-Host "Step 9: Running database migrations..." -ForegroundColor Cyan
flyctl ssh console -C "alembic upgrade head"

# STEP 10: Get deployment info
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your application is now live:" -ForegroundColor Cyan
flyctl apps info | Select-String "Hostname"
Write-Host ""
Write-Host "Test your API:" -ForegroundColor Yellow
Write-Host "  curl https://course-companion-fte.fly.dev/health" -ForegroundColor Gray
Write-Host ""
Write-Host "OpenAPI Spec for ChatGPT:" -ForegroundColor Yellow
Write-Host "  https://course-companion-fte.fly.dev/api/openapi.json" -ForegroundColor Gray
Write-Host ""
Write-Host "Monitor logs:" -ForegroundColor Yellow
Write-Host "  flyctl logs" -ForegroundColor Gray
Write-Host ""
