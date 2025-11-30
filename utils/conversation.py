from typing import List, Dict, Any, Optional
from datetime import datetime

class Message:
    """Represents a single message in a conversation."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[float] = None):
        """
        Initialize a message.
        
        Args:
            role: The role of the message sender ('user', 'assistant', 'system')
            content: The content of the message
            timestamp: Optional timestamp (defaults to current time)
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create a Message from a dictionary."""
        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=data.get('timestamp')
        )

class Conversation:
    """Manages a conversation with a user, including history and context."""
    
    def __init__(self, conversation_id: str = None, system_prompt: str = None):
        """
        Initialize a new conversation.
        
        Args:
            conversation_id: Optional unique ID for the conversation
            system_prompt: Optional system prompt to initialize the conversation
        """
        self.conversation_id = conversation_id or f"conv_{int(datetime.now().timestamp())}"
        self.messages: List[Message] = []
        self.metadata = {
            'created_at': datetime.now().timestamp(),
            'updated_at': datetime.now().timestamp(),
            'title': 'New Chat',
            'response_mode': 'concise'  # or 'detailed'
        }
        
        # Add system prompt if provided
        if system_prompt:
            self.add_message('system', system_prompt)
    
    def add_message(self, role: str, content: str) -> 'Message':
        """
        Add a message to the conversation.
        
        Args:
            role: The role of the message sender
            content: The message content
            
        Returns:
            The created Message object
        """
        message = Message(role, content)
        self.messages.append(message)
        self.metadata['updated_at'] = datetime.now().timestamp()
        return message
    
    def get_recent_messages(self, max_messages: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent messages in the conversation.
        
        Args:
            max_messages: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        recent = self.messages[-max_messages:]
        return [msg.to_dict() for msg in recent]
    
    def get_formatted_history(self, max_messages: int = 10) -> str:
        """
        Get the conversation history as a formatted string.
        
        Args:
            max_messages: Maximum number of messages to include
            
        Returns:
            Formatted conversation history as a string
        """
        history = []
        for msg in self.messages[-max_messages:]:
            role = "User" if msg.role == "user" else "Assistant"
            history.append(f"{role}: {msg.content}")
        
        return "\n---\n".join(history)
    
    def set_response_mode(self, mode: str) -> None:
        """Set the response mode ('concise' or 'detailed')."""
        if mode not in ['concise', 'detailed']:
            raise ValueError("Response mode must be 'concise' or 'detailed'")
        self.metadata['response_mode'] = mode
    
    def get_response_mode(self) -> str:
        """Get the current response mode."""
        return self.metadata.get('response_mode', 'concise')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the conversation to a dictionary."""
        return {
            'conversation_id': self.conversation_id,
            'messages': [msg.to_dict() for msg in self.messages],
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create a Conversation from a dictionary."""
        conv = cls(conversation_id=data['conversation_id'])
        conv.messages = [Message.from_dict(msg) for msg in data.get('messages', [])]
        conv.metadata = data.get('metadata', {})
        return conv

class ConversationManager:
    """Manages multiple conversations."""
    
    def __init__(self):
        """Initialize the conversation manager."""
        self.conversations: Dict[str, Conversation] = {}
    
    def create_conversation(self, system_prompt: str = None) -> str:
        """
        Create a new conversation.
        
        Args:
            system_prompt: Optional system prompt
            
        Returns:
            The ID of the new conversation
        """
        conv = Conversation(system_prompt=system_prompt)
        self.conversations[conv.conversation_id] = conv
        return conv.conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: The ID of the conversation to retrieve
            
        Returns:
            The Conversation object, or None if not found
        """
        return self.conversations.get(conversation_id)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: The ID of the conversation to delete
            
        Returns:
            True if the conversation was deleted, False if not found
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
