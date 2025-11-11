"""
Dataset generation for queries and system outputs
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import json
from pathlib import Path
from .query_simulator import QuerySimulator
from .query_categorizer import QueryCategorizer
from ..system import System


class DatasetGenerator:
    """Generate query dataset with system outputs"""
    
    def __init__(
        self,
        system: Optional[System] = None,
        query_simulator: Optional[QuerySimulator] = None,
        categorizer: Optional[QueryCategorizer] = None
    ):
        self.system = system or System()
        self.query_simulator = query_simulator or QuerySimulator()
        self.categorizer = categorizer or QueryCategorizer()
    
    def generate_dataset(
        self,
        event_types: List[str],
        num_queries_per_type: int = 10,
        include_followups: bool = True,
        output_path: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Generate a complete query dataset with system outputs.
        
        Args:
            event_types: List of event types
            num_queries_per_type: Number of queries per event type
            include_followups: Whether to include follow-up queries
            output_path: Optional path to save dataset
        
        Returns:
            DataFrame with queries and system outputs
        """
        # Generate initial queries
        initial_queries = self.query_simulator.generate_queries(
            event_types=event_types,
            num_queries_per_type=num_queries_per_type
        )
        
        # Categorize queries
        categorized_queries = self.categorizer.categorize_batch(initial_queries)
        
        # Generate system outputs
        dataset_rows = []
        conversation_id = None
        
        for query_dict in categorized_queries:
            query = query_dict['query']
            query_id = query_dict.get('query_id', f"query_{len(dataset_rows)}")
            
            # Process query with system
            try:
                result = self.system.process_query(
                    query=query,
                    conversation_id=conversation_id
                )
                
                # Extract conversation ID
                conversation_id = result.get('metadata', {}).get('conversation_id', conversation_id)
                
                # Format output
                system_output = result.get('response', '')
                
                # Create dataset row
                row = {
                    'Query_Id': query_id,
                    'Query': query,
                    'Query_Category': self._format_category(query_dict),
                    'System_Output': system_output,
                    'Remarks': self._generate_remarks(query_dict, result),
                    'Task': query_dict.get('task', 'task1'),
                    'Difficulty': query_dict.get('difficulty', 'simple'),
                    'Use_Case': query_dict.get('use_case', 'general'),
                    'Event_Type': query_dict.get('event_type', 'unknown'),
                    'Is_Followup': query_dict.get('is_followup', False),
                    'Evidence_Count': result.get('metadata', {}).get('evidence_count', 0)
                }
                
                dataset_rows.append(row)
                
                # Generate follow-ups if requested
                if include_followups and not query_dict.get('is_followup', False):
                    followups = self.query_simulator.generate_followup_queries(
                        initial_query=query,
                        initial_response=system_output,
                        num_followups=2
                    )
                    
                    for followup in followups:
                        try:
                            followup_result = self.system.process_followup(
                                query=followup['query'],
                                conversation_id=conversation_id
                            )
                            
                            followup_row = {
                                'Query_Id': followup.get('query_id', f"followup_{len(dataset_rows)}"),
                                'Query': followup['query'],
                                'Query_Category': self._format_category(followup),
                                'System_Output': followup_result.get('explanation', ''),
                                'Remarks': self._generate_remarks(followup, followup_result),
                                'Task': 'task2',
                                'Difficulty': self.categorizer.categorize_query(followup['query'], is_followup=True).get('difficulty', 'simple'),
                                'Use_Case': self.categorizer.categorize_query(followup['query'], is_followup=True).get('use_case', 'general'),
                                'Event_Type': query_dict.get('event_type', 'unknown'),
                                'Is_Followup': True,
                                'Evidence_Count': followup_result.get('evidence_count', 0)
                            }
                            
                            dataset_rows.append(followup_row)
                        except Exception as e:
                            print(f"Error processing follow-up: {e}")
                            continue
            
            except Exception as e:
                print(f"Error processing query {query_id}: {e}")
                # Add row with error
                row = {
                    'Query_Id': query_id,
                    'Query': query,
                    'Query_Category': self._format_category(query_dict),
                    'System_Output': f"Error: {str(e)}",
                    'Remarks': f"Failed to process query: {str(e)}",
                    'Task': query_dict.get('task', 'task1'),
                    'Difficulty': query_dict.get('difficulty', 'simple'),
                    'Use_Case': query_dict.get('use_case', 'general'),
                    'Event_Type': query_dict.get('event_type', 'unknown'),
                    'Is_Followup': False,
                    'Evidence_Count': 0
                }
                dataset_rows.append(row)
                continue
        
        # Create DataFrame
        df = pd.DataFrame(dataset_rows)
        
        # Save if path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)
            print(f"Dataset saved to {output_path}")
        
        return df
    
    def _format_category(self, query_dict: Dict[str, Any]) -> str:
        """Format category string for query"""
        parts = []
        
        if query_dict.get('category'):
            parts.append(query_dict['category'])
        
        if query_dict.get('task'):
            parts.append(query_dict['task'])
        
        if query_dict.get('difficulty'):
            parts.append(query_dict['difficulty'])
        
        if query_dict.get('use_case'):
            parts.append(query_dict['use_case'])
        
        return ' | '.join(parts) if parts else 'general'
    
    def _generate_remarks(
        self,
        query_dict: Dict[str, Any],
        result: Dict[str, Any]
    ) -> str:
        """Generate remarks for dataset entry"""
        remarks = []
        
        # Add categorization info
        if query_dict.get('task'):
            remarks.append(f"Task: {query_dict['task']}")
        
        if query_dict.get('difficulty'):
            remarks.append(f"Difficulty: {query_dict['difficulty']}")
        
        # Add evidence info
        evidence_count = result.get('metadata', {}).get('evidence_count', 0)
        if evidence_count > 0:
            remarks.append(f"Evidence spans: {evidence_count}")
        
        # Add follow-up info
        if query_dict.get('is_followup'):
            remarks.append("Follow-up query")
        
        return '; '.join(remarks) if remarks else ''

