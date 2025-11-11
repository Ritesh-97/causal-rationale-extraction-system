"""
Task 1: Query-driven evidence-based causal explanation processor
"""

from typing import Dict, Any, Optional
from .query_parser import QueryParser
from ..retrieval.retrieval_pipeline import RetrievalPipeline
from ..causal_analysis.causal_analyzer import CausalAnalyzer
from ..explanation_generation.explanation_generator import ExplanationGenerator


class Task1Processor:
    """Process queries for Task 1: Evidence-based causal explanations"""
    
    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline,
        causal_analyzer: CausalAnalyzer,
        explanation_generator: ExplanationGenerator
    ):
        self.query_parser = QueryParser()
        self.retrieval_pipeline = retrieval_pipeline
        self.causal_analyzer = causal_analyzer
        self.explanation_generator = explanation_generator
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and generate evidence-based causal explanation.
        
        Args:
            query: Natural language query about business events
        
        Returns:
            Dictionary with query analysis, explanation, and evidence
        """
        # Parse query
        parsed_query = self.query_parser.parse_query(query)
        
        # Generate explanation
        explanation_result = self.explanation_generator.generate_structured_explanation(
            query=query,
            top_k=10,
            event_type=parsed_query.get('event_type')
        )
        
        # Format response
        response = {
            'query': query,
            'parsed_query': parsed_query,
            'explanation': explanation_result['explanation'],
            'summary': explanation_result['summary'],
            'key_factors': explanation_result['key_factors'],
            'causal_mechanisms': explanation_result['causal_mechanisms'],
            'evidence': explanation_result['evidence'],
            'citations': explanation_result['citations'],
            'evidence_count': explanation_result['evidence_count'],
            'full_explanation': explanation_result['full_explanation']
        }
        
        return response
    
    def format_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format response for API output.
        
        Args:
            result: Result dictionary from process_query
        
        Returns:
            Formatted response dictionary
        """
        # Format evidence for response
        formatted_evidence = []
        for i, span in enumerate(result['evidence'][:10], 1):
            formatted_evidence.append({
                'evidence_id': i,
                'span_id': span.get('span_id', f'evidence_{i}'),
                'text': span.get('text', '')[:500],  # Truncate for display
                'transcript_id': span.get('metadata', {}).get('transcript_id', 'unknown'),
                'turn_ids': span.get('turn_ids', []),
                'evidence_score': span.get('evidence_score', 0.0),
                'metadata': {
                    'speakers': span.get('speakers', []),
                    'temporal_relation': span.get('temporal_relation', 'unknown'),
                    'pattern_score': span.get('pattern_score', 0.0)
                }
            })
        
        return {
            'response': result['full_explanation'],
            'summary': result['summary'],
            'key_factors': result['key_factors'],
            'causal_mechanisms': result['causal_mechanisms'],
            'evidence': formatted_evidence,
            'citations': result['citations'],
            'metadata': {
                'query': result['query'],
                'event_type': result['parsed_query'].get('event_type'),
                'intent': result['parsed_query'].get('intent'),
                'evidence_count': result['evidence_count']
            }
        }

