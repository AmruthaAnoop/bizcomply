"""
Chat models and database operations for the BizComply application.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import sqlite3
from pydantic import BaseModel, Field
from config.config import DB_PATH

class Message(BaseModel):
    """Represents a single chat message."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sender_type: str  # 'user' or 'assistant'
    content: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Conversation(BaseModel):
    """Represents a conversation with multiple messages."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: Optional[str] = None
    title: str = "New Conversation"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatRepository:
    """Repository for chat-related database operations."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._create_tables()
    
    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """Ensure tables exist and add missing columns."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create conversations table if not exists (minimal version)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                business_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            ''')
            
            # Check and add missing columns
            cursor.execute("PRAGMA table_info(conversations)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            # Add columns that might be missing
            missing_columns = {
                'title': 'TEXT NOT NULL DEFAULT "New Conversation"',
                'is_active': 'INTEGER DEFAULT 1',
                'metadata': 'TEXT'
            }
            
            for col, col_type in missing_columns.items():
                if col not in existing_columns:
                    cursor.execute(f'ALTER TABLE conversations ADD COLUMN {col} {col_type}')
            
            # Create chat_messages table if not exists
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                sender_type TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )
            ''')
            
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id 
            ON chat_messages(conversation_id, created_at)
            ''')
            
            conn.commit()
    
    def create_conversation(self, conversation: Conversation) -> str:
        """Create a new conversation."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO conversations (id, business_id, title, created_at, updated_at, is_active, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                conversation.id,
                conversation.business_id,
                conversation.title,
                conversation.created_at,
                conversation.updated_at,
                int(conversation.is_active),
                str(conversation.metadata) if conversation.metadata else None
            ))
            conn.commit()
            return conversation.id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a conversation by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM conversations WHERE id = ?', (conversation_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def update_conversation(self, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """Update a conversation."""
        if not updates:
            return False
            
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values())
        values.append(conversation_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'UPDATE conversations SET {set_clause}, updated_at = ? WHERE id = ?',
                values + [datetime.utcnow().isoformat(), conversation_id]
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_user_conversations(self, business_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all conversations for a business."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM conversations 
            WHERE business_id = ? 
            ORDER BY updated_at DESC 
            LIMIT ? OFFSET ?
            ''', (business_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    def add_message(self, message: Message) -> str:
        """Add a message to a conversation."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO chat_messages (id, conversation_id, sender_type, content, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                message.id,
                message.conversation_id,
                message.sender_type,
                message.content,
                message.created_at,
                str(message.metadata) if message.metadata else None
            ))
            
            # Update conversation's updated_at timestamp
            cursor.execute('''
            UPDATE conversations 
            SET updated_at = ? 
            WHERE id = ?
            ''', (datetime.utcnow().isoformat(), message.conversation_id))
            
            conn.commit()
            return message.id
    
    def get_messages(self, conversation_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get messages for a conversation."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM chat_messages 
            WHERE conversation_id = ? 
            ORDER BY created_at ASC 
            LIMIT ? OFFSET ?
            ''', (conversation_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chat_messages WHERE conversation_id = ?', (conversation_id,))
            cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
            conn.commit()
            return cursor.rowcount > 0
