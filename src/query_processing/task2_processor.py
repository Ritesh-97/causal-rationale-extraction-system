"""
Task 2: Conversational follow-up and contextual response generation processor
"""

from typing import Dict, Any, Optional, List
from .task1_processor import Task1Processor
from ..conversation_manager.context_manager import ContextManager
from ..conversation_manager.followup_processor import FollowUpProcessor


class Task2Processor:
    """Process queries for Task 2: Contextual follow-up conversations"""
    
    def __init__(
        self,
        task1_processor: Task1Processor,
        context_manager: ContextManager,
        followup_processor: FollowUpProcessor
    ):
        self.task1_processor = task1_processor
        self.context_manager = context_manager
        self.followup_processor = followup_processor
    
    def process_query(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process a query with context awareness.
        Handles both initial queries (Task 1) and follow-up queries (Task 2).
        
        Args:
            query: Natural language query
            conversation_id: Optional conversation ID for context tracking
            context: Optional explicit context
        
        Returns:
            Dictionary with response and evidence
        """
        # Get or create conversation
        if conversation_id is None:
            conversation_id = self.context_manager.get_or_create_conversation().conversation_id
        
        # Check if this is a follow-up
        is_followup = self.context_manager.is_followup(query, conversation_id)
        
        if is_followup and (context or self.context_manager.get_context(conversation_id)):
            # Process as follow-up (Task 2)
            result = self.followup_processor.process_followup(
                query=query,
                conversation_id=conversation_id,
                context=context
            )
            
            # Format response
            formatted = self.followup_processor.format_response(result)
        else:
            # Process as initial query (Task 1)
            result = self.task1_processor.process_query(query)
            
            # Format response
            formatted = self.task1_processor.format_response(result)
            
            # Add to conversation context
            self.context_manager.add_turn(
                conversation_id=conversation_id,
                query=query,
                response=formatted['response'],
                metadata={
                    'is_followup': False,
                    'event_type': result['parsed_query'].get('event_type'),
                    'evidence_count': result['evidence_count']
                }
            )
            
            # Add metadata
            formatted['metadata']['conversation_id'] = conversation_id
            formatted['metadata']['is_followup'] = False
        
        return formatted

