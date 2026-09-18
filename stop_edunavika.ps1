# EduNavika PowerShell Stopper
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "                    STOPPING EDUNAVIKA SERVICES" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[*] Terminating Backend & Frontend processes..." -ForegroundColor Yellow

# Kill by window title
taskkill /fi "WINDOWTITLE eq EduNavika Backend*" /f 2>$null
taskkill /fi "WINDOWTITLE eq EduNavika Frontend*" /f 2>$null

# Also kill any remaining processes listening on ports 8000 or 3000
$ports = @(8000, 3000)
foreach ($p in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($c in $conns) {
            try {
                Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
                Write-Host "[OK] Stopped process on port $p (PID: $($c.OwningProcess))" -ForegroundColor Green
            } catch {}
        }
    }
}

Write-Host "[OK] All EduNavika services stopped cleanly." -ForegroundColor Green
Start-Sleep -Seconds 2
