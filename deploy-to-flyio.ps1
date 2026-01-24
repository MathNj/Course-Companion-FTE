# Course Companion FTE - Fly.io Deployment Script for Windows
# Usage: .\deploy-to-flyio.ps1

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Course Companion FTE - Fly.io Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if flyctl is installed
$flyctlInstalled = $false
try {
    $null = flyctl version 2>&1
    $flyctlInstalled = $true
} catch {
    $flyctlInstalled = $false
}

if (-not $flyctlInstalled) {
    Write-Host "❌ flyctl not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install Fly.io CLI:" -ForegroundColor Yellow
    Write-Host "  PowerShell: iwr https://fly.io/install.ps1 -useb | iex"
    Write-Host ""
    Write-Host "Or download from: https://fly.io/docs/getting-started/installing-flyctl/"
    exit 1
}

Write-Host "✅ flyctl installed" -ForegroundColor Green
Write-Host ""

# Check if logged in
Write-Host "Checking Fly.io authentication..." -ForegroundColor Yellow
try {
    flyctl auth whoami 2>&1 | Out-Null
    Write-Host "✅ Logged in to Fly.io" -ForegroundColor Green
} catch {
    Write-Host "Please login to Fly.io:" -ForegroundColor Yellow
    flyctl auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Login failed" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Generate JWT secret
if (-not (Test-Path ".jwt_secret")) {
    Write-Host "Generating JWT secret..." -ForegroundColor Yellow
    $jwtSecret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
    $jwtSecret | Out-File -FilePath ".jwt_secret" -Encoding UTF8
    Write-Host "✅ JWT secret generated and saved to .jwt_secret" -ForegroundColor Green
    Write-Host ""
}

$JWT_SECRET = Get-Content .jwt_secret

# Navigate to backend
$originalDir = Get-Location
Set-Location backend

Write-Host "Step 1: Creating Fly.io app..." -ForegroundColor Cyan
Write-Host "-------------------------------" -ForegroundColor Cyan

# Check if app exists
$appExists = flyctl apps list 2>&1 | Select-String "course-companion-fte"
if ($appExists) {
    Write-Host "App already exists, skipping creation" -ForegroundColor Yellow
} else {
    flyctl launch --name course-companion-fte --region iad --no-deploy --copy-config
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create app" -ForegroundColor Red
        Set-Location $originalDir
        exit 1
    }
}

Write-Host ""

Write-Host "Step 2: Creating PostgreSQL database..." -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan

# Check if database exists
$dbExists = flyctl postgres list 2>&1 | Select-String "course-companion-db"
if ($dbExists) {
    Write-Host "Database already exists" -ForegroundColor Yellow
} else {
    flyctl postgres create --name course-companion-db --region iad --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create database" -ForegroundColor Red
        Set-Location $originalDir
        exit 1
    }

    Write-Host "Attaching database to app..." -ForegroundColor Yellow
    flyctl postgres attach course-companion-db
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Warning: Database attachment may have failed" -ForegroundColor Yellow
    }
}

Write-Host ""

Write-Host "Step 3: Setting secrets..." -ForegroundColor Cyan
Write-Host "-------------------------" -ForegroundColor Cyan

flyctl secrets set JWT_SECRET_KEY="$JWT_SECRET" APP_ENV="production" CORS_ORIGINS="https://chat.openai.com,https://chatgpt.com" LOG_LEVEL="INFO"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set secrets" -ForegroundColor Red
    Set-Location $originalDir
    exit 1
}

Write-Host ""

Write-Host "Step 4: Deploying application..." -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan

flyctl deploy --dockerfile Dockerfile.production
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs with: flyctl logs" -ForegroundColor Yellow
    Set-Location $originalDir
    exit 1
}

Write-Host ""

Write-Host "Step 5: Running database migrations..." -ForegroundColor Cyan
Write-Host "---------------------------------------" -ForegroundColor Cyan

flyctl ssh console -C "alembic upgrade head"
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Warning: Migration may have failed. Run manually:" -ForegroundColor Yellow
    Write-Host "   flyctl ssh console" -ForegroundColor Yellow
    Write-Host "   alembic upgrade head" -ForegroundColor Yellow
}

Write-Host ""

Set-Location $originalDir

Write-Host "============================================" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Your app is now live at:" -ForegroundColor Cyan
flyctl apps info | Select-String "Hostname"
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the API:" -ForegroundColor White
Write-Host "   curl https://course-companion-fte.fly.dev/health" -ForegroundColor Gray
Write-Host "   curl https://course-companion-fte.fly.dev/api/v1/chapters" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Update ChatGPT Custom GPT:" -ForegroundColor White
Write-Host "   - Edit Actions in ChatGPT" -ForegroundColor Gray
Write-Host "   - Import from: https://course-companion-fte.fly.dev/api/openapi.json" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Monitor logs:" -ForegroundColor White
Write-Host "   flyctl logs" -ForegroundColor Gray
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  flyctl status      # Check app status" -ForegroundColor Gray
Write-Host "  flyctl logs        # View logs" -ForegroundColor Gray
Write-Host "  flyctl ssh console # SSH into app" -ForegroundColor Gray
Write-Host "  flyctl open        # Open in browser" -ForegroundColor Gray
Write-Host ""
