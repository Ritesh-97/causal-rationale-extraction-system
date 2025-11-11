"""
Baseline implementations for comparison
"""

from typing import List, Dict, Any, Optional
import re
from collections import Counter


class KeywordSearchBaseline:
    """Simple keyword search baseline"""
    
    def __init__(self):
        pass
    
    def search(
        self,
        query: str,
        spans: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search using keyword matching"""
        query_words = set(query.lower().split())
        
        scored_spans = []
        for span in spans:
            text = span.get('text', '').lower()
            text_words = set(text.split())
            
            # Calculate keyword overlap
            overlap = len(query_words.intersection(text_words))
            score = overlap / len(query_words) if query_words else 0.0
            
            span_copy = span.copy()
            span_copy['score'] = score
            scored_spans.append(span_copy)
        
        # Sort by score
        scored_spans.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        
        return scored_spans[:top_k]
    
    def generate_response(
        self,
        query: str,
        spans: List[Dict[str, Any]]
    ) -> str:
        """Generate simple response from keyword matches"""
        top_spans = self.search(query, spans, top_k=5)
        
        if not top_spans:
            return "No relevant information found."
        
        # Combine top spans
        response_parts = []
        for i, span in enumerate(top_spans, 1):
            text = span.get('text', '')
            response_parts.append(f"[Evidence {i}] {text[:200]}...")
        
        response = "Based on the following evidence:\n\n" + "\n\n".join(response_parts)
        
        return response


class SimpleRAGBaseline:
    """Simple RAG baseline without reranking"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        self.embedding_model = SentenceTransformer(embedding_model)
        self.cosine_similarity = cosine_similarity
        self.np = np
    
    def search(
        self,
        query: str,
        spans: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search using semantic similarity"""
        if not spans:
            return []
        
        # Get embeddings
        query_embedding = self.embedding_model.encode(
            query,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        span_texts = [span.get('text', '') for span in spans]
        span_embeddings = self.embedding_model.encode(
            span_texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        # Calculate similarities
        similarities = self.cosine_similarity(
            query_embedding.reshape(1, -1),
            span_embeddings
        )[0]
        
        # Add scores to spans
        scored_spans = []
        for i, span in enumerate(spans):
            span_copy = span.copy()
            span_copy['score'] = float(similarities[i])
            scored_spans.append(span_copy)
        
        # Sort by score
        scored_spans.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        
        return scored_spans[:top_k]
    
    def generate_response(
        self,
        query: str,
        spans: List[Dict[str, Any]]
    ) -> str:
        """Generate response from semantic search results"""
        top_spans = self.search(query, spans, top_k=5)
        
        if not top_spans:
            return "No relevant information found."
        
        # Combine top spans
        response_parts = []
        for i, span in enumerate(top_spans, 1):
            text = span.get('text', '')
            score = span.get('score', 0.0)
            response_parts.append(f"[Evidence {i}] (Score: {score:.2f}) {text[:200]}...")
        
        response = "Based on semantic search:\n\n" + "\n\n".join(response_parts)
        
        return response


class RuleBasedBaseline:
    """Rule-based baseline using pattern matching"""
    
    def __init__(self):
        # Event-specific patterns
        self.event_patterns = {
            'escalation': [
                r'supervisor', r'manager', r'escalate', r'complaint',
                r'formal', r'higher.*level'
            ],
            'refund': [
                r'refund', r'money.*back', r'return', r'cancel',
                r'chargeback', r'reimburse'
            ],
            'churn': [
                r'cancel', r'close.*account', r'switch', r'leave',
                r'terminate', r'close.*service'
            ]
        }
    
    def search(
        self,
        query: str,
        spans: List[Dict[str, Any]],
        event_type: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search using rule-based patterns"""
        query_lower = query.lower()
        
        # Determine event type if not provided
        if not event_type:
            for event, patterns in self.event_patterns.items():
                if any(re.search(pattern, query_lower) for pattern in patterns):
                    event_type = event
                    break
        
        # Score spans based on patterns
        scored_spans = []
        for span in spans:
            text = span.get('text', '').lower()
            score = 0.0
            
            # Match event-specific patterns
            if event_type and event_type in self.event_patterns:
                patterns = self.event_patterns[event_type]
                matches = sum(1 for pattern in patterns if re.search(pattern, text))
                score += matches / len(patterns) if patterns else 0.0
            
            # Match query keywords
            query_words = set(query_lower.split())
            text_words = set(text.split())
            keyword_overlap = len(query_words.intersection(text_words))
            score += keyword_overlap / len(query_words) if query_words else 0.0
            
            span_copy = span.copy()
            span_copy['score'] = score
            scored_spans.append(span_copy)
        
        # Sort by score
        scored_spans.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        
        return scored_spans[:top_k]
    
    def generate_response(
        self,
        query: str,
        spans: List[Dict[str, Any]]
    ) -> str:
        """Generate rule-based response"""
        # Extract event type from query
        event_type = None
        query_lower = query.lower()
        for event, patterns in self.event_patterns.items():
            if any(re.search(pattern, query_lower) for pattern in patterns):
                event_type = event
                break
        
        top_spans = self.search(query, spans, event_type=event_type, top_k=5)
        
        if not top_spans:
            return "No relevant information found based on rule-based matching."
        
        # Generate response
        response = f"Based on rule-based analysis for {event_type or 'events'}:\n\n"
        
        for i, span in enumerate(top_spans, 1):
            text = span.get('text', '')
            score = span.get('score', 0.0)
            response += f"[Evidence {i}] (Score: {score:.2f}) {text[:200]}...\n\n"
        
        return response

