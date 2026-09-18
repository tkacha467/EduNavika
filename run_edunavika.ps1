# EduNavika PowerShell Launcher
$Host.UI.RawUI.WindowTitle = "EduNavika — Launcher"

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "                EDUNAVIKA — LAUNCHER & ORCHESTRATOR" -ForegroundColor Cyan
Write-Host "    Research-Grade Adaptive Learning & Assessment Platform (GSEB)" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not found in your PATH!" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://www.python.org/ and check 'Add to PATH'."
    Read-Host "Press Enter to exit..."
    exit 1
}
$pyVer = python --version 2>&1
Write-Host "[OK] $pyVer detected." -ForegroundColor Green

# 2. Check npm
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js / npm is not found in your PATH!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/"
    Read-Host "Press Enter to exit..."
    exit 1
}
$npmVer = npm --version 2>&1
Write-Host "[OK] npm v$npmVer detected." -ForegroundColor Green

# 3. Check frontend node_modules
$nodeModulesPath = Join-Path $PSScriptRoot "frontend\node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "`n[*] Installing frontend dependencies (first-time setup)..." -ForegroundColor Yellow
    Push-Location (Join-Path $PSScriptRoot "frontend")
    npm install
    Pop-Location
    Write-Host "[OK] Dependencies installed." -ForegroundColor Green
}

Write-Host "`n---------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host " Starting Services..." -ForegroundColor White
Write-Host "---------------------------------------------------------------------" -ForegroundColor DarkGray

# 4. Start Backend Server (FastAPI on Port 8000)
Write-Host "[*] Launching Backend on http://127.0.0.1:8000 ..." -ForegroundColor Yellow
$backendCmd = "/k title EduNavika Backend && cd /d `"$PSScriptRoot`" && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process -FilePath "cmd.exe" -ArgumentList $backendCmd

# 5. Start Frontend Server (Vite on Port 3000)
Write-Host "[*] Launching Frontend on http://localhost:3000 ..." -ForegroundColor Yellow
$frontendCmd = "/k title EduNavika Frontend && cd /d `"$PSScriptRoot\frontend`" && npm run dev"
Start-Process -FilePath "cmd.exe" -ArgumentList $frontendCmd

# 6. Wait for servers to initialize
Write-Host "[*] Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

# 7. Open Browser
Write-Host "[*] Opening application in default web browser..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "                      ALL SERVICES RUNNING!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  * Student & Teacher Web Portal:  http://localhost:3000" -ForegroundColor White
Write-Host "  * Backend REST API (Swagger UI): http://localhost:8000/docs" -ForegroundColor White
Write-Host "  * Backend Alternative (ReDoc):   http://localhost:8000/redoc" -ForegroundColor White
Write-Host ""
Write-Host "To stop EduNavika:" -ForegroundColor DarkYellow
Write-Host "  - Close the Backend and Frontend terminal windows, or" -ForegroundColor DarkYellow
Write-Host "  - Run: .\stop_edunavika.ps1 (or double-click stop_edunavika.bat)" -ForegroundColor DarkYellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to stop both servers now..."

Write-Host "[*] Stopping EduNavika processes..." -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "stop_edunavika.bat")
Write-Host "[OK] EduNavika services stopped." -ForegroundColor Green
Start-Sleep -Seconds 2
