#!/usr/bin/env python3
"""
Test script for the Causal Rationale Extraction System API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("=" * 70)
    print("Testing Health Check")
    print("=" * 70)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_query(query, conversation_id="test"):
    """Test query endpoint"""
    print("=" * 70)
    print(f"Testing Query: {query}")
    print("=" * 70)
    
    payload = {
        "query": query,
        "conversation_id": conversation_id
    }
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/query",
        json=payload,
        timeout=120
    )
    elapsed_time = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response length: {len(data.get('response', ''))} characters")
        print(f"Evidence count: {len(data.get('evidence', []))}")
        print(f"Conversation ID: {data.get('conversation_id')}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        print("\nResponse preview:")
        print(data.get('response', '')[:500] + "..." if len(data.get('response', '')) > 500 else data.get('response', ''))
        print("\nEvidence preview (first 2 items):")
        for i, evidence in enumerate(data.get('evidence', [])[:2], 1):
            print(f"  [{i}] {evidence.get('text', '')[:200]}...")
    else:
        print(f"Error: {response.text}")
    print()
    
    return response.json() if response.status_code == 200 else None

def test_followup(query, conversation_id):
    """Test follow-up query endpoint"""
    print("=" * 70)
    print(f"Testing Follow-up Query: {query}")
    print("=" * 70)
    
    payload = {
        "query": query,
        "conversation_id": conversation_id
    }
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/query/follow-up",
        json=payload,
        timeout=120
    )
    elapsed_time = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response length: {len(data.get('response', ''))} characters")
        print(f"Evidence count: {len(data.get('evidence', []))}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        print("\nResponse preview:")
        print(data.get('response', '')[:500] + "..." if len(data.get('response', '')) > 500 else data.get('response', ''))
    else:
        print(f"Error: {response.text}")
    print()
    
    return response.json() if response.status_code == 200 else None

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("Causal Rationale Extraction System - API Test Suite")
    print("=" * 70 + "\n")
    
    # Test 1: Health check
    try:
        test_health()
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return
    
    # Test 2: Task 1 - Initial queries
    test_queries = [
        "Why are escalations happening on calls?",
        "What causes refund requests?",
        "What leads to customer churn?"
    ]
    
    conversation_ids = []
    for i, query in enumerate(test_queries, 1):
        try:
            conv_id = f"test_{i:03d}"
            result = test_query(query, conversation_id=conv_id)
            if result:
                conversation_ids.append(conv_id)
            time.sleep(2)  # Rate limiting
        except Exception as e:
            print(f"✗ Query test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Test 3: Task 2 - Follow-up queries
    if conversation_ids:
        followup_queries = [
            "What patterns lead to these escalations?",
            "How can we prevent these refund requests?",
            "What are the warning signs of customer churn?"
        ]
        
        for i, (conv_id, query) in enumerate(zip(conversation_ids, followup_queries)):
            try:
                test_followup(query, conversation_id=conv_id)
                time.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"✗ Follow-up test failed: {e}")
                import traceback
                traceback.print_exc()
    
    print("=" * 70)
    print("Test Suite Complete")
    print("=" * 70)

if __name__ == "__main__":
    main()

