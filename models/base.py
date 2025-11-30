"""Base database models and session management."""
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from config.config import DB_PATH

# Ensure the database directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Create SQLite engine with connection pooling
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True  # Set to False in production
)

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Base class for all models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initialize the database with all models."""
    # Import models here to avoid circular imports
    from models.business import Business, BusinessOwner, BusinessAddress  # noqa: F401
    from models.compliance import ComplianceRequirement, BusinessCompliance  # noqa: F401
    from models.documents import DocumentTemplate, GeneratedDocument  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
