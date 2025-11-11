#!/bin/bash
# Start the API server for Causal Rationale Extraction System

cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export GEMINI_API_KEY=AIzaSyDceW1Y6h66LooX7kwZnZLLiRD7ffJkalo
export DEFAULT_LLM_PROVIDER=gemini
export DEFAULT_LLM_MODEL=gemini-2.0-flash
export VECTOR_DB_PATH=./data/processed/vector_db

# Kill existing server if running
pkill -f "uvicorn.*main:app" 2>/dev/null
sleep 2

# Start server
echo "Starting API server on http://0.0.0.0:8000"
echo "API documentation: http://localhost:8000/docs"
echo "Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

