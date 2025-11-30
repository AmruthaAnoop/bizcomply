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
streamlit run app_clean.py
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

### 📦 Manual Installation

```bash
# Clone the repository
git clone https://github.com/AmruthaAnoop/bizcomply.git
cd bizcomply

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the AI chatbot
streamlit run app_clean.py
```
- Create necessary directories

### 📋 Manual Setup

#### Prerequisites
- Python 3.8 or higher
- Node.js 16+ and npm
- pip package manager

#### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd bizcomply
```

2. **Set up Python environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up frontend dependencies:**
```bash
# Option 1: Run the setup script
setup_frontend.bat  # Windows
# or
setup_frontend.ps1  # PowerShell

# Option 2: Install manually
cd frontend
npm install
cd ..
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Verify installation:**
```bash
python verify_installation.py
```

6. **Run the application:**
```bash
# Option 1: Full stack (FastAPI + Streamlit + Regulatory Monitor)
python start_all.py

# Option 2: Streamlit only with regulatory monitor
python run.py

# Option 3: FastAPI only
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 4: Frontend only
cd frontend
npm start
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI API (for AI assistant)
OPENAI_API_KEY=your_openai_api_key

# Web Search API
WEB_SEARCH_API_KEY=your_web_search_api_key

# Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Security
SECRET_KEY=your_secret_key_here
```

### Frontend Environment Variables

Create `frontend/.env` for frontend configuration:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## Troubleshooting

### Common Issues

1. **TypeScript/Module Resolution Errors:**
   - Make sure to run `npm install` in the frontend directory
   - If you see "Cannot find module '@mui/material'" errors, the dependencies aren't installed
   - Run the setup script or manually install dependencies

2. **Import Errors:**
   - Ensure all dependencies are installed with `npm install`
   - Check that `node_modules` folder exists in the frontend directory

3. **Backend Connection Issues:**
   - Make sure the FastAPI backend is running on port 8000
   - Check the API_URL environment variable in frontend/.env

4. **Regulatory Monitor Issues:**
   - Ensure the data directory exists and is writable
   - Check the database path in config.py

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

- **Streamlit Dashboard**: http://localhost:8501
- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **React Frontend**: http://localhost:3000

## Demo Credentials

- Email: `admin@example.com`
- Password: `admin123`

## Support

For support and questions:
- Documentation: [Link to docs]
- Issues: [Link to GitHub Issues]
- Email: support@bizcomply.com

## License

This project is licensed under the MIT License - see the LICENSE file for details.
