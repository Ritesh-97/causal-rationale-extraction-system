#!/bin/bash
# Complete server restart script

echo "=========================================="
echo "Causal Rationale Extraction System"
echo "Server Restart Script"
echo "=========================================="
echo ""

# Kill all server processes
echo "[1/4] Killing all server processes..."
lsof -ti:8000 | xargs -r kill -9 2>/dev/null
pkill -9 -f "uvicorn" 2>/dev/null
pkill -9 -f "test_server_startup" 2>/dev/null
pkill -9 -f "src.main:app" 2>/dev/null
sleep 2
echo "✓ All processes killed"
echo ""

# Check port is free
echo "[2/4] Checking port 8000..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "✗ Port 8000 is still in use!"
    exit 1
else
    echo "✓ Port 8000 is free"
fi
echo ""

# Set environment
cd "$(dirname "$0")/.."
source venv/bin/activate
export GEMINI_API_KEY=AIzaSyDceW1Y6h66LooX7kwZnZLLiRD7ffJkalo
export DEFAULT_LLM_PROVIDER=gemini
export DEFAULT_LLM_MODEL=gemini-2.0-flash
export VECTOR_DB_PATH=./data/processed/vector_db

# Start server
echo "[3/4] Starting server..."
echo "Server will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""

python3 test_server_startup.py

