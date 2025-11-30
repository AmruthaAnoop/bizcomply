import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
import json
import uuid
from pathlib import Path

from config.config import (
    DB_PATH, BusinessType, Jurisdiction, ComplianceStatus,
    DEFAULT_BUSINESS_TYPE, DEFAULT_JURISDICTION
)

@dataclass
class BusinessProfile:
    """Represents a business entity for compliance tracking."""
    id: str
    name: str
    business_type: BusinessType
    jurisdiction: Jurisdiction
    registration_number: str
    registration_date: str
    address: Dict[str, str]
    contact: Dict[str, str]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the business profile to a dictionary."""
        data = asdict(self)
        data['business_type'] = self.business_type.value
        data['jurisdiction'] = self.jurisdiction.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusinessProfile':
        """Create a BusinessProfile from a dictionary."""
        data['business_type'] = BusinessType(data['business_type'])
        data['jurisdiction'] = Jurisdiction(data['jurisdiction'])
        return cls(**data)

@dataclass
class ComplianceRequirement:
    """Represents a compliance requirement for a business."""
    id: str
    business_id: str
    title: str
    description: str
    category: str
    due_date: str
    status: ComplianceStatus
    jurisdiction: str
    authority: str
    reference_url: str = ""
    completed_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the compliance requirement to a dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceRequirement':
        """Create a ComplianceRequirement from a dictionary."""
        data['status'] = ComplianceStatus(data['status'])
        return cls(**data)

class ComplianceEngine:
    """Core engine for managing business compliance requirements."""
    
    def __init__(self, db_path: str = DB_PATH):
        """Initialize the compliance engine with a SQLite database."""
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self) -> None:
        """Initialize the database with required tables."""
        with self._get_connection() as conn:
            # Create business profiles table
            # Create or update business_profiles table
            conn.execute('''
            CREATE TABLE IF NOT EXISTS business_profiles (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                business_type TEXT NOT NULL,
                jurisdiction TEXT NOT NULL,
                registration_number TEXT NOT NULL,
                registration_date TEXT NOT NULL,
                address TEXT NOT NULL,
                contact TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
            ''')
            
            # Create compliance requirements table
            # Ensure new columns exist (simple migration)
            expected_cols = {
                'registration_number': 'TEXT',
                'registration_date': 'TEXT',
                'address': 'TEXT',
                'contact': 'TEXT',
                'metadata': 'TEXT',
            }
            cursor = conn.execute("PRAGMA table_info(business_profiles)")
            existing = {row[1] for row in cursor.fetchall()}
            for col, col_type in expected_cols.items():
                if col not in existing:
                    conn.execute(f"ALTER TABLE business_profiles ADD COLUMN {col} {col_type}")

            conn.execute('''
            CREATE TABLE IF NOT EXISTS compliance_requirements (
                id TEXT PRIMARY KEY,
                business_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL,
                jurisdiction TEXT NOT NULL,
                authority TEXT NOT NULL,
                reference_url TEXT,
                completed_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES business_profiles (id)
            )
            ''')
            
            # Create indexes for better query performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_business_id ON compliance_requirements(business_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON compliance_requirements(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_due_date ON compliance_requirements(due_date)')
            
            conn.commit()
    
    def create_business_profile(self, **kwargs) -> BusinessProfile:
        """Create a new business profile."""
        business_id = str(uuid.uuid4())
        business_type = kwargs.get('business_type', DEFAULT_BUSINESS_TYPE)
        jurisdiction = kwargs.get('jurisdiction', DEFAULT_JURISDICTION)
        
        if isinstance(business_type, BusinessType):
            business_type = business_type.value
        if isinstance(jurisdiction, Jurisdiction):
            jurisdiction = jurisdiction.value
        
        business = BusinessProfile(
            id=business_id,
            name=kwargs['name'],
            business_type=BusinessType(business_type),
            jurisdiction=Jurisdiction(jurisdiction),
            registration_number=kwargs['registration_number'],
            registration_date=kwargs.get('registration_date', datetime.utcnow().date().isoformat()),
            address=kwargs['address'],
            contact=kwargs['contact'],
            metadata=kwargs.get('metadata', {})
        )
        
        with self._get_connection() as conn:
            conn.execute('''
            INSERT INTO business_profiles 
            (id, name, business_type, jurisdiction, registration_number, registration_date, 
             address, contact, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                business.id,
                business.name,
                business.business_type.value,
                business.jurisdiction.value,
                business.registration_number,
                business.registration_date,
                json.dumps(business.address),
                json.dumps(business.contact),
                business.created_at,
                business.updated_at,
                json.dumps(business.metadata)
            ))
            conn.commit()
        
        return business
    
    def get_business_profile(self, business_id: str) -> Optional[BusinessProfile]:
        """Retrieve a business profile by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM business_profiles WHERE id = ?', (business_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return BusinessProfile(
                id=row['id'],
                name=row['name'],
                business_type=BusinessType(row['business_type']),
                jurisdiction=Jurisdiction(row['jurisdiction']),
                registration_number=row['registration_number'],
                registration_date=row['registration_date'],
                address=json.loads(row['address']),
                contact=json.loads(row['contact']),
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                metadata=json.loads(row['metadata'])
            )
    
    def list_business_profiles(self) -> List[BusinessProfile]:
        """List all business profiles."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM business_profiles')
            return [
                BusinessProfile(
                    id=row['id'],
                    name=row['name'],
                    business_type=BusinessType(row['business_type']),
                    jurisdiction=Jurisdiction(row['jurisdiction']),
                    registration_number=row['registration_number'],
                    registration_date=row['registration_date'],
                    address=json.loads(row['address']),
                    contact=json.loads(row['contact']),
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    metadata=json.loads(row['metadata'])
                )
                for row in cursor.fetchall()
            ]
    
    def update_business_profile(self, business_id: str, **updates) -> Optional[BusinessProfile]:
        """Update a business profile."""
        business = self.get_business_profile(business_id)
        if not business:
            return None
        
        # Update fields if provided
        for field, value in updates.items():
            if hasattr(business, field):
                if field == 'business_type':
                    setattr(business, field, BusinessType(value))
                elif field == 'jurisdiction':
                    setattr(business, field, Jurisdiction(value))
                elif field in ('address', 'contact', 'metadata') and isinstance(value, dict):
                    current = getattr(business, field, {}) or {}
                    current.update(value)
                    setattr(business, field, current)
                else:
                    setattr(business, field, value)
        
        business.updated_at = datetime.utcnow().isoformat()
        
        with self._get_connection() as conn:
            conn.execute('''
            UPDATE business_profiles 
            SET name = ?, business_type = ?, jurisdiction = ?, 
                registration_number = ?, registration_date = ?, 
                address = ?, contact = ?, updated_at = ?, metadata = ?
            WHERE id = ?
            ''', (
                business.name,
                business.business_type.value,
                business.jurisdiction.value,
                business.registration_number,
                business.registration_date,
                json.dumps(business.address),
                json.dumps(business.contact),
                business.updated_at,
                json.dumps(business.metadata),
                business.id
            ))
            conn.commit()
        
        return business
    
    def delete_business_profile(self, business_id: str) -> bool:
        """Delete a business profile and all its compliance requirements."""
        with self._get_connection() as conn:
            # First delete all compliance requirements for this business
            conn.execute('DELETE FROM compliance_requirements WHERE business_id = ?', (business_id,))
            
            # Then delete the business profile
            cursor = conn.execute('DELETE FROM business_profiles WHERE id = ?', (business_id,))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def add_compliance_requirement(self, business_id: str, **kwargs) -> ComplianceRequirement:
        """Add a new compliance requirement for a business."""
        if not self.get_business_profile(business_id):
            raise ValueError(f"Business with ID {business_id} does not exist")
        
        requirement_id = str(uuid.uuid4())
        status = kwargs.get('status', ComplianceStatus.PENDING)
        
        if isinstance(status, str):
            status = ComplianceStatus(status.lower())
        
        requirement = ComplianceRequirement(
            id=requirement_id,
            business_id=business_id,
            title=kwargs['title'],
            description=kwargs['description'],
            category=kwargs['category'],
            due_date=kwargs['due_date'],
            status=status,
            jurisdiction=kwargs['jurisdiction'],
            authority=kwargs['authority'],
            reference_url=kwargs.get('reference_url', ''),
            completed_date=kwargs.get('completed_date'),
            metadata=kwargs.get('metadata', {})
        )
        
        with self._get_connection() as conn:
            conn.execute('''
            INSERT INTO compliance_requirements 
            (id, business_id, title, description, category, due_date, status, 
             jurisdiction, authority, reference_url, completed_date, 
             created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                requirement.id,
                requirement.business_id,
                requirement.title,
                requirement.description,
                requirement.category,
                requirement.due_date,
                requirement.status.value,
                requirement.jurisdiction,
                requirement.authority,
                requirement.reference_url,
                requirement.completed_date,
                requirement.created_at,
                requirement.updated_at,
                json.dumps(requirement.metadata)
            ))
            conn.commit()
        
        return requirement
    
    def get_compliance_requirement(self, requirement_id: str) -> Optional[ComplianceRequirement]:
        """Retrieve a compliance requirement by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM compliance_requirements WHERE id = ?', (requirement_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return ComplianceRequirement(
                id=row['id'],
                business_id=row['business_id'],
                title=row['title'],
                description=row['description'],
                category=row['category'],
                due_date=row['due_date'],
                status=ComplianceStatus(row['status']),
                jurisdiction=row['jurisdiction'],
                authority=row['authority'],
                reference_url=row['reference_url'],
                completed_date=row['completed_date'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                metadata=json.loads(row['metadata'])
            )
    
    def list_compliance_requirements(self, business_id: str = None, status: str = None) -> List[ComplianceRequirement]:
        """List compliance requirements, optionally filtered by business ID and/or status."""
        query = 'SELECT * FROM compliance_requirements'
        params = []
        
        conditions = []
        if business_id:
            conditions.append('business_id = ?')
            params.append(business_id)
        if status:
            conditions.append('status = ?')
            params.append(status.lower())
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [
                ComplianceRequirement(
                    id=row['id'],
                    business_id=row['business_id'],
                    title=row['title'],
                    description=row['description'],
                    category=row['category'],
                    due_date=row['due_date'],
                    status=ComplianceStatus(row['status']),
                    jurisdiction=row['jurisdiction'],
                    authority=row['authority'],
                    reference_url=row['reference_url'],
                    completed_date=row['completed_date'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    metadata=json.loads(row['metadata'])
                )
                for row in cursor.fetchall()
            ]
    
    def update_compliance_requirement(self, requirement_id: str, **updates) -> Optional[ComplianceRequirement]:
        """Update a compliance requirement."""
        requirement = self.get_compliance_requirement(requirement_id)
        if not requirement:
            return None
        
        # Update fields if provided
        for field, value in updates.items():
            if hasattr(requirement, field):
                if field == 'status':
                    if isinstance(value, str):
                        value = ComplianceStatus(value.lower())
                    if value == ComplianceStatus.COMPLETED and not requirement.completed_date:
                        requirement.completed_date = datetime.utcnow().date().isoformat()
                    setattr(requirement, field, value)
                elif field in ('metadata',) and isinstance(value, dict):
                    current = getattr(requirement, field, {}) or {}
                    current.update(value)
                    setattr(requirement, field, current)
                else:
                    setattr(requirement, field, value)
        
        requirement.updated_at = datetime.utcnow().isoformat()
        
        with self._get_connection() as conn:
            conn.execute('''
            UPDATE compliance_requirements 
            SET title = ?, description = ?, category = ?, due_date = ?, 
                status = ?, jurisdiction = ?, authority = ?, reference_url = ?, 
                completed_date = ?, updated_at = ?, metadata = ?
            WHERE id = ?
            ''', (
                requirement.title,
                requirement.description,
                requirement.category,
                requirement.due_date,
                requirement.status.value,
                requirement.jurisdiction,
                requirement.authority,
                requirement.reference_url,
                requirement.completed_date,
                requirement.updated_at,
                json.dumps(requirement.metadata),
                requirement.id
            ))
            conn.commit()
        
        return requirement
    
    def delete_compliance_requirement(self, requirement_id: str) -> bool:
        """Delete a compliance requirement."""
        with self._get_connection() as conn:
            cursor = conn.execute('DELETE FROM compliance_requirements WHERE id = ?', (requirement_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_upcoming_requirements(self, days_ahead: int = 30) -> List[ComplianceRequirement]:
        """Get compliance requirements due within the next N days."""
        today = datetime.utcnow().date()
        future_date = (today + timedelta(days=days_ahead)).isoformat()
        
        query = '''
        SELECT * FROM compliance_requirements 
        WHERE due_date BETWEEN ? AND ? 
        AND status != ?
        ORDER BY due_date ASC
        '''
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                query, 
                (today.isoformat(), future_date, ComplianceStatus.COMPLETED.value)
            )
            
            return [
                ComplianceRequirement(
                    id=row['id'],
                    business_id=row['business_id'],
                    title=row['title'],
                    description=row['description'],
                    category=row['category'],
                    due_date=row['due_date'],
                    status=ComplianceStatus(row['status']),
                    jurisdiction=row['jurisdiction'],
                    authority=row['authority'],
                    reference_url=row['reference_url'],
                    completed_date=row['completed_date'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    metadata=json.loads(row['metadata'])
                )
                for row in cursor.fetchall()
            ]
    
    def generate_compliance_report(self, business_id: str) -> Dict[str, Any]:
        """Generate a compliance report for a business."""
        business = self.get_business_profile(business_id)
        if not business:
            raise ValueError(f"Business with ID {business_id} does not exist")
        
        requirements = self.list_compliance_requirements(business_id=business_id)
        
        # Categorize requirements by status
        by_status = {status.value: [] for status in ComplianceStatus}
        for req in requirements:
            by_status[req.status.value].append(req)
        
        # Count requirements by status
        status_counts = {status: len(reqs) for status, reqs in by_status.items()}
        
        # Find overdue requirements
        today = datetime.utcnow().date().isoformat()
        overdue = [
            req for req in requirements 
            if req.due_date < today and req.status != ComplianceStatus.COMPLETED
        ]
        
        # Find upcoming deadlines (next 30 days)
        upcoming_deadline = (datetime.utcnow() + timedelta(days=30)).date().isoformat()
        upcoming = [
            req for req in requirements
            if today <= req.due_date <= upcoming_deadline 
            and req.status != ComplianceStatus.COMPLETED
        ]
        
        return {
            'business': business.to_dict(),
            'summary': {
                'total_requirements': len(requirements),
                'status_counts': status_counts,
                'overdue_count': len(overdue),
                'upcoming_count': len(upcoming),
            },
            'by_status': {
                status: [req.to_dict() for req in reqs]
                for status, reqs in by_status.items()
            },
            'overdue': [req.to_dict() for req in overdue],
            'upcoming': [req.to_dict() for req in upcoming],
            'generated_at': datetime.utcnow().isoformat()
        }
