"""
Reranking mechanism for dialogue spans
"""

from typing import List, Dict, Any, Optional
from sentence_transformers import CrossEncoder
import numpy as np


class Reranker:
    """Rerank retrieved dialogue spans using cross-encoder"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = CrossEncoder(model_name, max_length=512)
    
    def rerank(
        self,
        query: str,
        spans: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank dialogue spans based on query relevance.
        
        Args:
            query: Search query text
            spans: List of dialogue span dictionaries with 'text' field
            top_k: Number of top results to return (None for all)
        
        Returns:
            Reranked list of spans with relevance scores
        """
        if not spans:
            return []
        
        # Prepare query-span pairs
        pairs = [
            [query, span.get('text', '')]
            for span in spans
        ]
        
        # Get relevance scores
        scores = self.model.predict(pairs)
        
        # Add scores to spans
        results = []
        for i, span in enumerate(spans):
            result = span.copy()
            result['relevance_score'] = float(scores[i])
            results.append(result)
        
        # Sort by relevance (descending)
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top-k if specified
        if top_k is not None:
            return results[:top_k]
        
        return results
    
    def rerank_with_weights(
        self,
        query: str,
        spans: List[Dict[str, Any]],
        similarity_scores: Optional[List[float]] = None,
        top_k: Optional[int] = None,
        similarity_weight: float = 0.3,
        relevance_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Rerank spans using weighted combination of similarity and relevance.
        
        Args:
            query: Search query text
            spans: List of dialogue span dictionaries
            similarity_scores: Optional pre-computed similarity scores
            top_k: Number of top results to return
            similarity_weight: Weight for similarity score
            relevance_weight: Weight for relevance score
        
        Returns:
            Reranked list of spans with combined scores
        """
        # Get relevance scores
        reranked = self.rerank(query, spans, top_k=None)
        
        # Combine scores if similarity scores provided
        if similarity_scores and len(similarity_scores) == len(spans):
            # Create mapping from span to similarity score
            span_to_similarity = {
                id(span): score
                for span, score in zip(spans, similarity_scores)
            }
            
            # Combine scores
            for result in reranked:
                span_id = id([s for s in spans if s.get('text') == result.get('text')][0])
                similarity = span_to_similarity.get(span_id, 0.0)
                relevance = result.get('relevance_score', 0.0)
                
                # Normalize scores to [0, 1] if needed
                combined_score = (
                    similarity_weight * similarity +
                    relevance_weight * relevance
                )
                result['combined_score'] = combined_score
                result['similarity_score'] = similarity
        else:
            # Use relevance score as combined score
            for result in reranked:
                result['combined_score'] = result.get('relevance_score', 0.0)
        
        # Sort by combined score
        reranked.sort(key=lambda x: x.get('combined_score', 0.0), reverse=True)
        
        # Return top-k if specified
        if top_k is not None:
            return reranked[:top_k]
        
        return reranked

