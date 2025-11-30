"""Pydantic models for integration-related schemas."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, validator

from app.models.integrations import IntegrationType, OperationType, Status

# Shared properties
class IntegrationBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    integration_type: IntegrationType
    provider: Optional[str] = Field(None, max_length=50)
    config: Optional[Dict[str, Any]] = {}

# Properties to receive via API on creation
class IntegrationCreate(IntegrationBase):
    oauth2_config: Optional['OAuth2ConfigCreate'] = None

# Properties to receive via API on update
class IntegrationUpdate(IntegrationBase):
    name: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None

# Properties shared by models stored in DB
class IntegrationInDBBase(IntegrationBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Additional properties to return via API
class IntegrationReturn(IntegrationInDBBase):
    oauth2_config: Optional['OAuth2ConfigReturn'] = None
    api_keys: List['APIReturn'] = []

# OAuth2 Configuration
class OAuth2ConfigBase(BaseModel):
    client_id: str = Field(..., max_length=255)
    client_secret: str = Field(..., max_length=512)
    authorization_url: str = Field(..., max_length=512)
    token_url: str = Field(..., max_length=512)
    redirect_uri: str = Field(..., max_length=512)
    scope: str = ""

class OAuth2ConfigCreate(OAuth2ConfigBase):
    pass

class OAuth2ConfigUpdate(OAuth2ConfigBase):
    client_id: Optional[str] = Field(None, max_length=255)
    client_secret: Optional[str] = Field(None, max_length=512)
    authorization_url: Optional[str] = Field(None, max_length=512)
    token_url: Optional[str] = Field(None, max_length=512)
    redirect_uri: Optional[str] = Field(None, max_length=512)

class OAuth2ConfigInDBBase(OAuth2ConfigBase):
    id: int
    integration_id: int

    class Config:
        orm_mode = True

class OAuth2ConfigReturn(OAuth2ConfigInDBBase):
    pass

# API Key Management
class APIBase(BaseModel):
    name: str = Field(..., max_length=100)
    expires_at: Optional[datetime] = None

class APICreate(APIBase):
    pass

class APIRegenerateKey(BaseModel):
    name: str = Field(..., max_length=100)

class APIRegenerateSecret(BaseModel):
    current_secret: str

class APIInDBBase(APIBase):
    id: int
    key: str
    integration_id: int
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class APIReturn(APIInDBBase):
    pass

# Data Import/Export
class DataImportExportBase(BaseModel):
    operation_type: OperationType
    format: str
    model_name: str
    options: Optional[Dict[str, Any]] = {}

class DataImportExportCreate(DataImportExportBase):
    filters: Optional[Dict[str, Any]] = {}

class DataImportExportInDBBase(DataImportExportBase):
    id: int
    status: Status
    file_path: Optional[str] = None
    created_by: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        orm_mode = True

class DataImportExportReturn(DataImportExportInDBBase):
    download_url: Optional[str] = None

class DataImportExportStatus(BaseModel):
    id: int
    status: str
    progress: int
    details: Dict[str, Any]
    download_url: Optional[str] = None

    class Config:
        orm_mode = True

# Update forward refs
IntegrationCreate.update_forward_refs()
IntegrationReturn.update_forward_refs()
OAuth2ConfigReturn.update_forward_refs()
APIReturn.update_forward_refs()
DataImportExportReturn.update_forward_refs()
