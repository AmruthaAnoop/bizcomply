"""API Gateway service for managing third-party integrations and routing requests."""
import json
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import has_scope
from app.models.integrations import APIKey, Integration, OAuth2Config

class APIGatewayService:
    """Service for managing API Gateway functionality."""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def make_request(
        self, 
        integration_id: int, 
        endpoint: str, 
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to a third-party API."""
        integration = self.db.query(Integration).get(integration_id)
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration with ID {integration_id} not found"
            )
            
        if integration.integration_type == "oauth2":
            return await self._make_oauth2_request(integration, endpoint, method, data, params, headers)
        else:
            return await self._make_api_key_request(integration, endpoint, method, data, params, headers)
    
    async def _make_oauth2_request(
        self,
        integration: Integration,
        endpoint: str,
        method: str,
        data: Optional[Dict[str, Any]],
        params: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Make a request using OAuth2 authentication."""
        # In a real implementation, you would:
        # 1. Get the access token from the token store
        # 2. Check if it's expired and refresh if needed
        # 3. Make the request with the token
        
        # This is a simplified example
        oauth_config = integration.oauth2_configs[0] if integration.oauth2_configs else None
        if not oauth_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth2 configuration not found for this integration"
            )
            
        # In a real implementation, get the actual access token from the token store
        access_token = "your_access_token_here"
        
        request_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            **(headers or {})
        }
        
        return await self._execute_request(
            url=endpoint,
            method=method,
            headers=request_headers,
            json=data,
            params=params
        )
    
    async def _make_api_key_request(
        self,
        integration: Integration,
        endpoint: str,
        method: str,
        data: Optional[Dict[str, Any]],
        params: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Make a request using API key authentication."""
        api_key = self.db.query(APIKey).filter(
            APIKey.integration_id == integration.id,
            APIKey.is_active == True
        ).first()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active API key found for this integration"
            )
            
        request_headers = {
            "X-API-Key": api_key.key,
            "Content-Type": "application/json",
            **(headers or {})
        }
        
        return await self._execute_request(
            url=endpoint,
            method=method,
            headers=request_headers,
            json=data,
            params=params
        )
    
    @staticmethod
    async def _execute_request(
        url: str,
        method: str,
        headers: Dict[str, str],
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the HTTP request using httpx."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                try:
                    error_detail = e.response.json()
                except json.JSONDecodeError:
                    error_detail = e.response.text
                
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=error_detail or "Error making request to external service"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Error connecting to external service: {str(e)}"
                )

class DataImportExportService:
    """Service for handling data import/export operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def export_data(
        self, 
        model_name: str, 
        format: str = "json",
        filters: Optional[Dict[str, Any]] = None,
        user_id: int = None
    ) -> str:
        """Export data from the specified model."""
        # This is a simplified example - in a real implementation, you would:
        # 1. Validate the model name and format
        # 2. Apply filters to the query
        # 3. Convert the data to the requested format
        # 4. Save the file to a storage service
        # 5. Return the file path or a download URL
        
        # For now, we'll just return a success message
        return f"Exported {model_name} data to {format} format"
    
    async def import_data(
        self, 
        file_path: str, 
        model_name: str,
        user_id: int = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Import data into the specified model."""
        # This is a simplified example - in a real implementation, you would:
        # 1. Read the file from the specified path
        # 2. Validate the data structure
        # 3. Import the data into the database
        # 4. Return a summary of the import operation
        
        # For now, we'll just return a success message
        return {
            "status": "completed",
            "imported_count": 0,  # Replace with actual count
            "errors": []
        }
    
    def get_import_export_status(self, operation_id: int) -> Dict[str, Any]:
        """Get the status of an import/export operation."""
        # In a real implementation, you would query the database for the operation status
        return {
            "id": operation_id,
            "status": "completed",
            "progress": 100,
            "details": {}
        }
