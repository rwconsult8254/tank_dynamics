#!/bin/bash

# dev.sh - Start backend and frontend dev servers
#
# Usage: ./scripts/dev.sh
#
# Starts:
#   - Backend:  uvicorn on port 8000 (with hot reload scoped to api/ and tank_sim/)
#   - Frontend: Next.js dev server on port 3000
#
# Press Ctrl+C to stop both servers.
#
# Lessons encoded in this script:
#   1. Use .venv/bin/uvicorn directly, NOT "uv run". uv run triggers a full
#      C++ rebuild of the tank_sim extension every time (~60s). The extension
#      is already installed in the venv via "uv pip install -e ."
#   2. Scope uvicorn --reload-dir to api/ and tank_sim/ only. Without this,
#      uvicorn watches the entire project including frontend/.next/, which
#      has thousands of rapidly-changing files. The two file watchers (uvicorn
#      and Next.js) conflict and cause the frontend to hang on refresh.
#   3. Clean up the Next.js dev lock file before starting. Stale lock files
#      from crashed dev servers prevent Next.js from starting.

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Resolve project root (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VENV_BIN="$PROJECT_ROOT/.venv/bin"

# --- Preflight checks ---

if [ ! -f "$VENV_BIN/uvicorn" ]; then
    echo -e "${RED}Error: uvicorn not found in .venv/bin/${NC}"
    echo "Run: uv sync --extra api --extra dev"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${RED}Error: frontend/node_modules not found${NC}"
    echo "Run: cd frontend && npm install"
    exit 1
fi

# Check that tank_sim C++ extension is installed
if ! "$VENV_BIN/python" -c "import tank_sim" 2>/dev/null; then
    echo -e "${YELLOW}Warning: tank_sim not installed. Building (this takes ~60s)...${NC}"
    cd "$PROJECT_ROOT" && uv pip install -e .
fi

# --- Cleanup ---

# Kill any existing servers on our ports
for port in 3000 8000; do
    pid=$(lsof -ti ":$port" 2>/dev/null || true)
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}Killing existing process on port $port (PID: $pid)${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
done

# Remove stale Next.js lock file
rm -f "$FRONTEND_DIR/.next/dev/lock"

# --- Start servers ---

# Trap Ctrl+C to kill both background processes
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}Done.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${GREEN}Starting backend on http://localhost:8000${NC}"
cd "$PROJECT_ROOT"
"$VENV_BIN/uvicorn" api.main:app \
    --reload \
    --reload-dir api \
    --reload-dir tank_sim \
    --host 0.0.0.0 \
    --port 8000 &
BACKEND_PID=$!

# Start frontend
echo -e "${GREEN}Starting frontend on http://localhost:3000${NC}"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

# Wait for both
echo ""
echo -e "${GREEN}Both servers starting. Press Ctrl+C to stop.${NC}"
echo ""
wait $BACKEND_PID $FRONTEND_PID
