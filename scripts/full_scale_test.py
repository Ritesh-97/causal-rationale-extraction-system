"""
Full-scale testing script for the Causal Rationale Extraction System
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processing.pipeline import DataProcessingPipeline
from src.system import System
from src.evaluation.dataset_generator import DatasetGenerator
from src.evaluation.evaluator import Evaluator
import pandas as pd


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_step(step_num, total, description):
    """Print a step indicator"""
    print(f"[{step_num}/{total}] {description}...")


def main():
    """Run full-scale testing"""
    start_time = time.time()
    
    print_section("Full-Scale Testing - Causal Rationale Extraction System")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: No API key found!")
        print("Please set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY")
        print("Continuing with data processing only...\n")
        api_available = False
    else:
        api_available = True
        print("✓ API key found\n")
    
    # Step 1: Process and index data
    print_step(1, 5, "Processing and indexing transcript data")
    try:
        pipeline = DataProcessingPipeline(
            vector_db_path=os.getenv("VECTOR_DB_PATH", "./data/processed/vector_db"),
            embedding_model="all-MiniLM-L6-v2",
            span_window_size=5
        )
        
        # Process dummy data
        # Note: output_directory=None to avoid generating 10k JSON files
        # Only the vector database is needed for testing
        processed = pipeline.process_batch(
            input_directory="data/raw",
            output_directory=None,  # Don't save individual files to save disk space
            file_pattern="dummy_transcripts.json",
            index_to_vector_db=True
        )
        
        print(f"✓ Processed {len(processed)} transcripts")
        print(f"✓ Indexed dialogue spans to vector database")
        
        # Get statistics
        total_spans = sum(len(t.get('spans', [])) for t in processed)
        total_events = sum(len(t.get('events', [])) for t in processed)
        print(f"✓ Total dialogue spans: {total_spans}")
        print(f"✓ Total events: {total_events}")
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return
    
    # Step 2: Initialize system
    print_step(2, 5, "Initializing system")
    try:
        # Get LLM provider and model from environment
        llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
        if llm_provider == "gemini":
            llm_model = os.getenv("DEFAULT_LLM_MODEL", "gemini-2.0-flash")
        elif llm_provider == "openai":
            llm_model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
        elif llm_provider == "anthropic":
            llm_model = os.getenv("DEFAULT_LLM_MODEL", "claude-3-opus-20240229")
        else:
            llm_model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
        
        system = System(
            vector_db_path=os.getenv("VECTOR_DB_PATH", "./data/processed/vector_db"),
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        print("✓ System initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return
    
    # Step 3: Test basic queries
    if api_available:
        print_step(3, 5, "Testing basic queries")
        test_queries = [
            "Why are escalations happening on calls?",
            "What causes refund requests?",
            "What leads to customer churn?",
        ]
        
        results = []
        for i, query in enumerate(test_queries, 1):
            try:
                print(f"  Testing query {i}: {query[:50]}...")
                result = system.process_query(
                    query=query,
                    conversation_id=f"test_{i}"
                )
                
                response = result.get('response', 'No response')
                evidence_count = result.get('metadata', {}).get('evidence_count', 0)
                
                results.append({
                    'query': query,
                    'response_length': len(response),
                    'evidence_count': evidence_count,
                    'status': 'success'
                })
                
                print(f"    ✓ Response length: {len(response)} chars")
                print(f"    ✓ Evidence count: {evidence_count}")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                results.append({
                    'query': query,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Summary
        successful = sum(1 for r in results if r.get('status') == 'success')
        print(f"\n✓ Successfully processed {successful}/{len(test_queries)} queries")
    
    # Step 4: Test follow-up queries
    if api_available:
        print_step(4, 5, "Testing follow-up queries")
        try:
            # Initial query
            conv_id = "followup_test"
            query1 = "Why are escalations happening on calls?"
            print(f"  Initial query: {query1}")
            
            result1 = system.process_query(
                query=query1,
                conversation_id=conv_id
            )
            print(f"    ✓ Initial response generated")
            
            # Follow-up query
            query2 = "What patterns lead to these escalations?"
            print(f"  Follow-up query: {query2}")
            
            result2 = system.process_followup(
                query=query2,
                conversation_id=conv_id
            )
            print(f"    ✓ Follow-up response generated")
            print(f"    ✓ Context used: {result2.get('context_used', False)}")
            
        except Exception as e:
            print(f"  ❌ Error testing follow-ups: {e}")
    
    # Step 5: Generate query dataset
    if api_available:
        print_step(5, 5, "Generating query dataset")
        try:
            generator = DatasetGenerator(system=system)
            
            print("  Generating queries for event types: escalation, refund, churn")
            dataset = generator.generate_dataset(
                event_types=['escalation', 'refund', 'churn'],
                num_queries_per_type=10,  # 10 per type = 30 initial + follow-ups
                include_followups=True,
                output_path="data/queries/dataset.csv"
            )
            
            print(f"  ✓ Generated dataset with {len(dataset)} queries")
            print(f"  ✓ Saved to: data/queries/dataset.csv")
            
            # Statistics
            task1_count = len(dataset[dataset['Task'] == 'task1'])
            task2_count = len(dataset[dataset['Task'] == 'task2'])
            print(f"  ✓ Task 1 queries: {task1_count}")
            print(f"  ✓ Task 2 queries: {task2_count}")
            
            # Event type distribution
            for event_type in ['escalation', 'refund', 'churn']:
                count = len(dataset[dataset['Event_Type'] == event_type])
                print(f"  ✓ {event_type.capitalize()} queries: {count}")
            
        except Exception as e:
            print(f"  ❌ Error generating dataset: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    elapsed_time = time.time() - start_time
    print_section("Testing Complete")
    print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nNext steps:")
    print("1. Review generated dataset: data/queries/dataset.csv")
    print("2. Run evaluation: python -c 'from src.evaluation.evaluator import Evaluator; from src.system import System; e = Evaluator(System()); print(\"Evaluator ready\")'")
    print("3. Start API server: python -m src.main")
    print("4. Test API endpoints with curl or Postman")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

