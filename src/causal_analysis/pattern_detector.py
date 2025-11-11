"""
Causal pattern detection in dialogue
"""

from typing import List, Dict, Any, Optional
import re
from collections import Counter


class CausalPatternDetector:
    """Detect causal patterns in dialogue spans"""
    
    def __init__(self):
        # Common causal indicators in conversation
        self.causal_indicators = {
            'temporal': ['before', 'after', 'then', 'next', 'previously', 'earlier', 'later'],
            'causal': ['because', 'due to', 'as a result', 'led to', 'caused', 'resulted in'],
            'conditional': ['if', 'when', 'unless', 'provided that'],
            'consequence': ['therefore', 'thus', 'hence', 'consequently', 'so']
        }
        
        # Behavioral patterns
        self.behavioral_patterns = {
            'hesitation': ['um', 'uh', 'well', 'let me think', 'hmm'],
            'frustration': ['frustrated', 'annoyed', 'upset', 'disappointed'],
            'repetition': ['again', 'repeat', 'same', 'once more'],
            'escalation_signals': ['supervisor', 'manager', 'escalate', 'complaint', 'formal'],
            'refund_signals': ['refund', 'money back', 'return', 'cancel', 'chargeback'],
            'churn_signals': ['cancel', 'close account', 'switch', 'leave', 'terminate']
        }
    
    def detect_patterns(
        self,
        span: Dict[str, Any],
        event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect causal patterns in a dialogue span.
        
        Args:
            span: Dialogue span dictionary with 'text' field
            event_type: Optional event type to focus detection on
        
        Returns:
            Dictionary of detected patterns and scores
        """
        text = span.get('text', '').lower()
        
        patterns = {
            'temporal_indicators': self._count_indicators(text, self.causal_indicators['temporal']),
            'causal_indicators': self._count_indicators(text, self.causal_indicators['causal']),
            'conditional_indicators': self._count_indicators(text, self.causal_indicators['conditional']),
            'consequence_indicators': self._count_indicators(text, self.causal_indicators['consequence']),
            'behavioral_patterns': self._detect_behavioral_patterns(text, event_type),
            'pattern_score': 0.0
        }
        
        # Calculate overall pattern score
        patterns['pattern_score'] = self._calculate_pattern_score(patterns)
        
        return patterns
    
    def _count_indicators(self, text: str, indicators: List[str]) -> int:
        """Count occurrences of causal indicators"""
        count = 0
        for indicator in indicators:
            count += len(re.findall(r'\b' + re.escape(indicator) + r'\b', text))
        return count
    
    def _detect_behavioral_patterns(
        self,
        text: str,
        event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Detect behavioral patterns in text"""
        detected = {}
        
        for pattern_name, keywords in self.behavioral_patterns.items():
            count = self._count_indicators(text, keywords)
            detected[pattern_name] = count > 0
            detected[f'{pattern_name}_count'] = count
        
        # Event-specific pattern detection
        if event_type:
            event_patterns = self._get_event_specific_patterns(event_type)
            for pattern_name, keywords in event_patterns.items():
                count = self._count_indicators(text, keywords)
                detected[f'event_{pattern_name}'] = count > 0
                detected[f'event_{pattern_name}_count'] = count
        
        return detected
    
    def _get_event_specific_patterns(self, event_type: str) -> Dict[str, List[str]]:
        """Get event-specific patterns"""
        event_type_lower = event_type.lower()
        
        if 'escalation' in event_type_lower:
            return {
                'escalation_triggers': [
                    'not satisfied', 'unhappy', 'want to speak', 'need manager',
                    'file complaint', 'not helping', 'waste of time'
                ]
            }
        elif 'refund' in event_type_lower:
            return {
                'refund_triggers': [
                    'not working', 'defective', 'broken', 'not as described',
                    'want money back', 'dissatisfied', 'poor quality'
                ]
            }
        elif 'churn' in event_type_lower:
            return {
                'churn_triggers': [
                    'too expensive', 'better option', 'switching', 'leaving',
                    'not worth it', 'found alternative', 'better deal'
                ]
            }
        
        return {}
    
    def _calculate_pattern_score(self, patterns: Dict[str, Any]) -> float:
        """Calculate overall pattern score"""
        score = 0.0
        
        # Weight different indicators
        weights = {
            'temporal_indicators': 0.2,
            'causal_indicators': 0.4,
            'conditional_indicators': 0.2,
            'consequence_indicators': 0.2
        }
        
        for indicator, weight in weights.items():
            count = patterns.get(indicator, 0)
            # Normalize count (max 5 occurrences)
            normalized = min(count / 5.0, 1.0)
            score += weight * normalized
        
        # Add behavioral pattern bonus
        behavioral = patterns.get('behavioral_patterns', {})
        if any(behavioral.get(k, False) for k in behavioral.keys() if isinstance(behavioral.get(k), bool)):
            score += 0.2
        
        # Normalize to [0, 1]
        return min(score, 1.0)
    
    def detect_temporal_patterns(
        self,
        spans: List[Dict[str, Any]],
        event_turn_index: int
    ) -> List[Dict[str, Any]]:
        """
        Detect temporal patterns in spans relative to an event.
        
        Args:
            spans: List of dialogue spans
            event_turn_index: Turn index of the event
        
        Returns:
            Spans with temporal pattern annotations
        """
        annotated_spans = []
        
        for span in spans:
            span_start = span.get('start_turn_index', 0)
            span_end = span.get('end_turn_index', 0)
            
            # Calculate temporal relationship
            if span_end < event_turn_index:
                temporal_relation = 'precedes'
                distance = event_turn_index - span_end
            elif span_start > event_turn_index:
                temporal_relation = 'follows'
                distance = span_start - event_turn_index
            else:
                temporal_relation = 'overlaps'
                distance = 0
            
            # Temporal pattern score (closer = higher score)
            if distance == 0:
                temporal_score = 1.0
            else:
                temporal_score = 1.0 / (1.0 + distance / 10.0)  # Decay with distance
            
            span_copy = span.copy()
            span_copy['temporal_relation'] = temporal_relation
            span_copy['temporal_distance'] = distance
            span_copy['temporal_score'] = temporal_score
            
            annotated_spans.append(span_copy)
        
        return annotated_spans
    
    def detect_sequential_patterns(
        self,
        spans: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect sequential patterns across spans.
        
        Args:
            spans: List of dialogue spans
        
        Returns:
            Spans with sequential pattern annotations
        """
        if len(spans) < 2:
            return spans
        
        # Sort spans by turn index
        sorted_spans = sorted(
            spans,
            key=lambda x: x.get('start_turn_index', 0)
        )
        
        annotated_spans = []
        
        for i, span in enumerate(sorted_spans):
            # Check for sequential relationships
            sequential_indicators = 0
            
            if i > 0:
                prev_span = sorted_spans[i - 1]
                # Check for continuation patterns
                if self._is_sequential(prev_span, span):
                    sequential_indicators += 1
            
            if i < len(sorted_spans) - 1:
                next_span = sorted_spans[i + 1]
                # Check for continuation patterns
                if self._is_sequential(span, next_span):
                    sequential_indicators += 1
            
            span_copy = span.copy()
            span_copy['sequential_indicators'] = sequential_indicators
            span_copy['sequential_score'] = min(sequential_indicators / 2.0, 1.0)
            
            annotated_spans.append(span_copy)
        
        return annotated_spans
    
    def _is_sequential(self, span1: Dict[str, Any], span2: Dict[str, Any]) -> bool:
        """Check if two spans are sequentially related"""
        # Check if spans are adjacent or close
        end1 = span1.get('end_turn_index', 0)
        start2 = span2.get('start_turn_index', 0)
        
        # Adjacent or within 2 turns
        return abs(start2 - end1) <= 2

