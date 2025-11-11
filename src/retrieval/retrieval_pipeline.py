"""
Main retrieval pipeline combining semantic search, reranking, and span extraction
"""

from typing import List, Dict, Any, Optional
from .semantic_search import SemanticSearch
from .reranker import Reranker
from .span_extractor import SpanExtractor
from ..data_processing.vector_store import VectorStore


class RetrievalPipeline:
    """End-to-end retrieval pipeline"""
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        use_reranking: bool = True
    ):
        self.vector_store = vector_store
        self.semantic_search = SemanticSearch(embedding_model=embedding_model)
        self.reranker = Reranker(model_name=reranker_model) if use_reranking else None
        self.span_extractor = SpanExtractor()
        self.use_reranking = use_reranking
    
    def retrieve(
        self,
        query: str,
        top_k: int = 20,
        rerank_top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant dialogue spans for a query.
        
        Args:
            query: Search query text
            top_k: Number of initial results to retrieve
            rerank_top_k: Number of results after reranking
            filter_dict: Optional metadata filters
        
        Returns:
            List of retrieved and reranked dialogue spans
        """
        # Retrieve from vector store if available
        if self.vector_store:
            results = self.vector_store.search(
                query=query,
                n_results=top_k,
                filter_dict=filter_dict
            )
            
            # Convert to span format
            spans = [
                {
                    'text': r['text'],
                    'span_id': r['span_id'],
                    'metadata': r['metadata'],
                    'similarity_score': 1.0 - r.get('distance', 0.0) if r.get('distance') else 0.0
                }
                for r in results
            ]
        else:
            # Fallback: return empty if no vector store
            spans = []
        
        # Rerank if enabled
        if self.use_reranking and self.reranker and spans:
            reranked = self.reranker.rerank(
                query=query,
                spans=spans,
                top_k=rerank_top_k
            )
            return reranked
        
        # Return top-k if no reranking
        return spans[:rerank_top_k]
    
    def retrieve_for_event(
        self,
        query: str,
        event_type: str,
        transcript: Optional[Dict[str, Any]] = None,
        top_k: int = 20,
        rerank_top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve spans specifically for an event type.
        
        Args:
            query: Search query text
            event_type: Type of event (e.g., "escalation", "refund")
            transcript: Optional transcript dictionary for event-specific extraction
            top_k: Number of initial results
            rerank_top_k: Number of results after reranking
        
        Returns:
            List of retrieved spans relevant to the event type
        """
        # Filter by event type if vector store supports it
        filter_dict = None
        if self.vector_store:
            filter_dict = {'event_types': {'$contains': event_type}}
        
        # Retrieve spans
        spans = self.retrieve(
            query=query,
            top_k=top_k,
            rerank_top_k=rerank_top_k,
            filter_dict=filter_dict
        )
        
        # If transcript provided, also extract event-specific spans
        if transcript:
            event_spans = self.span_extractor.extract_event_specific_spans(
                transcript=transcript,
                event_type=event_type,
                window_before=10
            )
            
            # Combine and deduplicate
            all_spans = spans + event_spans
            seen_texts = set()
            unique_spans = []
            for span in all_spans:
                text = span.get('text', '')
                if text not in seen_texts:
                    seen_texts.add(text)
                    unique_spans.append(span)
            
            # Rerank combined results
            if self.use_reranking and self.reranker:
                return self.reranker.rerank(query, unique_spans, top_k=rerank_top_k)
            
            return unique_spans[:rerank_top_k]
        
        return spans
    
    def retrieve_with_context(
        self,
        query: str,
        context: Optional[List[Dict[str, Any]]] = None,
        top_k: int = 20,
        rerank_top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve spans with context from previous conversation.
        
        Args:
            query: Current query text
            context: List of previous queries/responses for context
            top_k: Number of initial results
            rerank_top_k: Number of results after reranking
        
        Returns:
            List of retrieved spans with context awareness
        """
        # Enhance query with context if available
        enhanced_query = query
        if context:
            # Extract relevant information from context
            context_texts = [
                item.get('query', '') or item.get('response', '')
                for item in context
            ]
            context_summary = ' '.join(context_texts[-3:])  # Last 3 context items
            enhanced_query = f"{context_summary} {query}"
        
        # Retrieve with enhanced query
        return self.retrieve(
            query=enhanced_query,
            top_k=top_k,
            rerank_top_k=rerank_top_k
        )

