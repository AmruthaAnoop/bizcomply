"""Minimal FastAPI application module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api_minimal import api_router

# Create FastAPI app
app = FastAPI(
    title="BizComply API",
    description="BizComply API for chat functionality",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS to allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "BizComply API is running"}

@app.get("/")
async def root():
    return {"message": "BizComply API is running", "docs": "/docs"}
