"""Minimal Compliance API endpoints - placeholder implementation."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def get_compliance_status():
    """Get compliance system status."""
    return {"status": "active", "message": "Compliance module is running"}

# Note: Full compliance endpoints will be implemented later
# This is a minimal placeholder to allow the backend to start
