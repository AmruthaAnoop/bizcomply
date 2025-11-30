import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional, List
import os

class BusinessProfile:
    """Business Profile Management System"""
    
    def __init__(self, db_path: str = "business_profiles.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with business profiles table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT NOT NULL,
                registration_number TEXT,
                location TEXT NOT NULL,
                industry TEXT NOT NULL,
                business_type TEXT NOT NULL,
                employee_count TEXT,
                revenue_range TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profile_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES business_profiles (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_profile(self, profile_data: Dict) -> int:
        """Create a new business profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO business_profiles 
            (business_name, registration_number, location, industry, business_type, employee_count, revenue_range)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile_data.get('business_name'),
            profile_data.get('registration_number'),
            profile_data.get('location'),
            profile_data.get('industry'),
            profile_data.get('business_type'),
            profile_data.get('employee_count'),
            profile_data.get('revenue_range')
        ))
        
        profile_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return profile_id
    
    def get_active_profile(self) -> Optional[Dict]:
        """Get the currently active business profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM business_profiles 
            WHERE is_active = 1 
            ORDER BY updated_at DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'business_name', 'registration_number', 'location', 'industry', 
                      'business_type', 'employee_count', 'revenue_range', 'created_at', 'updated_at', 'is_active']
            return dict(zip(columns, row))
        
        return None
    
    def update_profile(self, profile_id: int, updates: Dict) -> bool:
        """Update business profile and track changes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current profile for history tracking
        cursor.execute('SELECT * FROM business_profiles WHERE id = ?', (profile_id,))
        current = cursor.fetchone()
        
        if not current:
            conn.close()
            return False
        
        columns = ['id', 'business_name', 'registration_number', 'location', 'industry', 
                  'business_type', 'employee_count', 'revenue_range', 'created_at', 'updated_at', 'is_active']
        current_dict = dict(zip(columns, current))
        
        # Update each field and track changes
        for field, new_value in updates.items():
            if field in current_dict and current_dict[field] != new_value:
                # Track change in history
                cursor.execute('''
                    INSERT INTO profile_history (profile_id, field_name, old_value, new_value)
                    VALUES (?, ?, ?, ?)
                ''', (profile_id, field, current_dict[field], new_value))
                
                # Update the field
                cursor.execute(f'''
                    UPDATE business_profiles 
                    SET {field} = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (new_value, profile_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_all_profiles(self) -> List[Dict]:
        """Get all business profiles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM business_profiles ORDER BY updated_at DESC')
        rows = cursor.fetchall()
        
        columns = ['id', 'business_name', 'registration_number', 'location', 'industry', 
                  'business_type', 'employee_count', 'revenue_range', 'created_at', 'updated_at', 'is_active']
        
        profiles = [dict(zip(columns, row)) for row in rows]
        conn.close()
        
        return profiles
    
    def delete_profile(self, profile_id: int) -> bool:
        """Delete a business profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM business_profiles WHERE id = ?', (profile_id,))
        cursor.execute('DELETE FROM profile_history WHERE profile_id = ?', (profile_id,))
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    
    def set_active_profile(self, profile_id: int) -> bool:
        """Set a profile as active"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deactivate all profiles
        cursor.execute('UPDATE business_profiles SET is_active = 0')
        
        # Activate the selected profile
        cursor.execute('UPDATE business_profiles SET is_active = 1 WHERE id = ?', (profile_id,))
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    
    def get_profile_history(self, profile_id: int) -> List[Dict]:
        """Get change history for a profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM profile_history 
            WHERE profile_id = ? 
            ORDER BY updated_at DESC
        ''', (profile_id,))
        
        rows = cursor.fetchall()
        
        columns = ['id', 'profile_id', 'field_name', 'old_value', 'new_value', 'updated_at']
        history = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        
        return history

# Global instance
business_profile_manager = BusinessProfile()
