"""
Follow-up question processing for Task 2
"""

from typing import Dict, Any, Optional, List
from .context_manager import ContextManager
from ..query_processing.query_parser import QueryParser
from ..retrieval.retrieval_pipeline import RetrievalPipeline
from ..causal_analysis.causal_analyzer import CausalAnalyzer
from ..explanation_generation.explanation_generator import ExplanationGenerator


class FollowUpProcessor:
    """Process follow-up queries with context awareness"""
    
    def __init__(
        self,
        context_manager: ContextManager,
        retrieval_pipeline: RetrievalPipeline,
        causal_analyzer: CausalAnalyzer,
        explanation_generator: ExplanationGenerator
    ):
        self.context_manager = context_manager
        self.query_parser = QueryParser()
        self.retrieval_pipeline = retrieval_pipeline
        self.causal_analyzer = causal_analyzer
        self.explanation_generator = explanation_generator
    
    def process_followup(
        self,
        query: str,
        conversation_id: str,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process a follow-up query with context from previous conversation.
        
        Args:
            query: Follow-up query text
            conversation_id: Conversation ID for context tracking
            context: Optional explicit context (if not provided, retrieved from conversation)
        
        Returns:
            Dictionary with contextual response and evidence
        """
        # Get conversation context
        if context is None:
            conversation = self.context_manager.get_context(conversation_id)
            if conversation:
                context = [
                    {
                        'query': turn.query,
                        'response': turn.response,
                        'metadata': turn.metadata
                    }
                    for turn in conversation.get_recent_turns(3)
                ]
            else:
                context = []
        
        # Determine if this is a follow-up
        is_followup = self.context_manager.is_followup(query, conversation_id)
        
        # Enhance query with context
        enhanced_query = self._enhance_query_with_context(query, context)
        
        # Parse query
        parsed_query = self.query_parser.parse_query(enhanced_query)
        
        # Retrieve with context
        retrieved_spans = self.retrieval_pipeline.retrieve_with_context(
            query=enhanced_query,
            context=context,
            top_k=20,
            rerank_top_k=10
        )
        
        # Analyze causal patterns
        analyzed_spans = self.causal_analyzer.analyze_causal_spans(
            spans=retrieved_spans,
            query=enhanced_query,
            event_type=parsed_query.get('event_type'),
            top_k=10
        )
        
        # Generate contextual explanation
        context_summary = self.context_manager.get_context_summary(conversation_id)
        
        explanation_result = self.explanation_generator.llm_generator.generate_with_citations(
            query=enhanced_query,
            evidence=analyzed_spans,
            context=context_summary
        )
        
        # Format response
        response = {
            'query': query,
            'enhanced_query': enhanced_query,
            'is_followup': is_followup,
            'parsed_query': parsed_query,
            'explanation': explanation_result['explanation'],
            'evidence': analyzed_spans,
            'citations': explanation_result['citations'],
            'evidence_count': len(analyzed_spans),
            'context_used': len(context) > 0,
            'context_turns': len(context)
        }
        
        # Add turn to conversation
        self.context_manager.add_turn(
            conversation_id=conversation_id,
            query=query,
            response=explanation_result['explanation'],
            metadata={
                'is_followup': is_followup,
                'evidence_count': len(analyzed_spans),
                'enhanced_query': enhanced_query
            }
        )
        
        return response
    
    def _enhance_query_with_context(
        self,
        query: str,
        context: List[Dict[str, Any]]
    ) -> str:
        """Enhance query with context from previous conversation"""
        if not context:
            return query
        
        # Extract relevant information from context
        context_queries = [item.get('query', '') for item in context]
        context_responses = [item.get('response', '')[:200] for item in context]  # Truncate
        
        # Build enhanced query
        enhanced_parts = []
        
        # Add context summary
        if context_queries:
            enhanced_parts.append("Previous queries: " + "; ".join(context_queries[-2:]))
        
        # Add current query
        enhanced_parts.append(f"Current query: {query}")
        
        enhanced_query = ". ".join(enhanced_parts)
        
        return enhanced_query
    
    def format_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format response for API output.
        
        Args:
            result: Result dictionary from process_followup
        
        Returns:
            Formatted response dictionary
        """
        # Format evidence for response
        formatted_evidence = []
        for i, span in enumerate(result['evidence'][:10], 1):
            formatted_evidence.append({
                'evidence_id': i,
                'span_id': span.get('span_id', f'evidence_{i}'),
                'text': span.get('text', '')[:500],
                'transcript_id': span.get('metadata', {}).get('transcript_id', 'unknown'),
                'turn_ids': span.get('turn_ids', []),
                'evidence_score': span.get('evidence_score', 0.0)
            })
        
        return {
            'response': result['explanation'],
            'evidence': formatted_evidence,
            'citations': result['citations'],
            'metadata': {
                'query': result['query'],
                'enhanced_query': result['enhanced_query'],
                'is_followup': result['is_followup'],
                'event_type': result['parsed_query'].get('event_type'),
                'context_used': result['context_used'],
                'context_turns': result['context_turns'],
                'evidence_count': result['evidence_count']
            }
        }

