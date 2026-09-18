@echo off
cd /d "%~dp0"
title EduNavika Launcher

echo =====================================================================
echo                    EDUNAVIKA APPLICATION LAUNCHER
echo          GSEB Adaptive Learning Platform Standards 9 to 12
echo =====================================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
echo [OK] Python is available.

:: 2. Check Node.js and npm
call npm --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js and npm are not installed or not in your PATH.
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo [OK] Node.js and npm are available.

:: 3. Check frontend node_modules
if not exist "frontend\node_modules" (
    echo.
    echo [*] Installing frontend dependencies...
    cd frontend
    call npm install
    cd /d "%~dp0"
    echo [OK] Dependencies installed.
)

echo.
echo =====================================================================
echo  Starting Backend and Frontend Services...
echo =====================================================================
echo.

:: 4. Launch Backend in separate window
echo [*] Starting Backend Server on http://127.0.0.1:8000 ...
start "EduNavika Backend" cmd /k "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

:: 5. Launch Frontend in separate window
echo [*] Starting Frontend Server on http://localhost:3000 ...
start "EduNavika Frontend" cmd /k "cd frontend && npm run dev"

:: 6. Wait 3 seconds for servers to start
echo [*] Waiting for services to initialize...
ping 127.0.0.1 -n 4 >nul

:: 7. Open browser
echo [*] Opening application in browser...
start http://localhost:3000

echo.
echo =====================================================================
echo                    SERVICES ARE RUNNING!
echo =====================================================================
echo.
echo   * Frontend Web App:     http://localhost:3000
echo   * Backend REST API:     http://localhost:8000/docs
echo.
echo  Keep this window open. Press any key to stop all EduNavika services.
echo =====================================================================
echo.
pause

echo [*] Stopping services...
taskkill /fi "WINDOWTITLE eq EduNavika Backend*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq EduNavika Frontend*" /f >nul 2>&1
echo [OK] All services stopped.
ping 127.0.0.1 -n 2 >nul
exit /b 0
