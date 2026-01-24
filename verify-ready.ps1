# Verification script to check if system is ready for ChatGPT testing
# Run with: powershell -ExecutionPolicy Bypass -File verify-ready.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Course Companion FTE - Readiness Check" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Check 1: Docker containers
Write-Host "Checking Docker containers..." -ForegroundColor Yellow
try {
    $containers = docker-compose ps 2>&1
    if ($containers -match "healthy") {
        Write-Host "  ✅ Docker containers are running" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Docker containers not healthy" -ForegroundColor Red
        Write-Host "     Run: docker-compose up -d" -ForegroundColor Yellow
        $allPassed = $false
    }
} catch {
    Write-Host "  ❌ Docker not available" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Check 2: Backend health
Write-Host "Checking backend health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 5
    if ($response.Content -match "healthy") {
        Write-Host "  ✅ Backend is healthy" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Backend not healthy" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  ❌ Backend not responding" -ForegroundColor Red
    Write-Host "     Check: docker-compose logs backend" -ForegroundColor Yellow
    $allPassed = $false
}
Write-Host ""

# Check 3: API endpoints
Write-Host "Checking API endpoints..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/chapters" -UseBasicParsing -TimeoutSec 5
    if ($response.Content -match "chapter-1") {
        Write-Host "  ✅ Chapters endpoint working" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Chapters endpoint failed" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  ❌ API endpoints not accessible" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Check 4: OpenAPI schema
Write-Host "Checking OpenAPI schema..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/api/openapi.json" -UseBasicParsing -TimeoutSec 5
    if ($response.Content -match "get_chapters") {
        Write-Host "  ✅ OpenAPI schema available" -ForegroundColor Green
    } else {
        Write-Host "  ❌ OpenAPI schema incomplete" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  ❌ OpenAPI schema not found" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Check 5: Content files
Write-Host "Checking content files..." -ForegroundColor Yellow
$chapterCount = (Get-ChildItem -Path "backend\content\chapters\chapter-*.json" -ErrorAction SilentlyContinue).Count
$quizCount = (Get-ChildItem -Path "backend\content\quizzes\chapter-*-quiz.json" -ErrorAction SilentlyContinue).Count

if ($chapterCount -eq 6 -and $quizCount -eq 6) {
    Write-Host "  ✅ All content files present (6 chapters, 6 quizzes)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Content files: $chapterCount chapters, $quizCount quizzes" -ForegroundColor Yellow
    if ($chapterCount -ne 6 -or $quizCount -ne 6) {
        $allPassed = $false
    }
}
Write-Host ""

# Check 6: ChatGPT app files
Write-Host "Checking ChatGPT app files..." -ForegroundColor Yellow
if ((Test-Path "chatgpt-app\instructions.md") -and (Test-Path "chatgpt-app\openapi.yaml")) {
    Write-Host "  ✅ ChatGPT configuration files present" -ForegroundColor Green
} else {
    Write-Host "  ❌ ChatGPT files missing" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Summary
Write-Host "============================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "✅ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Download ngrok: https://ngrok.com/download" -ForegroundColor White
    Write-Host "2. Run: ngrok http 8001" -ForegroundColor White
    Write-Host "3. Copy the https://....ngrok-free.app URL" -ForegroundColor White
    Write-Host "4. Follow TESTING-GUIDE.md to create Custom GPT" -ForegroundColor White
    Write-Host ""
    Write-Host "Backend URL: http://localhost:8001" -ForegroundColor Cyan
    Write-Host "OpenAPI Schema: http://localhost:8001/api/openapi.json" -ForegroundColor Cyan
    Write-Host "Health Check: http://localhost:8001/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Happy testing! 🚀" -ForegroundColor Green
} else {
    Write-Host "❌ SOME CHECKS FAILED" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please fix the issues above before proceeding." -ForegroundColor Yellow
    Write-Host "Check docker-compose logs for more details." -ForegroundColor Yellow
    exit 1
}
