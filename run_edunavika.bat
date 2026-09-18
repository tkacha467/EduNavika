@echo off
setlocal enabledelayedexpansion

title EduNavika — Launcher

echo =====================================================================
echo                 EDUNAVIKA — LAUNCHER & ORCHESTRATOR
echo     Research-Grade Adaptive Learning & Assessment Platform (GSEB)
echo =====================================================================
echo.

:: 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in your PATH!
    echo Please install Python 3.10+ from https://www.python.org/ and check "Add to PATH".
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo [OK] %PYTHON_VER% detected.

:: 2. Check Node / npm
where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js / npm is not found in your PATH!
    echo Please install Node.js (v18+) from https://nodejs.org/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version 2^>^&1') do set NPM_VER=%%i
echo [OK] npm v%NPM_VER% detected.

:: 3. Check frontend node_modules
if not exist "frontend\node_modules\" (
    echo.
    echo [*] Installing frontend dependencies (first-time setup)...
    cd frontend
    call npm install
    cd ..
    echo [OK] Frontend dependencies installed.
)

echo.
echo ---------------------------------------------------------------------
echo  Starting Services...
echo ---------------------------------------------------------------------

:: 4. Start Backend Server (FastAPI + Uvicorn)
echo [*] Launching Backend on http://127.0.0.1:8000 ...
start "EduNavika Backend (FastAPI)" cmd /k "title EduNavika Backend && cd /d "%~dp0" && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

:: 5. Start Frontend Server (Vite)
echo [*] Launching Frontend on http://localhost:3000 ...
start "EduNavika Frontend (Vite)" cmd /k "title EduNavika Frontend && cd /d "%~dp0frontend" && npm run dev"

:: 6. Wait for servers to spin up
echo [*] Waiting for services to initialize...
timeout /t 4 /nobreak >nul

:: 7. Launch browser to the application
echo [*] Opening application in default web browser...
start http://localhost:3000

echo.
echo =====================================================================
echo                      ALL SERVICES RUNNING!
echo =====================================================================
echo.
echo   * Student & Teacher Web Portal:  http://localhost:3000
echo   * Backend REST API (Swagger UI): http://localhost:8000/docs
echo   * Backend Alternative (ReDoc):   http://localhost:8000/redoc
echo.
echo  To stop EduNavika:
echo   - Close the Backend and Frontend terminal windows, or
echo   - Press any key below to automatically terminate both services.
echo =====================================================================
echo.

pause

echo [*] Stopping EduNavika processes...
taskkill /fi "WINDOWTITLE eq EduNavika Backend*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq EduNavika Frontend*" /f >nul 2>&1

echo [OK] EduNavika services stopped.
timeout /t 2 /nobreak >nul
exit /b 0
