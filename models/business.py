"""Business-related database models."""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    ForeignKey, JSON, Enum as SQLAEnum, Text, Table, ForeignKeyConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from models.base import Base

class BusinessStructure(str, Enum):
    """Legal structure of the business."""
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    PARTNERSHIP = "partnership"
    LLC = "llc"
    CORPORATION = "corporation"
    NONPROFIT = "nonprofit"

class IndustryType(str, Enum):
    """Type of industry the business operates in."""
    RETAIL = "retail"
    FOOD_SERVICE = "food_service"
    CONSTRUCTION = "construction"
    CONSULTING = "consulting"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    TECHNOLOGY = "technology"
    OTHER = "other"

# Association table for many-to-many relationship between Business and BusinessOwner
business_owners = Table(
    'business_owners',
    Base.metadata,
    Column('business_id', String(36), ForeignKey('businesses.id'), primary_key=True),
    Column('owner_id', String(36), ForeignKey('business_owners_table.id'), primary_key=True),
    Column('ownership_percentage', Float, nullable=True),
    Column('is_primary', Boolean, default=False),
    Column('created_at', DateTime, default=datetime.utcnow),
)

class Business(Base):
    """Business entity model."""
    __tablename__ = 'businesses'

    id = Column(String(36), primary_key=True)
    legal_name = Column(String(255), nullable=False)
    dba_name = Column(String(255), nullable=True)
    structure = Column(SQLAEnum(BusinessStructure), nullable=False)
    industry = Column(SQLAEnum(IndustryType), nullable=False)
    ein = Column(String(20), unique=True, nullable=True)
    formation_date = Column(DateTime, nullable=True)
    employees_count = Column(Integer, default=0)
    annual_revenue = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    addresses: Mapped[List['BusinessAddress']] = relationship(
        'BusinessAddress', back_populates='business', cascade='all, delete-orphan'
    )
    owners: Mapped[List['BusinessOwner']] = relationship(
        'BusinessOwner',
        secondary=business_owners,
        back_populates='businesses',
        lazy='dynamic'
    )
    compliance_records: Mapped[List['BusinessCompliance']] = relationship(
        'BusinessCompliance', back_populates='business', cascade='all, delete-orphan'
    )
    documents: Mapped[List['GeneratedDocument']] = relationship(
        'GeneratedDocument', back_populates='business', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Business(id={self.id}, name='{self.legal_name}')>"

class BusinessAddress(Base):
    """Business address information."""
    __tablename__ = 'business_addresses'

    id = Column(String(36), primary_key=True)
    business_id = Column(String(36), ForeignKey('businesses.id'), nullable=False)
    address_type = Column(String(20), nullable=False)  # 'physical', 'mailing', 'registered_agent'
    street1 = Column(String(255), nullable=False)
    street2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False, default='United States')
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business: Mapped['Business'] = relationship('Business', back_populates='addresses')

    def __repr__(self):
        return f"<BusinessAddress(id={self.id}, type='{self.address_type}')>"

class BusinessOwner(Base):
    """Business owner or stakeholder information."""
    __tablename__ = 'business_owners_table'

    id = Column(String(36), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    ssn = Column(String(11), nullable=True)  # Encrypt in production
    date_of_birth = Column(DateTime, nullable=True)
    is_us_citizen = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    businesses: Mapped[List['Business']] = relationship(
        'Business',
        secondary=business_owners,
        back_populates='owners',
        lazy='dynamic'
    )
    addresses: Mapped[List['OwnerAddress']] = relationship(
        'OwnerAddress', back_populates='owner', cascade='all, delete-orphan'
    )

    @property
    def full_name(self) -> str:
        """Return the full name of the owner."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<BusinessOwner(id={self.id}, name='{self.full_name}')>"

class OwnerAddress(Base):
    """Owner's personal address information."""
    __tablename__ = 'owner_addresses'

    id = Column(String(36), primary_key=True)
    owner_id = Column(String(36), ForeignKey('business_owners_table.id'), nullable=False)
    address_type = Column(String(20), nullable=False)  # 'home', 'mailing', 'other'
    street1 = Column(String(255), nullable=False)
    street2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False, default='United States')
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner: Mapped['BusinessOwner'] = relationship('BusinessOwner', back_populates='addresses')

    def __repr__(self):
        return f"<OwnerAddress(id={self.id}, type='{self.address_type}')>"
