"""
Transcript loading and parsing utilities
"""

import json
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path


class TranscriptLoader:
    """Load and parse conversational transcripts"""
    
    def __init__(self):
        self.supported_formats = ['.json', '.csv', '.txt']
    
    def load_transcript(self, file_path: str) -> Dict[str, Any]:
        """
        Load transcript from file.
        
        Expected formats:
        - JSON: {"transcript_id": str, "turns": [...], "events": [...], "metadata": {...}}
        - CSV: columns: transcript_id, turn_id, speaker, text, timestamp, event_type, event_label
        - TXT: Simple text format (basic parsing)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {file_path}")
        
        if file_path.suffix == '.json':
            return self._load_json(file_path)
        elif file_path.suffix == '.csv':
            return self._load_csv(file_path)
        elif file_path.suffix == '.txt':
            return self._load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON format transcript"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle list of transcripts (batch file)
        if isinstance(data, list):
            if len(data) == 0:
                raise ValueError(f"Empty transcript list in {file_path}")
            # Return first transcript (for single file processing)
            # For batch processing, use load_batch instead
            data = data[0]
        
        # Normalize structure
        transcript = {
            'transcript_id': data.get('transcript_id', file_path.stem),
            'turns': data.get('turns', []),
            'events': data.get('events', []),
            'metadata': data.get('metadata', {})
        }
        
        return transcript
    
    def _load_csv(self, file_path: Path) -> Dict[str, Any]:
        """Load CSV format transcript"""
        df = pd.read_csv(file_path)
        
        # Expected columns: transcript_id, turn_id, speaker, text, timestamp, event_type, event_label
        required_cols = ['transcript_id', 'turn_id', 'speaker', 'text']
        
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV missing required columns: {required_cols}")
        
        # Group by transcript_id
        transcript_id = df['transcript_id'].iloc[0]
        
        turns = []
        events = []
        
        for _, row in df.iterrows():
            turn = {
                'turn_id': row['turn_id'],
                'speaker': row['speaker'],
                'text': row['text'],
                'timestamp': row.get('timestamp', None)
            }
            turns.append(turn)
            
            # Extract events if present
            if 'event_type' in df.columns and pd.notna(row.get('event_type')):
                event = {
                    'event_type': row['event_type'],
                    'event_label': row.get('event_label', None),
                    'turn_id': row['turn_id']
                }
                events.append(event)
        
        return {
            'transcript_id': transcript_id,
            'turns': turns,
            'events': events,
            'metadata': {}
        }
    
    def _load_txt(self, file_path: Path) -> Dict[str, Any]:
        """Load simple text format transcript"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Basic parsing: assume format like "Speaker: text"
        turns = []
        for i, line in enumerate(lines):
            line = line.strip()
            if ':' in line:
                parts = line.split(':', 1)
                speaker = parts[0].strip()
                text = parts[1].strip()
                turns.append({
                    'turn_id': i + 1,
                    'speaker': speaker,
                    'text': text,
                    'timestamp': None
                })
        
        return {
            'transcript_id': file_path.stem,
            'turns': turns,
            'events': [],
            'metadata': {}
        }
    
    def load_batch(self, directory: str, pattern: str = "*.json") -> List[Dict[str, Any]]:
        """Load multiple transcripts from a directory"""
        directory = Path(directory)
        transcripts = []
        
        for file_path in directory.glob(pattern):
            try:
                # Check if file contains a list of transcripts
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    # File contains list of transcripts
                    for item in data:
                        if isinstance(item, dict):
                            transcript = {
                                'transcript_id': item.get('transcript_id', f"{file_path.stem}_{len(transcripts)}"),
                                'turns': item.get('turns', []),
                                'events': item.get('events', []),
                                'metadata': item.get('metadata', {})
                            }
                            transcripts.append(transcript)
                else:
                    # Single transcript in file
                    transcript = self.load_transcript(str(file_path))
                    transcripts.append(transcript)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        return transcripts

