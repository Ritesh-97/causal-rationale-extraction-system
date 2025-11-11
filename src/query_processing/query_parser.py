"""
Query parsing and understanding utilities
"""

from typing import Dict, Any, Optional, List
import re


class QueryParser:
    """Parse and understand natural language queries"""
    
    def __init__(self):
        # Common event types
        self.event_types = ['escalation', 'refund', 'churn', 'complaint', 'satisfaction']
        
        # Query intent patterns
        self.intent_patterns = {
            'causal_inquiry': [
                r'why.*happen',
                r'what.*cause',
                r'what.*lead.*to',
                r'what.*trigger',
                r'how.*occur',
                r'what.*reason'
            ],
            'pattern_analysis': [
                r'what.*pattern',
                r'what.*common',
                r'what.*typical',
                r'what.*frequent',
                r'identify.*pattern'
            ],
            'specific_event': [
                r'about.*call',
                r'for.*call',
                r'in.*call',
                r'regarding.*call'
            ]
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query.
        
        Args:
            query: Natural language query text
        
        Returns:
            Dictionary with parsed query information
        """
        query_lower = query.lower()
        
        # Extract event type
        event_type = self._extract_event_type(query_lower)
        
        # Determine intent
        intent = self._determine_intent(query_lower)
        
        # Extract key terms
        key_terms = self._extract_key_terms(query)
        
        return {
            'original_query': query,
            'query_lower': query_lower,
            'event_type': event_type,
            'intent': intent,
            'key_terms': key_terms,
            'is_causal': intent == 'causal_inquiry',
            'is_pattern': intent == 'pattern_analysis',
            'is_specific': intent == 'specific_event'
        }
    
    def _extract_event_type(self, query_lower: str) -> Optional[str]:
        """Extract event type from query"""
        for event_type in self.event_types:
            if event_type in query_lower:
                return event_type
        
        # Check for variations
        if 'escalat' in query_lower:
            return 'escalation'
        elif 'refund' in query_lower:
            return 'refund'
        elif 'churn' in query_lower or 'cancel' in query_lower:
            return 'churn'
        elif 'complain' in query_lower:
            return 'complaint'
        
        return None
    
    def _determine_intent(self, query_lower: str) -> str:
        """Determine query intent"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        # Default to causal inquiry
        return 'causal_inquiry'
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query"""
        # Simple extraction: remove stop words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'what',
            'why', 'how', 'when', 'where', 'who', 'which', 'that', 'this', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Tokenize and filter
        words = re.findall(r'\b\w+\b', query.lower())
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        return key_terms
    
    def decompose_query(self, query: str) -> List[str]:
        """
        Decompose a complex query into sub-queries.
        
        Args:
            query: Complex query text
        
        Returns:
            List of sub-queries
        """
        # Simple decomposition: split by conjunctions
        conjunctions = ['and', 'or', 'but', 'also', 'additionally']
        
        sub_queries = [query]
        for conj in conjunctions:
            new_sub_queries = []
            for sq in sub_queries:
                if conj in sq.lower():
                    parts = re.split(rf'\b{conj}\b', sq, flags=re.IGNORECASE)
                    new_sub_queries.extend([p.strip() for p in parts if p.strip()])
                else:
                    new_sub_queries.append(sq)
            sub_queries = new_sub_queries
        
        return sub_queries

