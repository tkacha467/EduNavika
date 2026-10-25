#!/bin/bash
# =====================================================================
#                    EDUNAVIKA APPLICATION LAUNCHER
#          GSEB Adaptive Learning Platform Standards 9 to 12
# =====================================================================

# 1. Resolve repository directory and switch to it
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Set terminal tab/window title for the launcher
echo -ne "\033]0;EduNavika Launcher\007"

echo "====================================================================="
echo "                   EDUNAVIKA APPLICATION LAUNCHER                    "
echo "         GSEB Adaptive Learning Platform Standards 9 to 12           "
echo "====================================================================="
echo ""

# 2. Ensure macOS package manager paths (Homebrew / local) are in PATH
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:$PATH"

# 3. Check Python and Virtual Environment
VENV_PYTHON="$DIR/.venv/bin/python"

if [ -f "$VENV_PYTHON" ]; then
    PYTHON_EXE="$VENV_PYTHON"
    echo "[OK] Found virtual environment: .venv"
else
    echo "[*] Virtual environment not found. Checking system Python..."
    SYS_PYTHON=""
    for cmd in python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" &>/dev/null; then
            SYS_PYTHON="$cmd"
            break
        fi
    done

    if [ -z "$SYS_PYTHON" ]; then
        echo "[ERROR] Python 3 is not installed or not in your PATH."
        echo "Please install Python 3.10+ (e.g., brew install python@3.12)."
        echo ""
        read -r -p "Press [Enter] to exit..." dummy
        exit 1
    fi

    echo "[*] Creating virtual environment .venv with $SYS_PYTHON ..."
    "$SYS_PYTHON" -m venv "$DIR/.venv"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        read -r -p "Press [Enter] to exit..." dummy
        exit 1
    fi

    PYTHON_EXE="$DIR/.venv/bin/python"
    echo "[*] Installing required Python packages from requirements.txt ..."
    "$PYTHON_EXE" -m pip install --upgrade pip setuptools wheel
    "$PYTHON_EXE" -m pip install -r "$DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install Python dependencies."
        read -r -p "Press [Enter] to exit..." dummy
        exit 1
    fi
    echo "[OK] Python dependencies installed successfully."
fi

echo "[OK] Python runtime:"
"$PYTHON_EXE" --version
echo ""

# 4. Check Node.js and npm
if ! command -v node &>/dev/null; then
    echo "[ERROR] Node.js is not found in your PATH."
    echo "Please install Node.js (e.g., brew install node)."
    read -r -p "Press [Enter] to exit..." dummy
    exit 1
fi
echo "[OK] Node runtime: $(node --version)"

if ! command -v npm &>/dev/null; then
    echo "[ERROR] npm is not found in your PATH."
    read -r -p "Press [Enter] to exit..." dummy
    exit 1
fi
echo "[OK] npm runtime: $(npm --version)"
echo ""

# 5. Check and install frontend dependencies if missing
if [ ! -d "$DIR/frontend/node_modules" ]; then
    echo "[*] Installing frontend dependencies: npm install ..."
    (cd "$DIR/frontend" && npm install)
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install frontend dependencies."
        read -r -p "Press [Enter] to exit..." dummy
        exit 1
    fi
    echo "[OK] Frontend dependencies installed."
else
    echo "[OK] Frontend node_modules verified."
fi

# 6. Clean up any stale processes listening on ports 8000 and 3000
echo "[*] Checking for stale processes on ports 8000 and 3000..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :3000 | xargs kill -9 2>/dev/null || true

echo ""
echo "====================================================================="
echo " Starting Backend and Frontend Services in Separate Terminals...     "
echo "====================================================================="
echo ""

# 7. Launch Backend in a separate Terminal window
echo "[*] Starting Backend Server on http://127.0.0.1:8000 ..."
osascript - "$DIR" "$PYTHON_EXE" <<'EOF'
on run argv
    set workDir to item 1 of argv
    set pyExe to item 2 of argv
    tell application "Terminal"
        activate
        set newTab to do script "cd " & quoted form of workDir & " && " & quoted form of pyExe & " -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"
        set custom title of newTab to "EduNavika Backend"
    end tell
end run
EOF

# 8. Launch Frontend in a separate Terminal window
echo "[*] Starting Frontend Server on http://localhost:3000 ..."
osascript - "$DIR" <<'EOF'
on run argv
    set workDir to item 1 of argv
    tell application "Terminal"
        activate
        set newTab to do script "cd " & quoted form of (workDir & "/frontend") & " && npm run dev"
        set custom title of newTab to "EduNavika Frontend"
    end tell
end run
EOF

# 9. Wait for services to initialize
echo "[*] Waiting for services to initialize..."
sleep 4

# 10. Open application in Google Chrome or default web browser
echo "[*] Opening application in browser..."
open -a "Google Chrome" "http://localhost:3000" 2>/dev/null || open "http://localhost:3000"

echo ""
echo "====================================================================="
echo "                    SERVICES ARE RUNNING!                            "
echo "====================================================================="
echo ""
echo "   * Frontend Web App:     http://localhost:3000"
echo "   * Backend REST API:     http://localhost:8000/docs"
echo ""
echo "  Keep this window open. Press [Enter] to stop all EduNavika services."
echo "====================================================================="
echo ""

# 11. Cleanup function on exit or interrupt
cleanup() {
    echo ""
    echo "[*] Stopping EduNavika services..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    lsof -ti :3000 | xargs kill -9 2>/dev/null || true
    pkill -f "uvicorn backend.app.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true

    # Optionally close the terminal windows opened for EduNavika
    osascript <<'EOF' >/dev/null 2>&1
    tell application "Terminal"
        repeat with w in (every window)
            try
                if custom title of selected tab of w contains "EduNavika Backend" or custom title of selected tab of w contains "EduNavika Frontend" then
                    close w saving no
                end if
            end try
        end repeat
    end tell
EOF

    echo "[OK] All EduNavika services stopped."
    sleep 1
    exit 0
}

trap cleanup INT TERM

read -r -p "Press [Enter] to stop EduNavika: " dummy
cleanup
