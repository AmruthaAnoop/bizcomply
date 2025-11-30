"""Minimal Regulatory API endpoints - placeholder implementation."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def get_regulatory_status():
    """Get regulatory monitoring status."""
    return {"status": "active", "message": "Regulatory module is running"}

# Note: Full regulatory endpoints will be implemented later
# This is a minimal placeholder to allow the backend to start
