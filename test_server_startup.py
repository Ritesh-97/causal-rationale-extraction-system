#!/usr/bin/env python3
"""Test server startup without blocking"""
import os
import sys
from pathlib import Path

# Set environment
os.environ['GEMINI_API_KEY'] = 'AIzaSyDceW1Y6h66LooX7kwZnZLLiRD7ffJkalo'
os.environ['DEFAULT_LLM_PROVIDER'] = 'gemini'
os.environ['DEFAULT_LLM_MODEL'] = 'gemini-2.0-flash'

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("Testing Server Startup")
print("=" * 70)

# Test 1: Import app
print("\n[1/3] Testing app import...")
try:
    from src.main import app
    print("✓ App imported successfully")
except Exception as e:
    print(f"✗ Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Test system loading (lazy)
print("\n[2/3] Testing system initialization...")
try:
    from src.system import get_system
    print("✓ System module imported")
    print("  (System will load on first request)")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Start server
print("\n[3/3] Starting server...")
print("=" * 70)
print("Server will be available at:")
print("  - API: http://localhost:8000")
print("  - Docs: http://localhost:8000/docs")
print("  - Health: http://localhost:8000/health")
print("=" * 70)
print("\nStarting uvicorn server...\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

