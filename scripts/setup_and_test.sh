#!/bin/bash
# Setup and full-scale testing script

set -e

echo "============================================================"
echo "Full-Scale Testing Setup and Execution"
echo "============================================================"
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
python3 --version || { echo "Error: Python 3 not found"; exit 1; }
echo "✓ Python found"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[2/5] Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "[2/5] Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "[4/5] Installing dependencies..."
echo "This may take a few minutes..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check for API key
echo "[5/5] Checking for API key..."
if [ -f ".env" ]; then
    if grep -q "GEMINI_API_KEY\|OPENAI_API_KEY\|ANTHROPIC_API_KEY" .env; then
        echo "✓ API key found in .env file"
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo "⚠️  Warning: .env file exists but no API key found"
    fi
else
    echo "⚠️  Warning: .env file not found"
    echo "   Create .env file with your API key"
fi
echo ""

# Run full-scale test
echo "============================================================"
echo "Starting Full-Scale Testing"
echo "============================================================"
echo ""

python3 scripts/full_scale_test.py

echo ""
echo "============================================================"
echo "Testing Complete"
echo "============================================================"

