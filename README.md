# BizComply AI - Business Compliance & Regulatory Monitoring Platform

## Overview

BizComply AI is a comprehensive AI-powered compliance management platform that helps businesses stay up-to-date with regulatory requirements, monitor compliance status, and manage regulatory updates through intelligent conversational AI.

## 🌟 Key Features

### 🤖 AI Compliance Chatbot (NEW)
- **RAG Integration**: Document-based compliance answers using vector embeddings
- **Live Web Search**: Real-time regulatory updates and current information
- **Adaptive Response Modes**: Concise, Simple, and Detailed response styles
- **Business Profile Intelligence**: Personalized compliance guidance based on business type, industry, and location
- **Conversational Interface**: Natural language processing for intuitive compliance guidance

### 🔍 Regulatory Monitoring
- Automated monitoring of regulatory feeds (SEC, Federal Register, EU Official Journal)
- Impact analysis and relevance scoring
- Real-time updates and notifications
- Customizable filtering and search

### 📊 Compliance Dashboard
- Overview of compliance status
- Key metrics and KPIs
- Visual analytics and charts
- Risk assessment tools

### 📋 Compliance Management
- Compliance checklists
- Task tracking and management
- Deadline reminders
- Document management

### 📈 Reports & Analytics
- Generate compliance reports
- Export data in various formats
- Trend analysis
- Audit trails

## Quick Start

### 🚀 Launch AI Chatbot (Primary Interface)

```bash
streamlit run app.py
```

This will start the AI Compliance Chatbot at `http://localhost:8501` with:
- 🤖 Conversational AI assistant
- 📚 RAG-powered document search
- 🌐 Live web search integration
- 🎛️ Adaptive response modes
- 🏢 Business profile management

### 🛠️ Complete Setup (Windows)

```bash
setup_complete.bat
```
This script will:
- Check Python and Node.js installation
- Create Python virtual environment
- Install all dependencies
- Set up environment files


### Development Setup

For development with hot reload:

```bash
# Terminal 1: Start FastAPI backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start React frontend
cd frontend
npm start

# Terminal 3: Start regulatory monitor (optional)
python -c "from services.regulatory_monitor import monitor_regulatory_updates; import asyncio; asyncio.run(monitor_regulatory_updates())"
```

## Usage

### Dashboard
- View overall compliance status
- Monitor regulatory updates
- Access key metrics and analytics

### Regulatory Updates
- Browse latest regulatory changes
- Filter by source, category, or relevance
- Mark updates as read/unread
- View detailed impact analysis

### Compliance Management
- Track compliance tasks
- Manage deadlines
- Risk assessment
- Document compliance evidence

### AI Assistant
- Ask compliance questions
- Get guidance on regulations
- Search for specific requirements
- Generate compliance reports

## API Reference

The platform also provides REST API endpoints for integration:

- `GET /api/v1/regulatory/updates` - Get regulatory updates
- `POST /api/v1/regulatory/updates/process` - Process updates
- `GET /api/v1/regulatory/updates/{id}/impact` - Analyze impact

## Access Points

- **Streamlit Dashboard**:https://amruthaanoop-bizcomply-app-clean-rjeerz.streamlit.app/
- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **React Frontend**: http://localhost:3000

## Demo Credentials

- Email: `admin@example.com`
- Password: `admin123`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
