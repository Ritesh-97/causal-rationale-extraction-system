"""
Vector database integration for transcript storage and retrieval
"""

import os
import warnings
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

# Suppress ChromaDB telemetry warnings
warnings.filterwarnings("ignore", message=".*telemetry.*")


class VectorStore:
    """Manage vector database for transcript storage and retrieval"""
    
    def __init__(
        self,
        db_type: str = "chromadb",
        db_path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.db_type = db_type
        self.db_path = db_path or "./data/processed/vector_db"
        self.embedding_model_name = embedding_model
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize vector database
        if db_type == "chromadb":
            self._init_chromadb()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _init_chromadb(self):
        """Initialize ChromaDB"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Disable telemetry to avoid warnings
        os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
        
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="transcript_spans",
            metadata={"description": "Dialogue spans from transcripts"}
        )
    
    def add_transcript_spans(
        self,
        transcript_id: str,
        spans: List[Dict[str, Any]],
        events: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Add dialogue spans from a transcript to the vector database.
        
        Args:
            transcript_id: Unique identifier for the transcript
            spans: List of dialogue span dictionaries
            events: List of events associated with the transcript
        """
        if not spans:
            return
        
        # Prepare documents and metadata
        documents = []
        metadatas = []
        ids = []
        
        for span in spans:
            # Extract text
            text = span.get('text', '')
            if not text.strip():
                continue
            
            # Create unique ID
            span_id = span.get('span_id', f"{transcript_id}_span_{len(documents)}")
            
            # Prepare metadata
            metadata = {
                'transcript_id': transcript_id,
                'span_id': span_id,
                'start_turn_index': span.get('start_turn_index', -1),
                'end_turn_index': span.get('end_turn_index', -1),
                'turn_ids': str(span.get('turn_ids', [])),
                'speakers': ','.join(span.get('speakers', [])),
                'window_size': span.get('metadata', {}).get('window_size', 5)
            }
            
            # Add event information if available
            if events:
                # Find events that occur in or after this span
                span_events = [
                    e for e in events
                    if e.get('turn_id') and e.get('turn_id') in span.get('turn_ids', [])
                ]
                if span_events:
                    metadata['has_event'] = True
                    metadata['event_types'] = ','.join([e.get('event_type', '') for e in span_events])
                else:
                    metadata['has_event'] = False
                    metadata['event_types'] = ''
            else:
                metadata['has_event'] = False
                metadata['event_types'] = ''
            
            documents.append(text)
            metadatas.append(metadata)
            ids.append(span_id)
        
        # Add to collection
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant dialogue spans.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_dict: Optional metadata filters
        
        Returns:
            List of search results with metadata
        """
        # Build where clause for filtering
        where = None
        if filter_dict:
            where = filter_dict
        
        # Perform search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                result = {
                    'span_id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for a list of texts"""
        return self.embedding_model.encode(texts, show_progress_bar=False)
    
    def clear_collection(self):
        """Clear all data from the collection"""
        self.client.delete_collection(name="transcript_spans")
        self.collection = self.client.get_or_create_collection(
            name="transcript_spans",
            metadata={"description": "Dialogue spans from transcripts"}
        )

