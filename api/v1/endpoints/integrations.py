"""API endpoints for managing third-party integrations and data import/export."""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.core.security import has_scope
from app.models.integrations import (
    APIKey, DataImportExport, Integration, OAuth2Config,
    IntegrationType, OperationType, Status
)
from app.schemas.integrations import (
    APICreate, APIRegenerateKey, APIRegenerateSecret, APIReturn, 
    IntegrationCreate, IntegrationUpdate, IntegrationReturn, 
    OAuth2ConfigCreate, OAuth2ConfigUpdate, OAuth2ConfigReturn,
    DataImportExportCreate, DataImportExportReturn, DataImportExportStatus
)
from app.services.api_gateway import APIGatewayService, DataImportExportService

router = APIRouter()

# Integration Management
@router.post("/integrations/", response_model=IntegrationReturn, status_code=status.HTTP_201_CREATED)
def create_integration(
    *,
    db: Session = Depends(deps.get_db),
    integration_in: IntegrationCreate,
    current_user: dict = Depends(has_scope("integrations:write")),
) -> Any:
    """Create a new integration."""
    # Check if integration with this name already exists
    if db.query(Integration).filter(Integration.name == integration_in.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An integration with this name already exists",
        )
    
    # Create the integration
    integration = Integration(**integration_in.dict(exclude={"oauth2_config"}))
    db.add(integration)
    db.commit()
    db.refresh(integration)
    
    # If this is an OAuth2 integration, create the config
    if integration_in.integration_type == IntegrationType.OAUTH2 and integration_in.oauth2_config:
        oauth2_config = OAuth2Config(
            integration_id=integration.id,
            **integration_in.oauth2_config.dict()
        )
        db.add(oauth2_config)
        db.commit()
        db.refresh(oauth2_config)
        integration.oauth2_configs = [oauth2_config]
    
    return integration

@router.get("/integrations/", response_model=List[IntegrationReturn])
def list_integrations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(has_scope("integrations:read")),
) -> Any:
    """List all integrations."""
    return db.query(Integration).offset(skip).limit(limit).all()

@router.get("/integrations/{integration_id}", response_model=IntegrationReturn)
def get_integration(
    integration_id: int,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(has_scope("integrations:read")),
) -> Any:
    """Get a specific integration by ID."""
    integration = db.query(Integration).get(integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    return integration

# API Key Management
@router.post("/integrations/{integration_id}/api-keys", response_model=APIReturn)
def create_api_key(
    integration_id: int,
    *,
    db: Session = Depends(deps.get_db),
    api_key_in: APICreate,
    current_user: dict = Depends(has_scope("integrations:write")),
) -> Any:
    """Create a new API key for an integration."""
    integration = db.query(Integration).get(integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    
    # In a real implementation, you would generate a secure API key and hash it
    api_key = APIKey(
        name=api_key_in.name,
        key=f"api_key_{integration_id}_{api_key_in.name}",
        secret="hashed_secret_here",  # Hash this in a real implementation
        integration_id=integration_id,
        expires_at=api_key_in.expires_at,
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    # In a real implementation, you would only return the key and secret once
    return {
        **api_key.__dict__,
        "secret_plain": "only_show_this_once"  # Only show this once to the user
    }

# Data Import/Export
@router.post("/data/export", response_model=DataImportExportReturn)
async def export_data(
    *,
    db: Session = Depends(deps.get_db),
    export_in: DataImportExportCreate,
    current_user: dict = Depends(has_scope("data:export")),
) -> Any:
    """Export data in the specified format."""
    service = DataImportExportService(db)
    result = await service.export_data(
        model_name=export_in.model_name,
        format=export_in.format,
        filters=export_in.filters,
        user_id=current_user.id
    )
    
    # In a real implementation, you would return a file download
    return {
        "operation_id": "export_123",  # Replace with actual operation ID
        "status": "completed",
        "download_url": f"/api/v1/data/download/export_123"
    }

@router.post("/data/import", response_model=DataImportExportReturn)
async def import_data(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    model_name: str,
    current_user: dict = Depends(has_scope("data:import")),
) -> Any:
    """Import data from a file."""
    # In a real implementation, you would:
    # 1. Save the uploaded file to a temporary location
    # 2. Start an async task to process the import
    # 3. Return an operation ID to check the status
    
    service = DataImportExportService(db)
    result = await service.import_data(
        file_path=f"/tmp/{file.filename}",
        model_name=model_name,
        user_id=current_user.id
    )
    
    return {
        "operation_id": "import_123",  # Replace with actual operation ID
        "status": "processing",
        "details": result
    }

@router.get("/data/operations/{operation_id}", response_model=DataImportExportStatus)
def get_operation_status(
    operation_id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(has_scope("data:read")),
) -> Any:
    """Get the status of an import/export operation."""
    service = DataImportExportService(db)
    return service.get_import_export_status(operation_id)

# API Gateway
@router.post("/integrations/{integration_id}/proxy/{path:path}")
async def proxy_request(
    integration_id: int,
    path: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(has_scope("integrations:execute")),
) -> Any:
    """Proxy a request to a third-party API through the API Gateway."""
    service = APIGatewayService(db)
    return await service.make_request(
        integration_id=integration_id,
        endpoint=f"https://api.example.com/{path}",  # Replace with actual base URL from config
        method=method,
        data=data,
        params=params,
        headers=headers
    )
