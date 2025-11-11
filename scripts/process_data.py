"""
Script to process transcript data
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processing.pipeline import DataProcessingPipeline


def main():
    """Process transcript data"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process transcript data")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input directory containing transcript files"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed",
        help="Output directory for processed transcripts"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.json",
        help="File pattern to match (default: *.json)"
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Index spans to vector database"
    )
    
    args = parser.parse_args()
    
    print(f"Initializing data processing pipeline...")
    pipeline = DataProcessingPipeline(
        vector_db_path=os.getenv("VECTOR_DB_PATH", "./data/processed/vector_db")
    )
    
    print(f"Processing transcripts from: {args.input}")
    print(f"Output directory: {args.output}")
    print(f"File pattern: {args.pattern}")
    print(f"Index to vector DB: {args.index}")
    
    # Process batch
    processed = pipeline.process_batch(
        input_directory=args.input,
        output_directory=args.output,
        file_pattern=args.pattern,
        index_to_vector_db=args.index
    )
    
    print(f"\nProcessed {len(processed)} transcripts")
    print(f"Processed transcripts saved to: {args.output}")


if __name__ == "__main__":
    main()

