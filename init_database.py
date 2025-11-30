#!/usr/bin/env python3
"""
Database initialization script for BizComply
"""

import sqlite3
import os
from config.config import DB_PATH

def init_database():
    """Initialize the database with all required tables"""
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Create business_profiles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_profiles (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            business_type TEXT NOT NULL,
            jurisdiction TEXT NOT NULL,
            compliance_score REAL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # Create regulatory_updates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS regulatory_updates (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT,
            link TEXT NOT NULL,
            published TEXT,
            source TEXT NOT NULL,
            categories TEXT,
            metadata TEXT,
            relevance_score REAL DEFAULT 0.0,
            affected_businesses TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
        ''')
        
        # Create update_business_impact table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS update_business_impact (
            update_id TEXT,
            business_id TEXT,
            impact_score REAL,
            affected_areas TEXT,
            action_items TEXT,
            deadline TEXT,
            severity TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            PRIMARY KEY (update_id, business_id),
            FOREIGN KEY (update_id) REFERENCES regulatory_updates (id) ON DELETE CASCADE,
            FOREIGN KEY (business_id) REFERENCES business_profiles (id) ON DELETE CASCADE
        )
        ''')
        
        # Create compliance_tasks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS compliance_tasks (
            id TEXT PRIMARY KEY,
            business_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'medium',
            assigned_to TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (business_id) REFERENCES business_profiles (id) ON DELETE CASCADE
        )
        ''')
        
        # Create documents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            business_id TEXT,
            title TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            size INTEGER,
            uploaded_at TEXT NOT NULL,
            processed_at TEXT,
            metadata TEXT,
            FOREIGN KEY (business_id) REFERENCES business_profiles (id) ON DELETE CASCADE
        )
        ''')
        
        # Create conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            business_id TEXT,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            metadata TEXT,
            FOREIGN KEY (business_id) REFERENCES business_profiles (id) ON DELETE CASCADE
        )
        ''')
        
        # Create chat_messages table
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
        
        # Create index for faster message retrieval
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id 
        ON chat_messages(conversation_id, created_at)
        ''')
        
        conn.commit()
        print("✅ Database initialized successfully!")
        print(f"📁 Database location: {DB_PATH}")
        print("📊 Created tables:")
        print("   - business_profiles")
        print("   - regulatory_updates")
        print("   - update_business_impact")
        print("   - compliance_tasks")
        print("   - documents")
        print("   - conversations")
        print("   - chat_messages")
    print("✅ Database initialized successfully!")
    print(f"📁 Database location: {DB_PATH}")
    
    # Verify tables were created
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")

if __name__ == "__main__":
    init_database()
