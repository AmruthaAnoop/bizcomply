"""Document-related database models."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    Column, String, Integer, Text, DateTime, 
    ForeignKey, Boolean, JSON, Enum as SQLAEnum, LargeBinary
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from models.base import Base

class DocumentFormat(str, Enum):
    """Supported document formats."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    HTML = "html"
    TXT = "txt"
    CSV = "csv"

class DocumentStatus(str, Enum):
    """Status of a document in the system."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class DocumentTemplate(Base):
    """Template for generating documents."""
    __tablename__ = 'document_templates'

    id = Column(String(36), primary_key=True)
    
    # Identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), nullable=False, default="1.0")
    
    # Content
    template_type = Column(String(50), nullable=False)  # e.g., 'form', 'report', 'letter'
    format = Column(SQLAEnum(DocumentFormat), nullable=False)
    content = Column(LargeBinary, nullable=True)  # Binary content of the template
    content_url = Column(String(500), nullable=True)  # URL to template file if stored externally
    
    # Fields definition
    fields_schema = Column(JSON, nullable=True)  # JSON Schema for template fields
    sample_data = Column(JSON, nullable=True)  # Sample data for preview
    
    # Metadata
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags for filtering
    
    # Applicability
    jurisdiction = Column(String(100), nullable=True)  # 'federal', 'state:CA', etc.
    business_structures = Column(JSON, nullable=True)  # List of BusinessStructure enums
    industry_types = Column(JSON, nullable=True)  # List of IndustryType enums
    
    # System fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    generated_documents: Mapped[List['GeneratedDocument']] = relationship(
        'GeneratedDocument', back_populates='template'
    )
    
    def __repr__(self):
        return f"<DocumentTemplate(id={self.id}, name='{self.name}', version='{self.version}')>"

class GeneratedDocument(Base):
    """Instance of a generated document for a specific business."""
    __tablename__ = 'generated_documents'
    
    id = Column(String(36), primary_key=True)
    template_id = Column(String(36), ForeignKey('document_templates.id'), nullable=False)
    business_id = Column(String(36), ForeignKey('businesses.id'), nullable=False)
    compliance_id = Column(String(36), ForeignKey('business_compliances.id'), nullable=True)
    
    # Document details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLAEnum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False)
    
    # Content
    format = Column(SQLAEnum(DocumentFormat), nullable=False)
    content = Column(LargeBinary, nullable=True)  # Binary content of the generated document
    content_url = Column(String(500), nullable=True)  # URL to generated document if stored externally
    
    # Data used for generation
    data = Column(JSON, nullable=True)  # Data used to populate the template
    
    # Metadata
    metadata_ = Column('metadata', JSON, nullable=True)  # Additional metadata
    tags = Column(JSON, nullable=True)  # List of tags for organization
    
    # Audit fields
    generated_by = Column(String(100), nullable=True)  # User ID or system identifier
    generated_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # System fields
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template: Mapped['DocumentTemplate'] = relationship('DocumentTemplate', back_populates='generated_documents')
    business: Mapped['Business'] = relationship('Business', back_populates='documents')
    compliance_record: Mapped['BusinessCompliance'] = relationship('BusinessCompliance', back_populates='documents')
    
    def __repr__(self):
        return f"<GeneratedDocument(id={self.id}, name='{self.name}', status='{self.status}')>"

class DocumentSignature(Base):
    """Electronic signatures for documents."""
    __tablename__ = 'document_signatures'
    
    id = Column(String(36), primary_key=True)
    document_id = Column(String(36), ForeignKey('generated_documents.id'), nullable=False)
    
    # Signature details
    signer_name = Column(String(255), nullable=False)
    signer_email = Column(String(255), nullable=False)
    signer_role = Column(String(100), nullable=True)
    
    # Signature data
    signature_data = Column(JSON, nullable=True)  # Digital signature data
    signature_image = Column(LargeBinary, nullable=True)  # Image of signature if applicable
    
    # Timestamps
    sent_at = Column(DateTime, nullable=True)
    viewed_at = Column(DateTime, nullable=True)
    signed_at = Column(DateTime, nullable=True)
    
    # Verification
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    verification_token = Column(String(100), nullable=True)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document: Mapped['GeneratedDocument'] = relationship('GeneratedDocument')
    
    def __repr__(self):
        return f"<DocumentSignature(id={self.id}, signer='{self.signer_name}')>"

class DocumentFolder(Base):
    """Organization of documents into folders."""
    __tablename__ = 'document_folders'
    
    id = Column(String(36), primary_key=True)
    parent_id = Column(String(36), ForeignKey('document_folders.id'), nullable=True)
    business_id = Column(String(36), ForeignKey('businesses.id'), nullable=False)
    
    # Folder details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Access control
    is_shared = Column(Boolean, default=False)
    shared_settings = Column(JSON, nullable=True)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business: Mapped['Business'] = relationship('Business')
    parent: Mapped['DocumentFolder'] = relationship('DocumentFolder', remote_side=[id])
    
    def __repr__(self):
        return f"<DocumentFolder(id={self.id}, name='{self.name}')>"

class DocumentFolderItem(Base):
    """Association between documents and folders."""
    __tablename__ = 'document_folder_items'
    
    id = Column(String(36), primary_key=True)
    folder_id = Column(String(36), ForeignKey('document_folders.id'), nullable=False)
    document_id = Column(String(36), ForeignKey('generated_documents.id'), nullable=False)
    
    # Ordering
    sort_order = Column(Integer, default=0)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    folder: Mapped['DocumentFolder'] = relationship('DocumentFolder')
    document: Mapped['GeneratedDocument'] = relationship('GeneratedDocument')
    
    def __repr__(self):
        return f"<DocumentFolderItem(folder_id={self.folder_id}, document_id={self.document_id})>"
