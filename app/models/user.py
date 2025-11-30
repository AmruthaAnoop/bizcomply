"""User model and related functionality.

This module defines the User model and related classes for authentication and authorization,
including roles, permissions, and token management.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer,
    String, Text, Enum as SQLAEnum, JSON, Table
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import get_password_hash, verify_password
from app.models.base import Base

# Association table for many-to-many relationship between User and Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String(36), ForeignKey('users.id'), primary_key=True),
    Column('role_id', String(36), ForeignKey('roles.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
)

class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending_verification"

class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User information
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    profile_image_url = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    status = Column(SQLAEnum(UserStatus), default=UserStatus.PENDING)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles: Mapped[List['Role']] = relationship(
        'Role', 
        secondary=user_roles,
        back_populates='users',
        lazy='selectin'
    )
    
    # Business relationship
    businesses: Mapped[List['Business']] = relationship(
        'Business', 
        back_populates='owner',
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    
    # Token relationship
    tokens: Mapped[List['Token']] = relationship(
        'Token', 
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    
    # Audit fields
    created_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    updated_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    
    # Creator/Updater relationships
    creator: Mapped['User'] = relationship(
        'User', 
        remote_side=[id], 
        foreign_keys=[created_by],
        post_update=True
    )
    
    def __init__(self, **kwargs):
        if 'password' in kwargs:
            self.set_password(kwargs.pop('password'))
        super().__init__(**kwargs)
    
    def set_password(self, password: str):
        """Set hashed password."""
        self.hashed_password = get_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password.
        
        Args:
            password: The plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return verify_password(password, self.hashed_password)
    
    @property
    def full_name(self) -> str:
        """Return the full name of the user."""
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.email
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.is_active and self.is_verified
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission.
        
        Args:
            permission: The permission string to check
            
        Returns:
            bool: True if user has the permission, False otherwise
        """
        if self.is_superuser:
            return True
        return any(
            permission in role.permissions
            for role in self.roles
            if role.permissions
        )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

# Pydantic models for API
class UserBase(BaseModel):
    """Base user model for API."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    """User creation model for API."""
    password: str = Field(..., min_length=8)
    
class UserUpdate(BaseModel):
    """User update model for API."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_image_url: Optional[str] = None
    
class UserInDBBase(UserBase):
    """Base user model for database."""
    id: str
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    
    class Config:
        from_attributes = True

class UserResponse(UserInDBBase):
    """Response model for user data (without sensitive information)."""
    full_name: Optional[str] = None
    
class UserInDB(UserInDBBase):
    """Database model for user with hashed password."""
    hashed_password: str

# Role and Permission models
class Role(Base):
    """Role model for role-based access control."""
    __tablename__ = "roles"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True)  # List of permission strings
    
    # Relationships
    users: Mapped[List[User]] = relationship(
        'User', 
        secondary=user_roles,
        back_populates='roles',
        lazy='selectin'
    )
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

class Token(Base):
    """Token model for API authentication.
    
    This model stores authentication tokens for API access, including access tokens,
    refresh tokens, and other token types like email verification and password reset.
    """
    __tablename__ = "tokens"
    
    id = Column(String(36), primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    token_type = Column(String(50), nullable=False)  # 'access', 'refresh', 'email_verification', 'password_reset'
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    user: Mapped[User] = relationship("User", back_populates="tokens")
    
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
    
    def revoke(self):
        """Revoke the token."""
        self.is_revoked = True
    
    def __repr__(self):
        return f"<Token(id={self.id}, type='{self.token_type}')>"
