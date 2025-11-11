#!/usr/bin/env python3
"""
Quick Start Script for Causal Rationale Extraction System
Demonstrates basic usage of the system
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.system import System


def main():
    """Quick start demonstration"""
    print("=" * 60)
    print("Causal Rationale Extraction System - Quick Start")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  Warning: No API key found in environment variables!")
        print("Please set one of the following:")
        print("  - GEMINI_API_KEY")
        print("  - OPENAI_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        print("\nOr create a .env file with your API key.")
        print("\nContinuing with demo (may fail if no API key)...\n")
    
    try:
        # Initialize system
        print("Initializing system...")
        system = System()
        print("✓ System initialized\n")
        
        # Example 1: Simple query
        print("-" * 60)
        print("Example 1: Simple Query (Task 1)")
        print("-" * 60)
        query1 = "Why are escalations happening on calls?"
        print(f"Query: {query1}\n")
        
        try:
            result1 = system.process_query(
                query=query1,
                conversation_id="demo_1"
            )
            print("Response:")
            print(result1.get('response', 'No response generated')[:300] + "...")
            print(f"\nEvidence count: {result1.get('metadata', {}).get('evidence_count', 0)}")
        except Exception as e:
            print(f"Error: {e}")
            print("Note: This requires processed transcript data in the vector database.")
            print("Run: python scripts/process_data.py --input data/raw --index")
        
        # Example 2: Follow-up query
        print("\n" + "-" * 60)
        print("Example 2: Follow-Up Query (Task 2)")
        print("-" * 60)
        query2 = "What patterns lead to these escalations?"
        print(f"Query: {query2}\n")
        
        try:
            result2 = system.process_followup(
                query=query2,
                conversation_id="demo_1"
            )
            print("Response:")
            print(result2.get('explanation', 'No response generated')[:300] + "...")
            print(f"\nContext used: {result2.get('context_used', False)}")
        except Exception as e:
            print(f"Error: {e}")
            print("Note: This requires a previous query in the conversation.")
        
        print("\n" + "=" * 60)
        print("Quick Start Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Process your transcript data:")
        print("   python scripts/process_data.py --input data/raw --index")
        print("\n2. Start the API server:")
        print("   python -m src.main")
        print("\n3. Generate query dataset:")
        print("   python scripts/generate_dataset.py")
        print("\n4. See USAGE_GUIDE.md for detailed instructions")
        
    except Exception as e:
        print(f"\n❌ Error initializing system: {e}")
        print("\nTroubleshooting:")
        print("1. Check that all dependencies are installed: pip install -r requirements.txt")
        print("2. Verify API key is set in .env file")
        print("3. Check that data directories exist: data/raw, data/processed")


if __name__ == "__main__":
    main()

