"""Minimal API router configuration - only includes chat endpoint."""
from fastapi import APIRouter

from app.api.v1.endpoints import chat

api_router = APIRouter()

# Include only the chat endpoint for now
api_router.include_router(chat.router, prefix="/chatbot", tags=["Chat"])
