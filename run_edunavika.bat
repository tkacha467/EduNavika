@echo off
cd /d "%~dp0"
title EduNavika Launcher

echo =====================================================================
echo                    EDUNAVIKA APPLICATION LAUNCHER
echo          GSEB Adaptive Learning Platform Standards 9 to 12
echo =====================================================================
echo.

:: 0. Ensure Python and Node paths are in PATH
set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%LOCALAPPDATA%\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.19.0-win-x64;%PATH%"

:: 1. Check Python / Virtual Environment
if exist "%~dp0.venv\Scripts\python.exe" goto :USE_VENV

echo [*] Virtual environment not found. Checking system Python...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please ensure Python 3.11+ is installed.
    pause
    exit /b 1
)

echo [*] Creating virtual environment .venv ...
python -m venv "%~dp0.venv"
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
echo [*] Installing required Python packages from requirements.txt ...
"%PYTHON_EXE%" -m pip install --upgrade pip setuptools wheel
"%PYTHON_EXE%" -m pip install -r "%~dp0requirements.txt"
echo [OK] Python dependencies installed successfully.
goto :CHECK_PYTHON_VER

:USE_VENV
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
echo [OK] Found virtual environment: .venv

:CHECK_PYTHON_VER
echo [OK] Python runtime:
"%PYTHON_EXE%" --version
echo.

:: 2. Check Node.js and npm
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not found in your PATH.
    echo Please ensure Node.js is installed.
    pause
    exit /b 1
)
echo [OK] Node runtime:
node --version
echo.

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not found in your PATH.
    pause
    exit /b 1
)

:: 3. Check and install frontend dependencies if missing
if exist "%~dp0frontend\node_modules" goto :FRONTEND_READY

echo.
echo [*] Installing frontend dependencies: npm install ...
cd /d "%~dp0frontend"
call npm install
cd /d "%~dp0"
echo [OK] Frontend dependencies installed.

:FRONTEND_READY

:: 4. Clean up any stale processes listening on ports 8000 and 3000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo =====================================================================
echo  Starting Backend and Frontend Services...
echo =====================================================================
echo.

:: 5. Launch Backend in separate window
echo [*] Starting Backend Server on http://127.0.0.1:8000 ...
start "EduNavika Backend" cmd /k "cd /d "%~dp0" && "%PYTHON_EXE%" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

:: 6. Launch Frontend in separate window
echo [*] Starting Frontend Server on http://localhost:3000 ...
start "EduNavika Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

:: 7. Wait 4 seconds for servers to start
echo [*] Waiting for services to initialize...
ping 127.0.0.1 -n 5 >nul

:: 8. Open browser
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

:: Also terminate any remaining listeners on ports 8000 and 3000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo [OK] All EduNavika services stopped.
ping 127.0.0.1 -n 2 >nul
exit /b 0
