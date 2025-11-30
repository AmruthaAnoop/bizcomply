"""
Regulatory API Schemas

This module defines Pydantic models for the regulatory API endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

class RegulatoryUpdateStatus(str, Enum):
    """Status of a regulatory update."""
    PENDING = "pending"
    PROCESSED = "processed"
    IGNORED = "ignored"

class RegulatoryImpactLevel(str, Enum):
    """Impact level of a regulatory update."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class RegulatoryUpdateResponse(BaseModel):
    """Response model for a regulatory update."""
    id: str = Field(..., description="Unique identifier for the update")
    title: str = Field(..., description="Title of the regulatory update")
    summary: str = Field(..., description="Summary of the update")
    link: HttpUrl = Field(..., description="URL to the full update")
    published: datetime = Field(..., description="Publication date of the update")
    source: str = Field(..., description="Source of the update")
    categories: List[str] = Field(default_factory=list, description="Categories of the update")
    status: RegulatoryUpdateStatus = Field(..., description="Processing status of the update")
    impact_level: RegulatoryImpactLevel = Field(..., description="Impact level of the update")
    created_at: datetime = Field(..., description="When the update was first recorded")
    updated_at: datetime = Field(..., description="When the update was last updated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        schema_extra = {
            "example": {
                "id": "update-123",
                "title": "New Tax Regulation 2023",
                "summary": "New tax regulations affecting all businesses...",
                "link": "https://example.com/regulations/tax-2023",
                "published": "2023-01-15T00:00:00Z",
                "source": "IRS",
                "categories": ["tax", "financial"],
                "status": "pending",
                "impact_level": "high",
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T10:30:00Z",
                "metadata": {
                    "jurisdiction": "US",
                    "effective_date": "2023-07-01"
                }
            }
        }

class ComplianceRequirementImpact(BaseModel):
    """Impact of a regulatory update on a compliance requirement."""
    requirement_id: str = Field(..., description="ID of the affected requirement")
    name: str = Field(..., description="Name of the requirement")
    is_new: bool = Field(..., description="Whether this is a new requirement")
    requires_update: bool = Field(..., description="Whether an existing requirement needs updating")
    impact_description: str = Field(..., description="Description of the impact")
    action_required: bool = Field(..., description="Whether action is required")
    deadline: Optional[datetime] = Field(None, description="Deadline for compliance, if applicable")

class ComplianceImpactResponse(BaseModel):
    """Response model for compliance impact analysis."""
    update_id: str = Field(..., description="ID of the regulatory update")
    impacted_requirements: List[ComplianceRequirementImpact] = Field(
        default_factory=list, 
        description="List of impacted compliance requirements"
    )
    total_impacted: int = Field(..., description="Total number of impacted requirements")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        schema_extra = {
            "example": {
                "update_id": "update-123",
                "impacted_requirements": [
                    {
                        "requirement_id": "req-456",
                        "name": "Annual Tax Filing",
                        "is_new": False,
                        "requires_update": True,
                        "impact_description": "Deadline extended to July 31",
                        "action_required": True,
                        "deadline": "2023-07-31T23:59:59Z"
                    }
                ],
                "total_impacted": 1
            }
        }

class ProcessUpdatesResponse(BaseModel):
    """Response model for update processing requests."""
    status: str = Field(..., description="Status of the processing request")
    message: str = Field(..., description="Status message")
    update_id: Optional[str] = Field(None, description="ID of the update being processed, if applicable")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "processing",
                "message": "Processing of update update-123 has been queued",
                "update_id": "update-123"
            }
        }

class UpcomingRequirement(BaseModel):
    """Model for upcoming compliance requirements."""
    update_id: str = Field(..., description="ID of the regulatory update")
    update_title: str = Field(..., description="Title of the regulatory update")
    update_date: datetime = Field(..., description="Date of the regulatory update")
    requirement_id: str = Field(..., description="ID of the compliance requirement")
    requirement_name: str = Field(..., description="Name of the compliance requirement")
    action_required: bool = Field(..., description="Whether action is required")
    deadline: Optional[datetime] = Field(None, description="Deadline for compliance")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class RegulatoryUpdateSearch(BaseModel):
    """Search criteria for regulatory updates."""
    status: Optional[RegulatoryUpdateStatus] = None
    impact_level: Optional[RegulatoryImpactLevel] = None
    category: Optional[str] = None
    source: Optional[str] = None
    published_after: Optional[datetime] = None
    published_before: Optional[datetime] = None
    limit: int = 100
    skip: int = 0
