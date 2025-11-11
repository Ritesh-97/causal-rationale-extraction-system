"""
Main data processing pipeline
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .transcript_loader import TranscriptLoader
from .preprocessor import TranscriptPreprocessor
from .vector_store import VectorStore
import json


class DataProcessingPipeline:
    """End-to-end data processing pipeline"""
    
    def __init__(
        self,
        vector_db_path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        span_window_size: int = 5
    ):
        self.loader = TranscriptLoader()
        self.preprocessor = TranscriptPreprocessor()
        self.vector_store = VectorStore(
            db_path=vector_db_path,
            embedding_model=embedding_model
        )
        self.span_window_size = span_window_size
    
    def process_transcript(
        self,
        transcript_path: str,
        index_to_vector_db: bool = True
    ) -> Dict[str, Any]:
        """
        Process a single transcript file.
        
        Args:
            transcript_path: Path to transcript file
            index_to_vector_db: Whether to index spans to vector database
        
        Returns:
            Processed transcript dictionary
        """
        # Load transcript
        transcript = self.loader.load_transcript(transcript_path)
        
        # Preprocess
        processed = self.preprocessor.preprocess(transcript)
        
        # Extract dialogue spans
        spans = self.preprocessor.extract_dialogue_spans(
            processed['turns'],
            window_size=self.span_window_size
        )
        
        # Index to vector database
        if index_to_vector_db and spans:
            self.vector_store.add_transcript_spans(
                transcript_id=processed['transcript_id'],
                spans=spans,
                events=processed.get('events', [])
            )
        
        # Add spans to processed transcript
        processed['spans'] = spans
        
        return processed
    
    def process_batch(
        self,
        input_directory: str,
        output_directory: Optional[str] = None,
        file_pattern: str = "*.json",
        index_to_vector_db: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process multiple transcripts from a directory.
        
        Args:
            input_directory: Directory containing transcript files
            output_directory: Optional directory to save processed transcripts
            file_pattern: File pattern to match
            index_to_vector_db: Whether to index spans to vector database
        
        Returns:
            List of processed transcript dictionaries
        """
        input_dir = Path(input_directory)
        processed_transcripts = []
        
        # Process each transcript file
        for file_path in input_dir.glob(file_pattern):
            try:
                # Check if file contains a list of transcripts
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    # File contains list of transcripts - process each one
                    for i, transcript_data in enumerate(data):
                        try:
                            # Create a temporary transcript dict
                            transcript = {
                                'transcript_id': transcript_data.get('transcript_id', f"{file_path.stem}_{i}"),
                                'turns': transcript_data.get('turns', []),
                                'events': transcript_data.get('events', []),
                                'metadata': transcript_data.get('metadata', {})
                            }
                            
                            # Preprocess
                            processed = self.preprocessor.preprocess(transcript)
                            
                            # Extract dialogue spans
                            spans = self.preprocessor.extract_dialogue_spans(
                                processed['turns'],
                                window_size=self.span_window_size
                            )
                            
                            # Index to vector database
                            if index_to_vector_db and spans:
                                self.vector_store.add_transcript_spans(
                                    transcript_id=processed['transcript_id'],
                                    spans=spans,
                                    events=processed.get('events', [])
                                )
                            
                            # Add spans to processed transcript
                            processed['spans'] = spans
                            processed_transcripts.append(processed)
                            
                            # Save processed transcript if output directory specified
                            if output_directory:
                                output_dir = Path(output_directory)
                                output_dir.mkdir(parents=True, exist_ok=True)
                                
                                output_file = output_dir / f"{processed['transcript_id']}.json"
                                with open(output_file, 'w', encoding='utf-8') as f:
                                    json.dump(processed, f, indent=2, ensure_ascii=False)
                        except Exception as e:
                            print(f"Error processing transcript {i} in {file_path}: {e}")
                            continue
                else:
                    # Single transcript in file
                    processed = self.process_transcript(
                        str(file_path),
                        index_to_vector_db=index_to_vector_db
                    )
                    processed_transcripts.append(processed)
                    
                    # Save processed transcript if output directory specified
                    if output_directory:
                        output_dir = Path(output_directory)
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        output_file = output_dir / f"{processed['transcript_id']}.json"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(processed, f, indent=2, ensure_ascii=False)
            
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        return processed_transcripts
    
    def get_vector_store(self) -> VectorStore:
        """Get the vector store instance"""
        return self.vector_store

