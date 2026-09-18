@echo off
title EduNavika — Stopper

echo =====================================================================
echo                    STOPPING EDUNAVIKA SERVICES
echo =====================================================================
echo.

echo [*] Terminating Backend & Frontend processes...

taskkill /fi "WINDOWTITLE eq EduNavika Backend*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq EduNavika Frontend*" /f >nul 2>&1

:: Also kill any remaining processes listening on ports 8000 or 3000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo [OK] All EduNavika backend and frontend services have been stopped.
timeout /t 2 /nobreak >nul
exit /b 0
