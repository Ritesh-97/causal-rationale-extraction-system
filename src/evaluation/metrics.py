"""
Evaluation metrics for system performance
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
import re


class EvaluationMetrics:
    """Evaluation metrics for causal explanation quality"""
    
    def __init__(self):
        pass
    
    def evaluate_response_quality(
        self,
        response: str,
        reference: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Evaluate response quality metrics.
        
        Args:
            response: System response text
            reference: Optional reference response
        
        Returns:
            Dictionary with quality metrics
        """
        metrics = {
            'length': len(response),
            'word_count': len(response.split()),
            'sentence_count': len(re.split(r'[.!?]+', response)),
            'has_citations': self._has_citations(response),
            'citation_count': self._count_citations(response),
            'coherence_score': self._calculate_coherence(response)
        }
        
        # Compare with reference if provided
        if reference:
            metrics['similarity'] = self._calculate_similarity(response, reference)
        
        return metrics
    
    def evaluate_evidence_quality(
        self,
        evidence: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, float]:
        """
        Evaluate evidence quality metrics.
        
        Args:
            evidence: List of evidence spans
            query: Original query
        
        Returns:
            Dictionary with evidence quality metrics
        """
        if not evidence:
            return {
                'evidence_count': 0,
                'avg_evidence_score': 0.0,
                'evidence_coverage': 0.0
            }
        
        evidence_scores = [span.get('evidence_score', 0.0) for span in evidence]
        
        metrics = {
            'evidence_count': len(evidence),
            'avg_evidence_score': np.mean(evidence_scores) if evidence_scores else 0.0,
            'max_evidence_score': np.max(evidence_scores) if evidence_scores else 0.0,
            'min_evidence_score': np.min(evidence_scores) if evidence_scores else 0.0,
            'evidence_coverage': self._calculate_evidence_coverage(evidence),
            'evidence_diversity': self._calculate_evidence_diversity(evidence)
        }
        
        return metrics
    
    def evaluate_causal_explanation_quality(
        self,
        explanation: str,
        evidence: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, float]:
        """
        Evaluate causal explanation quality.
        
        Args:
            explanation: Explanation text
            evidence: List of evidence spans
            query: Original query
        
        Returns:
            Dictionary with explanation quality metrics
        """
        metrics = {
            'explanation_length': len(explanation),
            'has_causal_language': self._has_causal_language(explanation),
            'causal_indicator_count': self._count_causal_indicators(explanation),
            'evidence_reference_count': self._count_evidence_references(explanation, evidence),
            'explanation_completeness': self._calculate_completeness(explanation, query)
        }
        
        # Combine with evidence quality
        evidence_metrics = self.evaluate_evidence_quality(evidence, query)
        metrics.update(evidence_metrics)
        
        return metrics
    
    def evaluate_conversational_coherence(
        self,
        current_query: str,
        current_response: str,
        previous_turns: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Evaluate conversational coherence for follow-up queries.
        
        Args:
            current_query: Current query text
            current_response: Current response text
            previous_turns: List of previous conversation turns
        
        Returns:
            Dictionary with coherence metrics
        """
        if not previous_turns:
            return {
                'coherence_score': 0.0,
                'context_usage': 0.0,
                'reference_count': 0
            }
        
        # Check for references to previous context
        references = self._count_context_references(current_response, previous_turns)
        
        # Calculate coherence
        coherence_score = self._calculate_coherence_score(
            current_query,
            current_response,
            previous_turns
        )
        
        metrics = {
            'coherence_score': coherence_score,
            'context_usage': references / len(previous_turns) if previous_turns else 0.0,
            'reference_count': references,
            'context_relevance': self._calculate_context_relevance(
                current_response,
                previous_turns
            )
        }
        
        return metrics
    
    def _has_citations(self, text: str) -> bool:
        """Check if text contains citations"""
        pattern = r'\[Evidence\s+\d+\]|\[Citation\s+\d+\]|\(Evidence\s+\d+\)'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _count_citations(self, text: str) -> int:
        """Count citations in text"""
        pattern = r'\[Evidence\s+\d+\]|\[Citation\s+\d+\]|\(Evidence\s+\d+\)'
        return len(re.findall(pattern, text, re.IGNORECASE))
    
    def _calculate_coherence(self, text: str) -> float:
        """Calculate text coherence score"""
        # Simple coherence: check for transition words and logical flow
        transition_words = [
            'because', 'therefore', 'thus', 'hence', 'consequently',
            'furthermore', 'moreover', 'additionally', 'however', 'although'
        ]
        
        words = text.lower().split()
        transition_count = sum(1 for word in words if word in transition_words)
        
        # Normalize by text length
        coherence = min(transition_count / max(len(words), 1) * 10, 1.0)
        
        return coherence
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_evidence_coverage(self, evidence: List[Dict[str, Any]]) -> float:
        """Calculate evidence coverage across transcripts"""
        if not evidence:
            return 0.0
        
        transcript_ids = set()
        for span in evidence:
            transcript_id = span.get('transcript_id') or span.get('metadata', {}).get('transcript_id')
            if transcript_id:
                transcript_ids.add(transcript_id)
        
        # Coverage is number of unique transcripts
        return len(transcript_ids) / len(evidence) if evidence else 0.0
    
    def _calculate_evidence_diversity(self, evidence: List[Dict[str, Any]]) -> float:
        """Calculate evidence diversity"""
        if not evidence or len(evidence) < 2:
            return 0.0
        
        # Calculate diversity based on text similarity
        texts = [span.get('text', '') for span in evidence]
        similarities = []
        
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                sim = self._calculate_similarity(texts[i], texts[j])
                similarities.append(sim)
        
        # Diversity is inverse of average similarity
        avg_similarity = np.mean(similarities) if similarities else 0.0
        diversity = 1.0 - avg_similarity
        
        return diversity
    
    def _has_causal_language(self, text: str) -> bool:
        """Check if text contains causal language"""
        causal_indicators = [
            'because', 'due to', 'as a result', 'led to', 'caused',
            'resulted in', 'therefore', 'thus', 'hence', 'consequently'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in causal_indicators)
    
    def _count_causal_indicators(self, text: str) -> int:
        """Count causal indicators in text"""
        causal_indicators = [
            'because', 'due to', 'as a result', 'led to', 'caused',
            'resulted in', 'therefore', 'thus', 'hence', 'consequently'
        ]
        
        text_lower = text.lower()
        count = sum(1 for indicator in causal_indicators if indicator in text_lower)
        
        return count
    
    def _count_evidence_references(
        self,
        explanation: str,
        evidence: List[Dict[str, Any]]
    ) -> int:
        """Count references to evidence in explanation"""
        # Count citation patterns
        citation_count = self._count_citations(explanation)
        
        # Count references to evidence content
        evidence_texts = [span.get('text', '')[:50] for span in evidence[:5]]  # First 50 chars
        reference_count = 0
        
        for evidence_text in evidence_texts:
            if evidence_text.lower() in explanation.lower():
                reference_count += 1
        
        return citation_count + reference_count
    
    def _calculate_completeness(self, explanation: str, query: str) -> float:
        """Calculate explanation completeness"""
        # Check if explanation addresses query keywords
        query_words = set(query.lower().split())
        explanation_words = set(explanation.lower().split())
        
        if not query_words:
            return 0.0
        
        # Calculate coverage of query keywords
        coverage = len(query_words.intersection(explanation_words)) / len(query_words)
        
        return coverage
    
    def _count_context_references(
        self,
        response: str,
        previous_turns: List[Dict[str, Any]]
    ) -> int:
        """Count references to previous context"""
        references = 0
        
        for turn in previous_turns:
            # Check for references to previous query
            query_words = set(turn.get('query', '').lower().split())
            response_words = set(response.lower().split())
            
            if query_words.intersection(response_words):
                references += 1
        
        return references
    
    def _calculate_coherence_score(
        self,
        current_query: str,
        current_response: str,
        previous_turns: List[Dict[str, Any]]
    ) -> float:
        """Calculate coherence score for follow-up"""
        if not previous_turns:
            return 0.0
        
        # Check for pronoun usage (indicates context awareness)
        pronouns = ['it', 'that', 'this', 'these', 'those', 'they', 'them']
        query_words = current_query.lower().split()
        pronoun_count = sum(1 for word in query_words if word in pronouns)
        
        # Check for context references
        context_references = self._count_context_references(current_response, previous_turns)
        
        # Calculate coherence
        coherence = min(
            (pronoun_count * 0.3 + context_references * 0.7) / len(previous_turns),
            1.0
        )
        
        return coherence
    
    def _calculate_context_relevance(
        self,
        response: str,
        previous_turns: List[Dict[str, Any]]
    ) -> float:
        """Calculate relevance to previous context"""
        if not previous_turns:
            return 0.0
        
        # Calculate similarity to previous responses
        similarities = []
        for turn in previous_turns:
            prev_response = turn.get('response', '')
            if prev_response:
                sim = self._calculate_similarity(response, prev_response)
                similarities.append(sim)
        
        # Relevance is average similarity
        relevance = np.mean(similarities) if similarities else 0.0
        
        return relevance

