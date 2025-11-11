"""
Semantic search implementation for dialogue span retrieval
"""

from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class SemanticSearch:
    """Semantic search for dialogue spans"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embedding_model_name = embedding_model
        self.embedding_model = SentenceTransformer(embedding_model)
    
    def search(
        self,
        query: str,
        spans: List[Dict[str, Any]],
        top_k: int = 10,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search over dialogue spans.
        
        Args:
            query: Search query text
            spans: List of dialogue span dictionaries with 'text' field
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
        
        Returns:
            List of top-k spans with similarity scores, sorted by relevance
        """
        if not spans:
            return []
        
        # Get query embedding
        query_embedding = self.embedding_model.encode(
            query,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        # Get span embeddings
        span_texts = [span.get('text', '') for span in spans]
        span_embeddings = self.embedding_model.encode(
            span_texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        # Calculate similarities
        similarities = cosine_similarity(
            query_embedding.reshape(1, -1),
            span_embeddings
        )[0]
        
        # Create results with scores
        results = []
        for i, span in enumerate(spans):
            similarity = float(similarities[i])
            
            if similarity >= threshold:
                result = span.copy()
                result['similarity_score'] = similarity
                results.append(result)
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Return top-k
        return results[:top_k]
    
    def batch_search(
        self,
        queries: List[str],
        spans: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[List[Dict[str, Any]]]:
        """Perform batch semantic search"""
        results = []
        for query in queries:
            query_results = self.search(query, spans, top_k=top_k)
            results.append(query_results)
        return results

