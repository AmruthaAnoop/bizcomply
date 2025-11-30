"""Compliance-related database models with enhanced features."""
from datetime import datetime, date, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any, Set
import json

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, 
    ForeignKey, JSON, Enum as SQLAEnum, Text, ForeignKeyConstraint,
    CheckConstraint, Table, event, DDL
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from sqlalchemy.sql import func, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from models.base import Base
from config.config import BusinessType, Jurisdiction

# Enums for compliance tracking
class RequirementStatus(str, Enum):
    """Status of a compliance requirement for a business."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    WAIVED = "waived"
    EXEMPT = "exempt"
    AT_RISK = "at_risk"
    OVERDUE = "overdue"
    DUE_SOON = "due_soon"

class RiskLevel(str, Enum):
    """Risk level for compliance requirements and findings."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MonitoringFrequency(str, Enum):
    """Frequency for compliance monitoring checks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    REAL_TIME = "real_time"

class JurisdictionType(str, Enum):
    """Types of jurisdictions for compliance requirements."""
    FEDERAL = "federal"
    STATE = "state"
    PROVINCE = "province"
    COUNTY = "county"
    CITY = "city"
    MUNICIPALITY = "municipality"
    INTERNATIONAL = "international"

class RequirementFrequency(str, Enum):
    """Frequency of a compliance requirement."""
    ONE_TIME = "one_time"
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"
    BIWEEKLY = "biweekly"
    WEEKLY = "weekly"
    DAILY = "daily"
    ON_CHANGE = "on_change"

class RequirementSeverity(str, Enum):
    """Severity level of a compliance requirement."""
    CRITICAL = "critical"  # Legal requirement with severe penalties
    HIGH = "high"          # Legal requirement with significant penalties
    MEDIUM = "medium"      # Legal requirement with moderate penalties
    LOW = "low"            # Best practice or minor requirement
    INFO = "info"          # Informational only

# Association table for many-to-many relationship between requirements and controls
requirement_controls = Table(
    'requirement_controls',
    Base.metadata,
    Column('requirement_id', String(36), ForeignKey('compliance_requirements.id')),
    Column('control_id', String(36), ForeignKey('compliance_controls.id'))
)

# Association table for requirement dependencies
requirement_dependencies = Table(
    'requirement_dependencies',
    Base.metadata,
    Column('requirement_id', String(36), ForeignKey('compliance_requirements.id')),
    Column('depends_on_id', String(36), ForeignKey('compliance_requirements.id'))
)

class ComplianceControl(Base):
    """Internal controls that help achieve compliance with requirements."""
    __tablename__ = 'compliance_controls'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    control_type = Column(String(100))  # preventive, detective, corrective
    frequency = Column(SQLAEnum(MonitoringFrequency), default=MonitoringFrequency.MONTHLY)
    owner_role = Column(String(100))
    is_automated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requirements = relationship(
        'ComplianceRequirement',
        secondary=requirement_controls,
        back_populates='controls'
    )
    
    def __repr__(self):
        return f"<ComplianceControl(id={self.id}, name='{self.name}')>"

class ComplianceRequirement(Base):
    """
    Template for compliance requirements that apply to businesses.
    Enhanced with risk assessment, monitoring, and multi-jurisdictional support.
    """
    __tablename__ = 'compliance_requirements'

    id = Column(String(36), primary_key=True)
    
    # Identification and Metadata
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # e.g., 'FED_TAX_941', 'STATE_CA_DE1'
    description = Column(Text, nullable=True)
    version = Column(String(20), default='1.0.0')
    effective_date = Column(Date, nullable=False, default=date.today)
    expiration_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Regulatory Metadata
    regulation_id = Column(String(100), nullable=True)  # External regulation ID
    regulation_name = Column(String(255), nullable=True)  # Name of the regulation
    regulation_url = Column(String(500), nullable=True)  # Link to regulation text
    
    # Change Tracking
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    change_frequency = Column(SQLAEnum(MonitoringFrequency), default=MonitoringFrequency.ANNUAL)
    last_checked = Column(DateTime, nullable=True)
    next_check_due = Column(DateTime, nullable=True)
    change_notes = Column(Text, nullable=True)
    
    # Categorization and Taxonomy
    category = Column(String(100), nullable=False, index=True)  # e.g., 'tax', 'labor', 'licensing'
    subcategory = Column(String(100), nullable=True, index=True)
    tags = Column(ARRAY(String), default=[], index=True)  # For flexible categorization
    framework = Column(String(100), nullable=True, index=True)  # e.g., 'GDPR', 'HIPAA', 'SOX'
    
    # Jurisdictional Applicability
    jurisdiction_type = Column(SQLAEnum(JurisdictionType), nullable=False, default=JurisdictionType.FEDERAL)
    jurisdiction_code = Column(String(10), nullable=True)  # e.g., 'CA', 'NY', 'EU'
    jurisdiction_name = Column(String(255), nullable=True)  # e.g., 'California', 'European Union'
    
    # Business Applicability
    business_structures = Column(ARRAY(String), nullable=True)  # List of business structure types
    industry_codes = Column(ARRAY(String), nullable=True)  # e.g., NAICS codes
    employee_count_min = Column(Integer, nullable=True)
    employee_count_max = Column(Integer, nullable=True)
    revenue_min = Column(Float, nullable=True)
    revenue_max = Column(Float, nullable=True)
    
    # Cross-border considerations
    has_cross_border_impact = Column(Boolean, default=False)
    applicable_countries = Column(ARRAY(String), nullable=True)  # ISO country codes
    
    # Timing and Deadlines
    frequency = Column(SQLAEnum(RequirementFrequency), nullable=False)
    due_date_rule = Column(JSONB, nullable=True)  # Rule for calculating due dates
    grace_period_days = Column(Integer, default=0)  # Days after due date before considered late
    
    # Monitoring Configuration
    monitoring_frequency = Column(SQLAEnum(MonitoringFrequency), nullable=True)
    monitoring_instructions = Column(Text, nullable=True)
    automated_monitoring = Column(Boolean, default=False)
    monitoring_script = Column(String(255), nullable=True)  # Reference to monitoring script
    
    # Risk Assessment
    inherent_risk = Column(SQLAEnum(RiskLevel), default=RiskLevel.MEDIUM)
    residual_risk = Column(SQLAEnum(RiskLevel), nullable=True)
    risk_score = Column(Integer, default=0)  # 0-100 scale
    risk_factors = Column(JSONB, nullable=True)  # Factors affecting risk score
    
    # Impact and Penalties
    severity = Column(SQLAEnum(RequirementSeverity), nullable=False, default=RequirementSeverity.MEDIUM)
    penalty_amount = Column(String(100), nullable=True)  # e.g., '$100 per day', '1% of revenue'
    penalty_currency = Column(String(3), default='USD')
    penalty_description = Column(Text, nullable=True)
    
    # Compliance Effort
    estimated_hours = Column(Float, nullable=True)  # Estimated hours to comply
    complexity = Column(String(20), nullable=True)  # low, medium, high
    
    # Regulatory Metadata
    issuing_agency = Column(String(100), nullable=True)  # e.g., 'IRS', 'CA EDD', 'OSHA'
    agency_contact = Column(String(255), nullable=True)
    reference_url = Column(String(500), nullable=True)
    
    # Compliance Workflow
    approval_required = Column(Boolean, default=False)
    approval_roles = Column(ARRAY(String), nullable=True)  # Roles that can approve
    notification_roles = Column(ARRAY(String), nullable=True)  # Roles to notify
    
    # System Metadata
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    controls = relationship(
        'ComplianceControl',
        secondary=requirement_controls,
        back_populates='requirements'
    )
    
    dependencies = relationship(
        'ComplianceRequirement',
        secondary=requirement_dependencies,
        primaryjoin='ComplianceRequirement.id==requirement_dependencies.c.requirement_id',
        secondaryjoin='ComplianceRequirement.id==requirement_dependencies.c.depends_on_id',
        backref='dependent_requirements'
    )
    
    # Methods
    def calculate_risk_score(self) -> int:
        """Calculate a risk score based on various factors."""
        score = 0
        
        # Base score from severity
        severity_scores = {
            RequirementSeverity.CRITICAL: 80,
            RequirementSeverity.HIGH: 60,
            RequirementSeverity.MEDIUM: 40,
            RequirementSeverity.LOW: 20,
            RequirementSeverity.INFO: 10
        }
        score += severity_scores.get(self.severity, 30)
        
        # Adjust based on frequency
        if self.frequency == RequirementFrequency.DAILY:
            score += 20
        elif self.frequency == RequirementFrequency.WEEKLY:
            score += 15
        elif self.frequency == RequirementFrequency.MONTHLY:
            score += 10
        
        # Adjust for cross-border impact
        if self.has_cross_border_impact:
            score += 15
            
        # Cap at 100
        return min(score, 100)
    
    def get_next_check_date(self) -> datetime:
        """Calculate the next check date based on monitoring frequency."""
        if not self.monitoring_frequency:
            return None
            
        last_checked = self.last_checked or datetime.utcnow()
        
        if self.monitoring_frequency == MonitoringFrequency.DAILY:
            return last_checked + timedelta(days=1)
        elif self.monitoring_frequency == MonitoringFrequency.WEEKLY:
            return last_checked + timedelta(weeks=1)
        elif self.monitoring_frequency == MonitoringFrequency.BIWEEKLY:
            return last_checked + timedelta(weeks=2)
        elif self.monitoring_frequency == MonitoringFrequency.MONTHLY:
            # Add approximately one month
            return last_checked.replace(month=last_checked.month % 12 + 1)
        elif self.monitoring_frequency == MonitoringFrequency.QUARTERLY:
            return last_checked + timedelta(days=90)
        elif self.monitoring_frequency == MonitoringFrequency.ANNUAL:
            return last_checked.replace(year=last_checked.year + 1)
        else:  # real_time
            return last_checked
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'severity': self.severity.value if self.severity else None,
            'risk_score': self.risk_score,
            'status': 'active' if self.is_active else 'inactive',
            'next_check_due': self.next_check_due.isoformat() if self.next_check_due else None,
            'jurisdiction': f"{self.jurisdiction_type.value}:{self.jurisdiction_code or 'global'}"
        }
    
    # Event listeners
    @validates('severity')
    def update_risk_on_severity_change(self, key, severity):
        """Update risk score when severity changes."""
        if hasattr(self, 'severity') and self.severity != severity:
            self.risk_score = self.calculate_risk_score()
        return severity
    
    # Relationships
    business_compliances: Mapped[List['BusinessCompliance']] = relationship(
        'BusinessCompliance', back_populates='requirement', cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        return f"<ComplianceRequirement(id={self.id}, code='{self.code}')>"

# Create GIN index for JSONB columns
event.listen(
    ComplianceRequirement.__table__,
    'after_create',
    DDL("""
        CREATE INDEX IF NOT EXISTS idx_requirement_metadata ON compliance_requirements 
        USING GIN (risk_factors);
    """)
)

class BusinessCompliance(Base):
    """
    Tracks a business's compliance with a specific requirement.
    Enhanced with risk assessment, evidence tracking, and workflow support.
    """
    __tablename__ = 'business_compliances'
    
    id = Column(String(36), primary_key=True)
    business_id = Column(String(36), ForeignKey('businesses.id'), nullable=False, index=True)
    requirement_id = Column(String(36), ForeignKey('compliance_requirements.id'), nullable=False, index=True)
    
    # Versioning
    version = Column(Integer, default=1, nullable=False)
    is_current = Column(Boolean, default=True, index=True)
    replaced_by_id = Column(String(36), ForeignKey('business_compliances.id'), nullable=True)
    
    # External References
    external_id = Column(String(100), nullable=True, index=True)  # External system ID
    external_url = Column(String(500), nullable=True)  # Link to external system
    
    # Status and Workflow
    status = Column(SQLAEnum(RequirementStatus), default=RequirementStatus.NOT_STARTED, nullable=False, index=True)
    status_notes = Column(Text, nullable=True)
    status_changed_at = Column(DateTime, nullable=True)
    status_changed_by = Column(String(100), nullable=True)
    
    # Risk Assessment
    business_risk = Column(SQLAEnum(RiskLevel), nullable=True)
    business_impact = Column(Text, nullable=True)
    risk_assessment_date = Column(Date, nullable=True)
    risk_owner = Column(String(100), nullable=True)  # Role or user ID
    
    # Evidence and Documentation
    evidence_required = Column(Boolean, default=False)
    evidence_description = Column(Text, nullable=True)
    evidence_due_date = Column(Date, nullable=True)
    evidence_submitted = Column(Boolean, default=False)
    evidence_submitted_at = Column(DateTime, nullable=True)
    evidence_notes = Column(Text, nullable=True)
    
    # Dates and Deadlines
    start_date = Column(Date, nullable=True)  # When this requirement first applied to the business
    end_date = Column(Date, nullable=True)    # When this requirement no longer applies
    
    # Compliance Period
    period_start = Column(Date, nullable=True)  # Start of current compliance period
    period_end = Column(Date, nullable=True)    # End of current compliance period
    
    # Tracking
    last_completed_date = Column(Date, nullable=True)
    next_due_date = Column(Date, nullable=True, index=True)
    reminder_sent_date = Column(Date, nullable=True)
    
    # Auto-calculation fields
    days_until_due = Column(Integer, nullable=True, index=True)
    is_overdue = Column(Boolean, default=False, index=True)
    
    # Historical tracking
    times_completed = Column(Integer, default=0)
    last_verified_at = Column(DateTime, nullable=True)
    last_verified_by = Column(String(100), nullable=True)
    
    # Custom fields and metadata
    custom_fields = Column(JSONB, nullable=True)  # For storing business-specific data
    metadata_ = Column('metadata', JSONB, nullable=True)  # System metadata
    
    # Audit information
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Compliance Score
    compliance_score = Column(Integer, nullable=True)  # 0-100 scale
    last_scored_at = Column(DateTime, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business: Mapped['Business'] = relationship('Business', back_populates='compliance_records')
    requirement: Mapped['ComplianceRequirement'] = relationship('ComplianceRequirement', back_populates='business_compliances')
    documents: Mapped[List['GeneratedDocument']] = relationship(
        'GeneratedDocument', 
        back_populates='compliance_record', 
        cascade='all, delete-orphan',
        order_by='desc(GeneratedDocument.created_at)'
    )
    
    # Versioning relationship
    replaced_by = relationship(
        'BusinessCompliance',
        remote_side=[id],
        backref=relationship('replaces', remote_side=[replaced_by_id])
    )
    
    # Related items
    tasks = relationship(
        'ComplianceTask',
        back_populates='business_compliance',
        order_by='desc(ComplianceTask.due_date)'
    )
    audits = relationship(
        'ComplianceAudit',
        back_populates='business_compliance',
        order_by='desc(ComplianceAudit.audit_date)'
    )
    findings = relationship(
        'ComplianceFinding',
        back_populates='business_compliance',
        order_by='desc(ComplianceFinding.severity), ComplianceFinding.due_date'
    )
    
    # Table configuration
    __table_args__ = (
        # Ensure only one active record per business/requirement
        # CheckConstraint(
        #     "(is_current = true) OR (replaced_by_id IS NOT NULL)",
        #     name='valid_versioning'
        # ),
        # Check for valid status transitions
        # CheckConstraint(
        #     "status IN ('not_started', 'in_progress', 'pending_review', 'completed', 'waived', 'exempt', 'at_risk', 'overdue', 'due_soon')",
        #     name='valid_status'
        # ),
        # Indexes for performance
        # Index('idx_business_requirement', 'business_id', 'requirement_id', unique=True, postgresql_where=text("is_current = true")),
        # Index('idx_compliance_dates', 'next_due_date', 'status'),
        # Index('idx_risk_assessment', 'business_risk', 'compliance_score')
    )
    
    # Methods
    def update_status(self, new_status: RequirementStatus, user_id: str = None, notes: str = None):
        """Update the status with validation and history tracking."""
        if self.status != new_status:
            self.status = new_status
            self.status_changed_at = datetime.utcnow()
            self.status_changed_by = user_id
            if notes:
                self.status_notes = notes
    
    def calculate_compliance_score(self) -> int:
        """Calculate a compliance score based on various factors."""
        score = 0
        
        # Base score from status
        status_scores = {
            RequirementStatus.COMPLETED: 100,
            RequirementStatus.WAIVED: 90,
            RequirementStatus.EXEMPT: 100,
            RequirementStatus.PENDING_REVIEW: 70,
            RequirementStatus.IN_PROGRESS: 50,
            RequirementStatus.NOT_STARTED: 10,
            RequirementStatus.AT_RISK: 40,
            RequirementStatus.OVERDUE: 20,
            RequirementStatus.DUE_SOON: 60
        }
        score = status_scores.get(self.status, 0)
        
        # Adjust based on timeliness
        if self.next_due_date and self.last_completed_date:
            days_late = (datetime.utcnow().date() - self.next_due_date).days
            if days_late > 0:  # Overdue
                score = max(0, score - min(30, days_late * 2))  # Cap penalty at 30 points
        
        # Adjust based on evidence
        if self.evidence_required and not self.evidence_submitted:
            score = max(0, score - 20)  # Penalty for missing evidence
            
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def to_dict(self, include_related: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result = {
            'id': self.id,
            'business_id': self.business_id,
            'requirement_id': self.requirement_id,
            'status': self.status.value if self.status else None,
            'status_changed_at': self.status_changed_at.isoformat() if self.status_changed_at else None,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'is_overdue': self.is_overdue,
            'days_until_due': self.days_until_due,
            'compliance_score': self.compliance_score,
            'business_risk': self.business_risk.value if self.business_risk else None,
            'evidence_required': self.evidence_required,
            'evidence_submitted': self.evidence_submitted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_related and self.requirement:
            result['requirement'] = self.requirement.to_dict()
            
        return result
    
    @property
    def is_compliant(self) -> bool:
        """Determine if the business is currently compliant with this requirement."""
        return self.status in [
            RequirementStatus.COMPLETED, 
            RequirementStatus.EXEMPT,
            RequirementStatus.WAIVED
        ] and not self.is_overdue
    
    def __repr__(self):
        return f"<BusinessCompliance(business_id={self.business_id}, requirement_id={self.requirement_id}, status='{self.status}')>"

# Create indexes for performance
event.listen(
    BusinessCompliance.__table__,
    'after_create',
    DDL("""
        CREATE INDEX IF NOT EXISTS idx_business_compliance_status 
        ON business_compliances (business_id, status) 
        WHERE is_current = true;
        
        CREATE INDEX IF NOT EXISTS idx_business_compliance_dates 
        ON business_compliances (next_due_date) 
        WHERE is_current = true;
        
        CREATE INDEX IF NOT EXISTS idx_business_compliance_risk 
        ON business_compliances (business_risk, compliance_score) 
        WHERE is_current = true;
    """)
)

class ComplianceCheckpoint(Base):
    """
    Historical record of a compliance check or submission.
    Enhanced with evidence tracking, approval workflow, and detailed status history.
    """
    __tablename__ = 'compliance_checkpoints'
    
    id = Column(String(36), primary_key=True)
    business_compliance_id = Column(String(36), ForeignKey('business_compliances.id'), nullable=False)
    
    # Checkpoint details
    checkpoint_type = Column(String(50), nullable=False, index=True)  # 'submission', 'verification', 'reminder', 'update', 'audit'
    status = Column(String(50), nullable=False, index=True)  # 'pending', 'submitted', 'approved', 'rejected', 'failed', 'in_review'
    
    # Workflow
    workflow_stage = Column(String(50), nullable=True)  # Current stage in workflow
    workflow_status = Column(String(50), nullable=True)  # Status within workflow
    
    # Priority and impact
    priority = Column(String(20), default='medium')  # low, medium, high, critical
    impact = Column(String(20), nullable=True)  # low, medium, high, critical
    
    # Evidence and documentation
    evidence_type = Column(String(100), nullable=True)  # 'document', 'signature', 'confirmation', 'external'
    evidence_notes = Column(Text, nullable=True)
    evidence_verified = Column(Boolean, default=False)
    evidence_verified_at = Column(DateTime, nullable=True)
    evidence_verified_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Document and evidence references
    document_ids = Column(ARRAY(String), nullable=True)  # List of document IDs
    external_references = Column(JSONB, nullable=True)  # External system references
    
    # Related items
    related_task_id = Column(String(36), ForeignKey('compliance_tasks.id'), nullable=True)
    related_audit_id = Column(String(36), ForeignKey('compliance_audits.id'), nullable=True)
    related_finding_id = Column(String(36), ForeignKey('compliance_findings.id'), nullable=True)
    
    # Dates and timing
    due_date = Column(Date, nullable=True, index=True)
    submitted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    
    # SLA tracking
    sla_days = Column(Integer, nullable=True)  # Expected days to resolve
    sla_breached = Column(Boolean, default=False)
    
    # Response time metrics
    first_response_at = Column(DateTime, nullable=True)
    time_to_first_response = Column(Integer, nullable=True)  # in minutes
    
    # Resolution metrics
    resolution_due_date = Column(Date, nullable=True)
    resolution_time = Column(Integer, nullable=True)  # in minutes
    
    # Audit and tracking
    submitted_by = Column(String(100), nullable=True)  # User ID or system identifier
    assigned_to = Column(String(100), nullable=True)  # User ID or role
    reviewer_notes = Column(Text, nullable=True)
    
    # Change tracking
    change_log = Column(JSONB, nullable=True)  # History of changes
    
    # System fields
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business_compliance: Mapped['BusinessCompliance'] = relationship(
        'BusinessCompliance', 
        back_populates='checkpoints'
    )
    
    # Related items (lazy loaded)
    related_task = relationship('ComplianceTask', foreign_keys=[related_task_id])
    related_audit = relationship('ComplianceAudit', foreign_keys=[related_audit_id])
    related_finding = relationship('ComplianceFinding', foreign_keys=[related_finding_id])
    
    # Methods
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'checkpoint_type': self.checkpoint_type,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'submitted_by': self.submitted_by,
            'assigned_to': self.assigned_to,
            'evidence_verified': self.evidence_verified,
            'document_ids': self.document_ids or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def add_note(self, note: str, user_id: str):
        """Add a note to the change log."""
        if not self.change_log:
            self.change_log = []
            
        self.change_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': 'note_added',
            'details': note
        })
    
    def update_status(self, new_status: str, user_id: str, notes: str = None):
        """Update status with audit trail."""
        old_status = self.status
        self.status = new_status
        
        if not self.change_log:
            self.change_log = []
            
        self.change_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': 'status_change',
            'old_status': old_status,
            'new_status': new_status,
            'notes': notes
        })
        
        # Update timestamps based on status
        if new_status == 'submitted' and not self.submitted_at:
            self.submitted_at = datetime.utcnow()
        elif new_status in ['completed', 'approved', 'rejected'] and not self.completed_at:
            self.completed_at = datetime.utcnow()
            
        # Calculate response time if this is the first response
        if new_status in ['in_review', 'in_progress'] and not self.first_response_at:
            self.first_response_at = datetime.utcnow()
            if self.created_at:
                self.time_to_first_response = int((self.first_response_at - self.created_at).total_seconds() / 60)
                
        # Calculate resolution time if completed
        if new_status in ['completed', 'approved', 'rejected'] and self.created_at and not self.resolution_time:
            self.resolution_time = int((datetime.utcnow() - self.created_at).total_seconds() / 60)
    
    # Relationships (updated with backref)
    business_compliance: Mapped['BusinessCompliance'] = relationship(
        'BusinessCompliance',
        back_populates='checkpoints'
    )
    
    def __repr__(self):
        return f"<ComplianceCheckpoint(id={self.id}, type='{self.checkpoint_type}', status='{self.status}')>"

# Update BusinessCompliance relationship to include checkpoints
BusinessCompliance.checkpoints = relationship(
    'ComplianceCheckpoint',
    back_populates='business_compliance',
    order_by='desc(ComplianceCheckpoint.created_at)',
    cascade='all, delete-orphan'
)

# Add this at the end of the file to ensure all models are defined first
def update_auto_fields(mapper, connection, target):
    """Automatically update calculated fields before flush."""
    if isinstance(target, BusinessCompliance):
        # Update days until due
        if target.next_due_date:
            target.days_until_due = (target.next_due_date - date.today()).days
            target.is_overdue = target.days_until_due < 0
        
        # Update compliance score if needed
        if target.status_changed_at is None or \
           (target.updated_at and target.status_changed_at < target.updated_at):
            target.compliance_score = target.calculate_compliance_score()
    
    elif isinstance(target, ComplianceRequirement):
        # Update risk score if severity changes
        if target.severity and not target.risk_score:
            target.risk_score = target.calculate_risk_score()
        
        # Update next check date if needed
        if target.monitoring_frequency and not target.next_check_due:
            target.next_check_due = target.get_next_check_date()

# Register event listeners
event.listen(BusinessCompliance, 'before_update', update_auto_fields)
event.listen(ComplianceRequirement, 'before_update', update_auto_fields)
