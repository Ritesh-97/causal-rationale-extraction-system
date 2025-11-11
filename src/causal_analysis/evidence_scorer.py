"""
Evidence scoring and ranking for causal explanations
"""

from typing import List, Dict, Any, Optional
import numpy as np


class EvidenceScorer:
    """Score and rank evidence spans for causal explanations"""
    
    def __init__(
        self,
        relevance_weight: float = 0.4,
        temporal_weight: float = 0.3,
        pattern_weight: float = 0.2,
        similarity_weight: float = 0.1
    ):
        self.relevance_weight = relevance_weight
        self.temporal_weight = temporal_weight
        self.pattern_weight = pattern_weight
        self.similarity_weight = similarity_weight
    
    def score_evidence(
        self,
        spans: List[Dict[str, Any]],
        query: str,
        event_type: Optional[str] = None,
        event_turn_index: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Score evidence spans for causal explanation.
        
        Args:
            spans: List of dialogue spans with metadata
            query: Search query text
            event_type: Optional event type
            event_turn_index: Optional turn index of event
        
        Returns:
            Spans with evidence scores, sorted by score
        """
        scored_spans = []
        
        for span in spans:
            # Extract scores from span metadata
            relevance_score = span.get('relevance_score', span.get('combined_score', 0.0))
            similarity_score = span.get('similarity_score', 0.0)
            pattern_score = span.get('pattern_score', 0.0)
            temporal_score = span.get('temporal_score', 0.5)  # Default if not calculated
            
            # Calculate evidence score
            evidence_score = (
                self.relevance_weight * relevance_score +
                self.temporal_weight * temporal_score +
                self.pattern_weight * pattern_score +
                self.similarity_weight * similarity_score
            )
            
            span_copy = span.copy()
            span_copy['evidence_score'] = evidence_score
            span_copy['evidence_components'] = {
                'relevance': relevance_score,
                'temporal': temporal_score,
                'pattern': pattern_score,
                'similarity': similarity_score
            }
            
            scored_spans.append(span_copy)
        
        # Sort by evidence score (descending)
        scored_spans.sort(key=lambda x: x.get('evidence_score', 0.0), reverse=True)
        
        return scored_spans
    
    def rank_evidence(
        self,
        spans: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank evidence spans by score.
        
        Args:
            spans: List of scored spans
            top_k: Number of top spans to return
        
        Returns:
            Top-k ranked spans
        """
        # Ensure spans are scored
        if not all('evidence_score' in span for span in spans):
            # Score spans if not already scored
            spans = self.score_evidence(spans, query="")
        
        # Sort by evidence score
        ranked = sorted(
            spans,
            key=lambda x: x.get('evidence_score', 0.0),
            reverse=True
        )
        
        # Return top-k if specified
        if top_k is not None:
            return ranked[:top_k]
        
        return ranked
    
    def aggregate_evidence(
        self,
        spans: List[Dict[str, Any]],
        max_spans: int = 10
    ) -> Dict[str, Any]:
        """
        Aggregate evidence from multiple spans.
        
        Args:
            spans: List of evidence spans
            max_spans: Maximum number of spans to aggregate
        
        Returns:
            Aggregated evidence dictionary
        """
        # Take top spans
        top_spans = spans[:max_spans]
        
        # Aggregate text
        aggregated_text = ' '.join([
            span.get('text', '')
            for span in top_spans
        ])
        
        # Aggregate metadata
        all_turn_ids = []
        all_speakers = []
        transcript_ids = set()
        
        for span in top_spans:
            all_turn_ids.extend(span.get('turn_ids', []))
            all_speakers.extend(span.get('speakers', []))
            transcript_id = span.get('transcript_id') or span.get('metadata', {}).get('transcript_id')
            if transcript_id:
                transcript_ids.add(transcript_id)
        
        # Calculate aggregate scores
        avg_evidence_score = np.mean([
            span.get('evidence_score', 0.0)
            for span in top_spans
        ]) if top_spans else 0.0
        
        return {
            'text': aggregated_text,
            'spans': top_spans,
            'turn_ids': list(set(all_turn_ids)),
            'speakers': list(set(all_speakers)),
            'transcript_ids': list(transcript_ids),
            'num_spans': len(top_spans),
            'avg_evidence_score': float(avg_evidence_score),
            'metadata': {
                'aggregation_method': 'top_k',
                'max_spans': max_spans
            }
        }
    
    def filter_evidence(
        self,
        spans: List[Dict[str, Any]],
        min_score: float = 0.3,
        max_spans: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter evidence spans by score threshold.
        
        Args:
            spans: List of scored spans
            min_score: Minimum evidence score threshold
            max_spans: Maximum number of spans to return
        
        Returns:
            Filtered spans
        """
        # Filter by score
        filtered = [
            span for span in spans
            if span.get('evidence_score', 0.0) >= min_score
        ]
        
        # Limit to max_spans if specified
        if max_spans is not None:
            filtered = filtered[:max_spans]
        
        return filtered

