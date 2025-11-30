"""Main FastAPI application module."""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.api.v1.api_minimal import api_router
# from app.core.config import settings
# from app.core.security import get_current_active_user
# from app.models.user import User

# Create FastAPI app
app = FastAPI(
    title="BizComply API",
    description="BizComply API for chat functionality",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=settings.STATIC_DIR),
    name="static"
)

# Include API routes
app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
    dependencies=[Depends(get_current_active_user)],
)

# Custom docs route that requires authentication
@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(
    current_user: User = Depends(get_current_active_user)
):
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
    )

# Custom OpenAPI schema
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

# Health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok", "version": settings.VERSION}

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Welcome to BizComply API",
        "version": settings.VERSION,
        "docs": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
