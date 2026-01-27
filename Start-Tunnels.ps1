# Cloudflare Tunnel Launcher for Course Companion FTE
# PowerShell script for automated tunnel creation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Course Companion FTE - Cloudflare Tunnels" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if cloudflared is installed
Write-Host "[1/5] Checking cloudflared installation..." -ForegroundColor Yellow
try {
    $version = cloudflared --version 2>$null
    Write-Host "  ✓ cloudflared installed: $version" -ForegroundColor Green
} catch {
    Write-Host "  ✗ cloudflared not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install first:" -ForegroundColor Yellow
    Write-Host "  winget install cloudflare.cloudflared" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host ""

# Check if backend APIs are running
Write-Host "[2/5] Checking backend APIs..." -ForegroundColor Yellow

$ports = @{8000 = "Content API"; 8001 = "Quiz API"; 8002 = "Progress API"}
$running = @{}

foreach ($port in $ports.Keys) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port/" -TimeoutSec 2 -UseBasicParsing
        $running[$port] = $true
        Write-Host "  ✓ $($ports[$port]) is running on port $port" -ForegroundColor Green
    } catch {
        $running[$port] = $false
        Write-Host "  ✗ $($ports[$port]) NOT running on port $port" -ForegroundColor Red
        Write-Host "    Start with: python simple_$($port - 8000)_api.py" -ForegroundColor Gray
    }
}

Write-Host ""

# Count running APIs
$runningCount = ($running.Values | Where-Object { $_ -eq $true }).Count

if ($runningCount -lt 3) {
    Write-Host "WARNING: Not all APIs are running!" -ForegroundColor Red
    Write-Host "Please start all 3 APIs before creating tunnels." -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y") {
        exit 1
    }
}

Write-Host ""

# Start tunnels
Write-Host "[3/5] Starting Cloudflare Tunnels..." -ForegroundColor Yellow
Write-Host ""

$tunnels = @{}

if ($running[8000]) {
    Write-Host "Starting Content API tunnel (port 8000)..." -ForegroundColor Cyan
    $job1 = Start-Job -ScriptBlock {
        $output = cloudflared tunnel --url http://localhost:8000 2>&1
        # Extract URL from output
        $output | Select-String "https://.*\.trycloudflare\.com" | ForEach-Object {
            Write-Host "  Content API URL: $_" -ForegroundColor Green
        }
        Start-Sleep -Seconds 999999
    }
    Write-Host "  ✓ Content API tunnel started" -ForegroundColor Green
    Start-Sleep -Seconds 2
}

if ($running[8001]) {
    Write-Host "Starting Quiz API tunnel (port 8001)..." -ForegroundColor Cyan
    $job2 = Start-Job -ScriptBlock {
        $output = cloudflared tunnel --url http://localhost:8001 2>&1
        $output | Select-String "https://.*\.trycloudflare\.com" | ForEach-Object {
            Write-Host "  Quiz API URL: $_" -ForegroundColor Green
        }
        Start-Sleep -Seconds 999999
    }
    Write-Host "  ✓ Quiz API tunnel started" -ForegroundColor Green
    Start-Sleep -Seconds 2
}

if ($running[8002]) {
    Write-Host "Starting Progress API tunnel (port 8002)..." -ForegroundColor Cyan
    $job3 = Start-Job -ScriptBlock {
        $output = cloudflared tunnel --url http://localhost:8002 2>&1
        $output | Select-String "https://.*\.trycloudflare\.com" | ForEach-Object {
            Write-Host "  Progress API URL: $_" -ForegroundColor Green
        }
        Start-Sleep -Seconds 999999
    }
    Write-Host "  ✓ Progress API tunnel started" -ForegroundColor Green
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "[4/5] Waiting for URLs..." -ForegroundColor Yellow
Write-Host ""
Start-Sleep -Seconds 5

# Show output from jobs
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Your Cloudflare Tunnel URLs:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking job output..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Receive job output to find URLs
if ($running[8000]) {
    $output1 = Receive-Job -Job $job1 -Keep 2>$null
    $output1 | Select-String "https://.*\.trycloudflare\.com" | Select-Object -First 1 | ForEach-Object {
        Write-Host "Content API: $_" -ForegroundColor Green
    }
}

if ($running[8001]) {
    $output2 = Receive-Job -Job $job2 -Keep 2>$null
    $output2 | Select-String "https://.*\.trycloudflare\.com" | Select-Object -First 1 | ForEach-Object {
        Write-Host "Quiz API:    $_" -ForegroundColor Green
    }
}

if ($running[8002]) {
    $output3 = Receive-Job -Job $job3 -Keep 2>$null
    $output3 | Select-String "https://.*\.trycloudflare\.com" | Select-Object -First 1 | ForEach-Object {
        Write-Host "Progress API: $_" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[5/5] Tunnels are running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your APIs are now publicly accessible:" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Copy the URLs above" -ForegroundColor White
Write-Host "2. Use them in your ChatGPT App configuration" -ForegroundColor White
Write-Host "3. Test each URL in your browser" -ForegroundColor White
Write-Host ""
Write-Host "To stop tunnels:" -ForegroundColor Yellow
Write-Host "  Press Ctrl+C in each tunnel window" -ForegroundColor White
Write-Host "  Or run: Stop-Tunnels.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Tunnels will continue running in background." -ForegroundColor Cyan
Write-Host ""
