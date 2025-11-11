"""
Main causal analysis module combining pattern detection and evidence scoring
"""

from typing import List, Dict, Any, Optional
from .pattern_detector import CausalPatternDetector
from .evidence_scorer import EvidenceScorer
from ..retrieval.span_extractor import SpanExtractor


class CausalAnalyzer:
    """Main causal analysis engine"""
    
    def __init__(
        self,
        relevance_weight: float = 0.4,
        temporal_weight: float = 0.3,
        pattern_weight: float = 0.2,
        similarity_weight: float = 0.1
    ):
        self.pattern_detector = CausalPatternDetector()
        self.evidence_scorer = EvidenceScorer(
            relevance_weight=relevance_weight,
            temporal_weight=temporal_weight,
            pattern_weight=pattern_weight,
            similarity_weight=similarity_weight
        )
        self.span_extractor = SpanExtractor()
    
    def analyze_causal_spans(
        self,
        spans: List[Dict[str, Any]],
        query: str,
        event_type: Optional[str] = None,
        event_turn_index: Optional[int] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Analyze spans for causal relationships.
        
        Args:
            spans: List of dialogue spans
            query: Search query text
            event_type: Optional event type
            event_turn_index: Optional turn index of event
            top_k: Number of top spans to return
        
        Returns:
            Analyzed spans with causal scores and patterns
        """
        # Detect patterns in spans
        analyzed_spans = []
        for span in spans:
            patterns = self.pattern_detector.detect_patterns(span, event_type)
            span_copy = span.copy()
            span_copy.update(patterns)
            analyzed_spans.append(span_copy)
        
        # Detect temporal patterns if event turn index provided
        if event_turn_index is not None:
            analyzed_spans = self.pattern_detector.detect_temporal_patterns(
                analyzed_spans,
                event_turn_index
            )
        
        # Detect sequential patterns
        analyzed_spans = self.pattern_detector.detect_sequential_patterns(analyzed_spans)
        
        # Score evidence
        scored_spans = self.evidence_scorer.score_evidence(
            analyzed_spans,
            query=query,
            event_type=event_type,
            event_turn_index=event_turn_index
        )
        
        # Rank and return top-k
        ranked_spans = self.evidence_scorer.rank_evidence(scored_spans, top_k=top_k)
        
        return ranked_spans
    
    def extract_causal_rationale(
        self,
        transcript: Dict[str, Any],
        event: Dict[str, Any],
        query: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Extract causal rationale for a specific event.
        
        Args:
            transcript: Transcript dictionary
            event: Event dictionary
            query: Search query text
            top_k: Number of top spans to return
        
        Returns:
            Dictionary with causal rationale and evidence
        """
        # Extract causal spans around event
        event_type = event.get('event_type', '')
        event_turn_index = event.get('turn_index') or event.get('turn_id')
        
        causal_spans = self.span_extractor.extract_causal_spans(
            transcript=transcript,
            event=event,
            window_before=10,
            window_after=5
        )
        
        # Analyze causal spans
        analyzed_spans = self.analyze_causal_spans(
            spans=causal_spans,
            query=query,
            event_type=event_type,
            event_turn_index=event_turn_index,
            top_k=top_k
        )
        
        # Aggregate evidence
        aggregated = self.evidence_scorer.aggregate_evidence(
            analyzed_spans,
            max_spans=top_k
        )
        
        return {
            'event': event,
            'query': query,
            'causal_spans': analyzed_spans,
            'aggregated_evidence': aggregated,
            'rationale': {
                'top_spans': analyzed_spans[:top_k],
                'num_spans': len(analyzed_spans),
                'avg_evidence_score': aggregated.get('avg_evidence_score', 0.0)
            }
        }
    
    def analyze_event_patterns(
        self,
        transcript: Dict[str, Any],
        event_type: str,
        query: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze patterns for all events of a specific type.
        
        Args:
            transcript: Transcript dictionary
            event_type: Type of event to analyze
            query: Search query text
            top_k: Number of top spans to return
        
        Returns:
            Dictionary with pattern analysis and evidence
        """
        # Extract spans for all events of this type
        event_spans = self.span_extractor.extract_event_specific_spans(
            transcript=transcript,
            event_type=event_type,
            window_before=10
        )
        
        # Analyze spans
        analyzed_spans = self.analyze_causal_spans(
            spans=event_spans,
            query=query,
            event_type=event_type,
            top_k=top_k
        )
        
        # Aggregate evidence
        aggregated = self.evidence_scorer.aggregate_evidence(
            analyzed_spans,
            max_spans=top_k
        )
        
        return {
            'event_type': event_type,
            'query': query,
            'causal_spans': analyzed_spans,
            'aggregated_evidence': aggregated,
            'pattern_analysis': {
                'num_events': len([e for e in transcript.get('events', []) if e.get('event_type') == event_type]),
                'num_spans': len(analyzed_spans),
                'avg_evidence_score': aggregated.get('avg_evidence_score', 0.0)
            }
        }

