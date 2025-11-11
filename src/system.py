"""
System initialization and component wiring
"""

import os
from typing import Optional
from .data_processing.pipeline import DataProcessingPipeline
from .data_processing.vector_store import VectorStore
from .retrieval.retrieval_pipeline import RetrievalPipeline
from .causal_analysis.causal_analyzer import CausalAnalyzer
from .explanation_generation.explanation_generator import ExplanationGenerator
from .query_processing.task1_processor import Task1Processor
from .conversation_manager.context_manager import ContextManager
from .conversation_manager.followup_processor import FollowUpProcessor
from .query_processing.task2_processor import Task2Processor


class System:
    """Main system class that initializes and wires all components"""
    
    def __init__(
        self,
        vector_db_path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        llm_provider: str = "openai",
        llm_model: str = "gpt-4"
    ):
        # Initialize data processing pipeline
        self.data_pipeline = DataProcessingPipeline(
            vector_db_path=vector_db_path or os.getenv("VECTOR_DB_PATH", "./data/processed/vector_db"),
            embedding_model=embedding_model
        )
        
        # Get vector store
        self.vector_store = self.data_pipeline.get_vector_store()
        
        # Initialize retrieval pipeline
        self.retrieval_pipeline = RetrievalPipeline(
            vector_store=self.vector_store,
            embedding_model=embedding_model,
            reranker_model=reranker_model,
            use_reranking=True
        )
        
        # Initialize causal analyzer
        self.causal_analyzer = CausalAnalyzer()
        
        # Initialize explanation generator
        self.explanation_generator = ExplanationGenerator(
            retrieval_pipeline=self.retrieval_pipeline,
            causal_analyzer=self.causal_analyzer,
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        
        # Initialize Task 1 processor
        self.task1_processor = Task1Processor(
            retrieval_pipeline=self.retrieval_pipeline,
            causal_analyzer=self.causal_analyzer,
            explanation_generator=self.explanation_generator
        )
        
        # Initialize context manager
        self.context_manager = ContextManager()
        
        # Initialize follow-up processor
        self.followup_processor = FollowUpProcessor(
            context_manager=self.context_manager,
            retrieval_pipeline=self.retrieval_pipeline,
            causal_analyzer=self.causal_analyzer,
            explanation_generator=self.explanation_generator
        )
        
        # Initialize Task 2 processor
        self.task2_processor = Task2Processor(
            task1_processor=self.task1_processor,
            context_manager=self.context_manager,
            followup_processor=self.followup_processor
        )
    
    def process_query(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        context: Optional[list] = None
    ):
        """Process a query (handles both Task 1 and Task 2)"""
        return self.task2_processor.process_query(
            query=query,
            conversation_id=conversation_id,
            context=context
        )
    
    def process_followup(
        self,
        query: str,
        conversation_id: str,
        context: Optional[list] = None
    ):
        """Process a follow-up query (Task 2)"""
        return self.followup_processor.process_followup(
            query=query,
            conversation_id=conversation_id,
            context=context
        )


# Global system instance
_system_instance: Optional[System] = None


def get_system() -> System:
    """Get or create system instance"""
    global _system_instance
    if _system_instance is None:
        # Get default provider and model
        default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
        if default_provider == "gemini":
            default_model = os.getenv("DEFAULT_LLM_MODEL", "gemini-2.0-flash")
        elif default_provider == "openai":
            default_model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
        elif default_provider == "anthropic":
            default_model = os.getenv("DEFAULT_LLM_MODEL", "claude-3-opus-20240229")
        else:
            default_model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
        
        _system_instance = System(
            vector_db_path=os.getenv("VECTOR_DB_PATH", "./data/processed/vector_db"),
            embedding_model=os.getenv("DEFAULT_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2",
            llm_provider=default_provider,
            llm_model=default_model
        )
    return _system_instance

