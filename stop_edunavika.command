#!/bin/bash
# =====================================================================
#                    STOPPING EDUNAVIKA SERVICES
# =====================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo -ne "\033]0;EduNavika Stopper\007"

echo "====================================================================="
echo "                   STOPPING EDUNAVIKA SERVICES                       "
echo "====================================================================="
echo ""

echo "[*] Terminating Backend and Frontend processes..."

# Kill processes listening on ports 8000 and 3000
PIDS_8000=$(lsof -ti :8000 2>/dev/null)
if [ -n "$PIDS_8000" ]; then
    echo "[*] Killing process on port 8000 ($PIDS_8000)..."
    kill -9 $PIDS_8000 2>/dev/null || true
fi

PIDS_3000=$(lsof -ti :3000 2>/dev/null)
if [ -n "$PIDS_3000" ]; then
    echo "[*] Killing process on port 3000 ($PIDS_3000)..."
    kill -9 $PIDS_3000 2>/dev/null || true
fi

# Kill any leftover uvicorn or vite processes
pkill -f "uvicorn backend.app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# Close any EduNavika terminal windows
osascript <<'EOF' >/dev/null 2>&1
tell application "Terminal"
    repeat with w in (every window)
        try
            if custom title of selected tab of w contains "EduNavika" then
                close w saving no
            end if
        end try
    end repeat
end tell
EOF

echo "[OK] All EduNavika backend and frontend services have been stopped."
sleep 2
exit 0
