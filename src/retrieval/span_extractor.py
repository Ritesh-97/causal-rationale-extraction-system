"""
Dialogue span extraction utilities
"""

from typing import List, Dict, Any, Optional
import re


class SpanExtractor:
    """Extract and rank dialogue spans for causal analysis"""
    
    def __init__(self):
        pass
    
    def extract_causal_spans(
        self,
        transcript: Dict[str, Any],
        event: Dict[str, Any],
        window_before: int = 10,
        window_after: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Extract dialogue spans that precede and correlate with an event.
        
        Args:
            transcript: Transcript dictionary with turns
            event: Event dictionary with turn_id or turn_index
            window_before: Number of turns to include before event
            window_after: Number of turns to include after event
        
        Returns:
            List of dialogue spans relevant to the event
        """
        turns = transcript.get('turns', [])
        if not turns:
            return []
        
        # Find event turn index
        event_turn_index = None
        if 'turn_index' in event:
            event_turn_index = event['turn_index']
        elif 'turn_id' in event:
            # Find turn by turn_id
            for i, turn in enumerate(turns):
                if turn.get('turn_id') == event['turn_id']:
                    event_turn_index = i
                    break
        
        if event_turn_index is None:
            return []
        
        # Extract spans around event
        start_index = max(0, event_turn_index - window_before)
        end_index = min(len(turns), event_turn_index + window_after + 1)
        
        causal_turns = turns[start_index:end_index]
        
        # Create spans from causal turns
        spans = self._create_spans_from_turns(
            causal_turns,
            transcript_id=transcript.get('transcript_id', 'unknown'),
            start_index=start_index
        )
        
        return spans
    
    def _create_spans_from_turns(
        self,
        turns: List[Dict[str, Any]],
        transcript_id: str,
        start_index: int = 0,
        window_size: int = 5
    ) -> List[Dict[str, Any]]:
        """Create dialogue spans from turns"""
        spans = []
        
        for i in range(len(turns) - window_size + 1):
            span_turns = turns[i:i + window_size]
            
            # Combine text
            span_text = ' '.join([turn.get('text', '') for turn in span_turns])
            
            # Extract metadata
            speakers = [turn.get('speaker', 'unknown') for turn in span_turns]
            turn_ids = [turn.get('turn_id', start_index + i + j) for j, turn in enumerate(span_turns)]
            
            span = {
                'span_id': f"{transcript_id}_causal_span_{i}",
                'text': span_text,
                'start_turn_index': start_index + i,
                'end_turn_index': start_index + i + window_size - 1,
                'turn_ids': turn_ids,
                'speakers': speakers,
                'transcript_id': transcript_id,
                'metadata': {
                    'window_size': window_size,
                    'speaker_distribution': {s: speakers.count(s) for s in set(speakers)}
                }
            }
            
            spans.append(span)
        
        return spans
    
    def extract_event_specific_spans(
        self,
        transcript: Dict[str, Any],
        event_type: str,
        window_before: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract spans for all events of a specific type.
        
        Args:
            transcript: Transcript dictionary
            event_type: Type of event to extract spans for
            window_before: Number of turns to include before each event
        
        Returns:
            List of dialogue spans for all events of the specified type
        """
        events = transcript.get('events', [])
        relevant_events = [
            e for e in events
            if e.get('event_type', '').lower() == event_type.lower()
        ]
        
        all_spans = []
        for event in relevant_events:
            spans = self.extract_causal_spans(
                transcript,
                event,
                window_before=window_before,
                window_after=0
            )
            all_spans.extend(spans)
        
        return all_spans
    
    def rank_spans_by_temporal_proximity(
        self,
        spans: List[Dict[str, Any]],
        event_turn_index: int
    ) -> List[Dict[str, Any]]:
        """
        Rank spans by temporal proximity to an event.
        
        Args:
            spans: List of dialogue spans
            event_turn_index: Turn index of the event
        
        Returns:
            Spans sorted by temporal proximity (closest first)
        """
        ranked = []
        
        for span in spans:
            span_start = span.get('start_turn_index', 0)
            span_end = span.get('end_turn_index', 0)
            
            # Calculate distance to event
            if span_end < event_turn_index:
                distance = event_turn_index - span_end
            elif span_start > event_turn_index:
                distance = span_start - event_turn_index
            else:
                distance = 0  # Span overlaps with event
            
            span_copy = span.copy()
            span_copy['temporal_distance'] = distance
            ranked.append(span_copy)
        
        # Sort by temporal distance (ascending)
        ranked.sort(key=lambda x: x.get('temporal_distance', float('inf')))
        
        return ranked

