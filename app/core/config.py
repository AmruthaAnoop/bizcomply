"""Application configuration settings.

This module defines the application configuration using environment variables with sensible defaults.
It uses Pydantic's BaseSettings for validation and type conversion.
"""
import os
import secrets
from pathlib import Path
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "BizComply API"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    SERVER_NAME: str = os.getenv("SERVER_NAME", "BizComply")
    SERVER_HOST: str = os.getenv("SERVER_HOST", "http://localhost:8000")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # Local development
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{Path(__file__).parent.parent.parent}/data/bizcomply.db"
    )
    
    # Security
    SECURITY_PASSWORD_SALT: str = os.getenv("SECURITY_PASSWORD_SALT", "supersecretsalt")
    
    # First superuser
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER", "admin@bizcomply.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "changeme")
    
    # File storage
    UPLOAD_DIR: str = os.path.join(
        Path(__file__).parent.parent.parent, "uploads"
    )
    STATIC_DIR: str = os.path.join(
        Path(__file__).parent.parent.parent, "static"
    )
    
    # Ensure upload and static directories exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Email (SMTP)
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() in ("true", "1", "t")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[EmailStr] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = os.getenv("EMAILS_FROM_NAME", PROJECT_NAME)
    
    # Security Headers
    SECURE_COOKIES: bool = os.getenv("SECURE_COOKIES", "True").lower() in ("true", "1", "t")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create settings instance
settings = Settings()
