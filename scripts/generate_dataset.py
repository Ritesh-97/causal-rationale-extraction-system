"""
Script to generate query dataset
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.dataset_generator import DatasetGenerator
from src.system import System


def main():
    """Generate query dataset"""
    print("Initializing system...")
    system = System()
    
    print("Initializing dataset generator...")
    generator = DatasetGenerator(system=system)
    
    # Event types
    event_types = ['escalation', 'refund', 'churn', 'complaint']
    
    # Generate dataset
    print(f"Generating dataset for event types: {event_types}")
    print("This may take a while...")
    
    dataset = generator.generate_dataset(
        event_types=event_types,
        num_queries_per_type=15,  # 15 queries per type = 60 total, plus follow-ups
        include_followups=True,
        output_path="data/queries/dataset.csv"
    )
    
    print(f"\nDataset generated with {len(dataset)} queries")
    print(f"Saved to: data/queries/dataset.csv")
    
    # Print statistics
    print("\nDataset Statistics:")
    print(f"Total queries: {len(dataset)}")
    print(f"Task 1 queries: {len(dataset[dataset['Task'] == 'task1'])}")
    print(f"Task 2 queries: {len(dataset[dataset['Task'] == 'task2'])}")
    print(f"By event type:")
    for event_type in event_types:
        count = len(dataset[dataset['Event_Type'] == event_type])
        print(f"  {event_type}: {count}")
    
    print(f"\nBy difficulty:")
    for difficulty in dataset['Difficulty'].unique():
        count = len(dataset[dataset['Difficulty'] == difficulty])
        print(f"  {difficulty}: {count}")


if __name__ == "__main__":
    main()

