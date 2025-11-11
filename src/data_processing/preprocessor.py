"""
Transcript preprocessing utilities
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Turn:
    """Represents a single turn in a conversation"""
    turn_id: int
    speaker: str
    text: str
    timestamp: Optional[float] = None
    turn_index: Optional[int] = None


@dataclass
class Event:
    """Represents a business event in a conversation"""
    event_type: str  # e.g., "escalation", "refund", "churn"
    event_label: Optional[str] = None
    turn_id: Optional[int] = None
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class TranscriptPreprocessor:
    """Preprocess transcripts for analysis"""
    
    def __init__(self):
        self.speaker_normalization = {
            'agent': ['agent', 'representative', 'rep', 'support'],
            'customer': ['customer', 'client', 'caller', 'user']
        }
    
    def preprocess(self, transcript: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess a transcript:
        - Normalize speaker labels
        - Clean text
        - Segment turns
        - Extract dialogue structure
        """
        turns = self._normalize_turns(transcript['turns'])
        turns = self._clean_turns(turns)
        turns = self._add_turn_indices(turns)
        
        events = self._normalize_events(transcript.get('events', []))
        
        return {
            'transcript_id': transcript['transcript_id'],
            'turns': turns,
            'events': events,
            'metadata': transcript.get('metadata', {}),
            'dialogue_structure': self._extract_dialogue_structure(turns)
        }
    
    def _normalize_turns(self, turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize speaker labels"""
        normalized = []
        
        for turn in turns:
            speaker = turn.get('speaker', '').lower()
            
            # Normalize speaker label
            normalized_speaker = speaker
            for standard, variants in self.speaker_normalization.items():
                if any(variant in speaker for variant in variants):
                    normalized_speaker = standard
                    break
            
            turn_copy = turn.copy()
            turn_copy['speaker'] = normalized_speaker
            normalized.append(turn_copy)
        
        return normalized
    
    def _clean_turns(self, turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean text in turns"""
        cleaned = []
        
        for turn in turns:
            text = turn.get('text', '')
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove special characters that might interfere (keep basic punctuation)
            # text = re.sub(r'[^\w\s.,!?;:\-\'"]', '', text)
            
            # Trim
            text = text.strip()
            
            turn_copy = turn.copy()
            turn_copy['text'] = text
            cleaned.append(turn_copy)
        
        return cleaned
    
    def _add_turn_indices(self, turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add sequential turn indices"""
        indexed = []
        
        for i, turn in enumerate(turns):
            turn_copy = turn.copy()
            turn_copy['turn_index'] = i
            indexed.append(turn_copy)
        
        return indexed
    
    def _normalize_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize event labels"""
        normalized = []
        
        for event in events:
            event_type = event.get('event_type', '').lower()
            
            # Normalize common event types
            event_type_mapping = {
                'escalation': 'escalation',
                'escalate': 'escalation',
                'refund': 'refund',
                'refund_request': 'refund',
                'churn': 'churn',
                'churn_intent': 'churn',
                'cancellation': 'churn'
            }
            
            normalized_type = event_type_mapping.get(event_type, event_type)
            
            event_copy = event.copy()
            event_copy['event_type'] = normalized_type
            normalized.append(event_copy)
        
        return normalized
    
    def _extract_dialogue_structure(self, turns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract dialogue structure features"""
        if not turns:
            return {}
        
        # Count turns by speaker
        speaker_counts = {}
        for turn in turns:
            speaker = turn.get('speaker', 'unknown')
            speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1
        
        # Calculate average turn length
        turn_lengths = [len(turn.get('text', '')) for turn in turns]
        avg_turn_length = sum(turn_lengths) / len(turn_lengths) if turn_lengths else 0
        
        # Identify dialogue segments (conversation phases)
        segments = self._identify_segments(turns)
        
        return {
            'total_turns': len(turns),
            'speaker_distribution': speaker_counts,
            'average_turn_length': avg_turn_length,
            'segments': segments
        }
    
    def _identify_segments(self, turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify conversation segments/phases"""
        # Simple segmentation: group consecutive turns by speaker
        segments = []
        current_segment = None
        
        for i, turn in enumerate(turns):
            speaker = turn.get('speaker', 'unknown')
            
            if current_segment is None or current_segment['speaker'] != speaker:
                if current_segment is not None:
                    segments.append(current_segment)
                
                current_segment = {
                    'speaker': speaker,
                    'start_turn': i,
                    'end_turn': i,
                    'turns': [turn]
                }
            else:
                current_segment['end_turn'] = i
                current_segment['turns'].append(turn)
        
        if current_segment is not None:
            segments.append(current_segment)
        
        return segments
    
    def extract_dialogue_spans(
        self, 
        turns: List[Dict[str, Any]], 
        window_size: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Extract dialogue spans (sliding windows of turns) for retrieval.
        
        Args:
            turns: List of turn dictionaries
            window_size: Number of consecutive turns per span
        
        Returns:
            List of span dictionaries with text, metadata, and turn indices
        """
        spans = []
        
        for i in range(len(turns) - window_size + 1):
            span_turns = turns[i:i + window_size]
            
            # Combine text from span turns
            span_text = ' '.join([turn.get('text', '') for turn in span_turns])
            
            # Extract metadata
            speakers = [turn.get('speaker', 'unknown') for turn in span_turns]
            turn_ids = [turn.get('turn_id', i + j) for j, turn in enumerate(span_turns)]
            
            span = {
                'span_id': f"{turns[0].get('transcript_id', 'unknown')}_span_{i}",
                'text': span_text,
                'start_turn_index': i,
                'end_turn_index': i + window_size - 1,
                'turn_ids': turn_ids,
                'speakers': speakers,
                'transcript_id': turns[0].get('transcript_id', 'unknown'),
                'metadata': {
                    'window_size': window_size,
                    'speaker_distribution': {s: speakers.count(s) for s in set(speakers)}
                }
            }
            
            spans.append(span)
        
        return spans

