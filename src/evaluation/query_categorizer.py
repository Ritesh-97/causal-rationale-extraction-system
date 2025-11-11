"""
Query categorization utilities
"""

from typing import List, Dict, Any, Optional
import re


class QueryCategorizer:
    """Categorize queries by task, difficulty, and use case"""
    
    def __init__(self):
        # Task categories
        self.task_categories = {
            'task1': ['initial', 'causal_inquiry', 'first_query'],
            'task2': ['followup', 'contextual', 'follow_up', 'conversational']
        }
        
        # Difficulty categories
        self.difficulty_patterns = {
            'simple': [
                r'what.*happen',
                r'why.*happen',
                r'when.*happen',
                r'how.*many'
            ],
            'complex': [
                r'what.*pattern',
                r'identify.*factor',
                r'analyze.*relationship',
                r'compare.*and.*contrast',
                r'what.*correlation'
            ],
            'multi_hop': [
                r'if.*then',
                r'what.*if',
                r'how.*would',
                r'what.*would.*happen.*if'
            ]
        }
        
        # Use case categories
        self.use_case_patterns = {
            'agent_behavior': [
                r'agent',
                r'representative',
                r'staff',
                r'employee',
                r'performance'
            ],
            'product_feedback': [
                r'product',
                r'service',
                r'quality',
                r'feedback',
                r'satisfaction',
                r'experience'
            ],
            'customer_behavior': [
                r'customer',
                r'client',
                r'user',
                r'behavior',
                r'action'
            ],
            'process_analysis': [
                r'process',
                r'workflow',
                r'procedure',
                r'system',
                r'method'
            ]
        }
    
    def categorize_query(
        self,
        query: str,
        is_followup: bool = False
    ) -> Dict[str, Any]:
        """
        Categorize a query by task, difficulty, and use case.
        
        Args:
            query: Query text
            is_followup: Whether this is a follow-up query
        
        Returns:
            Dictionary with categorization
        """
        query_lower = query.lower()
        
        # Task category
        task_category = 'task2' if is_followup else 'task1'
        
        # Difficulty category
        difficulty = self._determine_difficulty(query_lower)
        
        # Use case category
        use_case = self._determine_use_case(query_lower)
        
        # Event type
        event_type = self._extract_event_type(query_lower)
        
        return {
            'task': task_category,
            'difficulty': difficulty,
            'use_case': use_case,
            'event_type': event_type,
            'is_followup': is_followup
        }
    
    def _determine_difficulty(self, query_lower: str) -> str:
        """Determine query difficulty"""
        # Check for complex patterns first
        for difficulty, patterns in self.difficulty_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return difficulty
        
        # Default to simple
        return 'simple'
    
    def _determine_use_case(self, query_lower: str) -> str:
        """Determine use case category"""
        for use_case, patterns in self.use_case_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return use_case
        
        # Default
        return 'general'
    
    def _extract_event_type(self, query_lower: str) -> Optional[str]:
        """Extract event type from query"""
        event_types = ['escalation', 'refund', 'churn', 'complaint', 'satisfaction']
        
        for event_type in event_types:
            if event_type in query_lower:
                return event_type
        
        return None
    
    def categorize_batch(
        self,
        queries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Categorize a batch of queries.
        
        Args:
            queries: List of query dictionaries with 'query' field
        
        Returns:
            List of queries with categorization added
        """
        categorized = []
        
        for query_dict in queries:
            query = query_dict.get('query', '')
            is_followup = query_dict.get('is_followup', False)
            
            categorization = self.categorize_query(query, is_followup)
            
            # Merge with original query dict
            categorized_query = query_dict.copy()
            categorized_query.update(categorization)
            
            categorized.append(categorized_query)
        
        return categorized

