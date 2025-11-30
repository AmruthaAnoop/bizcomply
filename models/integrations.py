"""Integration and API key management models."""
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, 
    String, Text, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship

from .base import Base

class IntegrationType(str, Enum):
    """Types of third-party integrations."""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    WEBHOOK = "webhook"

class IntegrationStatus(str, Enum):
    """Status of an integration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class OAuth2Provider(str, Enum):
    """Supported OAuth2 providers."""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    SALESFORCE = "salesforce"
    CUSTOM = "custom"

class Integration(Base):
    """Model for third-party integrations."""
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    integration_type = Column(SQLEnum(IntegrationType), nullable=False)
    provider = Column(String(50), nullable=True)  # e.g., 'salesforce', 'servicenow'
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.INACTIVE)
    config = Column(JSON, default={})  # Provider-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="integration", cascade="all, delete-orphan")
    oauth2_configs = relationship("OAuth2Config", back_populates="integration", uselist=False, cascade="all, delete-orphan")

class OAuth2Config(Base):
    """OAuth2 configuration for integrations."""
    __tablename__ = "oauth2_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id", ondelete="CASCADE"), unique=True)
    client_id = Column(String(255), nullable=False)
    client_secret = Column(String(512), nullable=False)
    authorization_url = Column(String(512), nullable=False)
    token_url = Column(String(512), nullable=False)
    redirect_uri = Column(String(512), nullable=False)
    scope = Column(Text, default="")
    
    # Relationships
    integration = relationship("Integration", back_populates="oauth2_configs")

class APIKey(Base):
    """API key management for integrations."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    key = Column(String(255), unique=True, index=True, nullable=False)
    secret = Column(String(512), nullable=True)  # Hashed secret for API key authentication
    integration_id = Column(Integer, ForeignKey("integrations.id", ondelete="CASCADE"))
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    integration = relationship("Integration", back_populates="api_keys")

class DataImportExport(Base):
    """Model to track data import/export operations."""
    __tablename__ = "data_import_exports"
    
    class OperationType(str, Enum):
        IMPORT = "import"
        EXPORT = "export"
    
    class Status(str, Enum):
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"
    
    id = Column(Integer, primary_key=True, index=True)
    operation_type = Column(SQLEnum(OperationType), nullable=False)
    status = Column(SQLEnum(Status), default=Status.PENDING)
    format = Column(String(20))  # csv, json, xlsx, etc.
    file_path = Column(String(512), nullable=True)
    model_name = Column(String(100), nullable=True)  # Which model is being imported/exported
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="data_operations")
