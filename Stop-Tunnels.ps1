# Stop Cloudflare Tunnels
# PowerShell script to stop all tunnel processes

Write-Host "Stopping Cloudflare Tunnels..." -ForegroundColor Yellow
Write-Host ""

# Find and stop all cloudflared processes
$processes = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue

if ($processes) {
    $count = $processes.Count
    Write-Host "Found $count tunnel process(es)" -ForegroundColor Cyan

    foreach ($process in $processes) {
        Write-Host "  Stopping PID $($process.Id)..." -ForegroundColor Yellow
        Stop-Process -Id $process.Id -Force
    }

    Write-Host ""
    Write-Host "✓ All tunnels stopped!" -ForegroundColor Green
} else {
    Write-Host "No tunnels running" -ForegroundColor Gray
}

Write-Host ""
