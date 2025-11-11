"""
Conversation context management for multi-turn dialogues
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation"""
    turn_id: str
    query: str
    response: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Manages context for a conversation session"""
    conversation_id: str
    turns: List[ConversationTurn] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_turn(self, query: str, response: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a turn to the conversation"""
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            query=query,
            response=response,
            metadata=metadata or {}
        )
        self.turns.append(turn)
        self.updated_at = datetime.now()
    
    def get_recent_turns(self, n: int = 3) -> List[ConversationTurn]:
        """Get the most recent n turns"""
        return self.turns[-n:] if len(self.turns) > n else self.turns
    
    def get_context_summary(self) -> str:
        """Get a summary of the conversation context"""
        if not self.turns:
            return ""
        
        summary_parts = []
        for turn in self.get_recent_turns(3):
            summary_parts.append(f"Q: {turn.query}")
            summary_parts.append(f"A: {turn.response[:200]}...")  # Truncate
        
        return "\n".join(summary_parts)


class ContextManager:
    """Manage conversation contexts across sessions"""
    
    def __init__(self, max_context_length: int = 4000):
        self.conversations: Dict[str, ConversationContext] = {}
        self.max_context_length = max_context_length
    
    def get_or_create_conversation(self, conversation_id: Optional[str] = None) -> ConversationContext:
        """Get existing conversation or create a new one"""
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationContext(
                conversation_id=conversation_id
            )
        
        return self.conversations[conversation_id]
    
    def add_turn(
        self,
        conversation_id: str,
        query: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a turn to a conversation"""
        conversation = self.get_or_create_conversation(conversation_id)
        conversation.add_turn(query, response, metadata)
    
    def get_context(self, conversation_id: str) -> Optional[ConversationContext]:
        """Get conversation context"""
        return self.conversations.get(conversation_id)
    
    def get_context_summary(self, conversation_id: str) -> str:
        """Get context summary for a conversation"""
        conversation = self.get_or_create_conversation(conversation_id)
        return conversation.get_context_summary()
    
    def clear_conversation(self, conversation_id: str):
        """Clear a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def is_followup(self, query: str, conversation_id: str) -> bool:
        """
        Determine if a query is a follow-up to previous conversation.
        
        Args:
            query: Current query text
            conversation_id: Conversation ID
        
        Returns:
            True if query appears to be a follow-up
        """
        conversation = self.get_context(conversation_id)
        if not conversation or not conversation.turns:
            return False
        
        # Check for follow-up indicators
        followup_indicators = [
            'also', 'additionally', 'furthermore', 'moreover',
            'what about', 'how about', 'tell me more', 'can you',
            'what else', 'another', 'other', 'different',
            'it', 'that', 'this', 'these', 'those', 'they'
        ]
        
        query_lower = query.lower()
        
        # Check for explicit follow-up indicators
        for indicator in followup_indicators:
            if indicator in query_lower:
                return True
        
        # Check for pronouns (likely referring to previous context)
        pronouns = ['it', 'that', 'this', 'these', 'those', 'they', 'them']
        query_words = query_lower.split()
        if any(word in pronouns for word in query_words):
            return True
        
        # Check query length (short queries are often follow-ups)
        if len(query.split()) < 5:
            return True
        
        return False

