"""API router configuration."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    # compliance,  # Disabled due to missing dependencies
    documents,
    integrations,  # Import the new integrations module
    # regulatory,  # Disabled due to missing dependencies
    chat  # new chat endpoint
)

api_router = APIRouter()

# Include all API routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(compliance.router, prefix="/compliance", tags=["Compliance"])  # Disabled
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])

# Include the new integrations router
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])

# Include chat endpoint
api_router.include_router(chat.router, prefix="/chatbot", tags=["Chat"])
# api_router.include_router(regulatory.router, prefix="/regulatory", tags=["Regulatory"])  # Disabled
