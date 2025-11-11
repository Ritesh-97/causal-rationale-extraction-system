#!/usr/bin/env python3
"""Quick verification that no JSON files will be created"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processing.pipeline import DataProcessingPipeline

# Count JSON files before
before = len(list(Path("data/processed").glob("*.json")))
print(f"JSON files before: {before}")

# Process just 1 file with output_directory=None
pipeline = DataProcessingPipeline(
    vector_db_path="./data/processed/vector_db",
    embedding_model="all-MiniLM-L6-v2",
    span_window_size=5
)

# Process a small batch
processed = pipeline.process_batch(
    input_directory="data/raw",
    output_directory=None,  # Should NOT create files
    file_pattern="dummy_transcripts.json",
    index_to_vector_db=True
)

# Count JSON files after
after = len(list(Path("data/processed").glob("*.json")))
print(f"JSON files after: {after}")
print(f"Processed transcripts: {len(processed)}")

if after == before:
    print("✓ SUCCESS: No JSON files were created!")
else:
    print(f"✗ ERROR: {after - before} JSON files were created!")

