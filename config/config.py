# config/config.py
import os
from pathlib import Path
from enum import Enum

# Enum definitions
class BusinessType(Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    OTHER = "other"

class Jurisdiction(Enum):
    US = "us"
    EU = "eu"
    UK = "uk"
    GLOBAL = "global"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING = "pending"
    EXEMPT = "exempt"

# Project settings
PROJECT_NAME = "BizComply"
PROJECT_VERSION = "1.0.0"

# Default values
DEFAULT_BUSINESS_TYPE = BusinessType.TECHNOLOGY
DEFAULT_JURISDICTION = Jurisdiction.US

# Database settings
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "compliance.db")

# Regulatory monitoring settings
REGULATORY_FEEDS = [
    {
        "name": "SEC Filings",
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=&company=&dateb=&owner=include&start=0&count=100&output=atom",
        "category": "financial",
        "enabled": True
    },
    {
        "name": "Federal Register",
        "url": "https://www.federalregister.gov/api/v1/documents.rss?conditions[agencies][]=securities-and-exchange-commission",
        "category": "regulatory",
        "enabled": True
    },
    {
        "name": "EU Official Journal",
        "url": "https://eur-lex.europa.eu/rss/latest.xml",
        "category": "eu_regulation",
        "enabled": True
    }
]
REGULATORY_UPDATE_FREQUENCY = 60  # minutes

# LLM settings
LLM_PROVIDER = "groq"
LLM_MODEL = "llama-3.1-8b-instant"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# RAG settings
RAG_ENABLED = True
VECTOR_STORE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vector_store")
DOCUMENTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "documents")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Web search settings
WEB_SEARCH_ENABLED = False
WEB_SEARCH_API_KEY = os.getenv("WEB_SEARCH_API_KEY")
WEB_SEARCH_ENGINE = "google"
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
MAX_WEB_RESULTS = 5

# UI settings
UI_TITLE = "BizComply Portal"
UI_DESCRIPTION = "Business Compliance & Regulatory Monitoring Platform"
UI_AVATAR = ""

# Response modes for chatbot
RESPONSE_MODES = ["simple", "detailed", "comprehensive"]
DEFAULT_RESPONSE_MODE = "simple"

# Notification settings
EMAIL_ENABLED = True
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "app.log")