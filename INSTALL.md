# Installation Guide

## Quick Setup

### 1. Prerequisites
- Python 3.8+
- Node.js 16+ and npm
- Git

### 2. Clone and Setup
```bash
git clone <repository-url>
cd AI_UseCase
```

### 3. Backend Setup
```bash
# Create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your API keys
```

### 4. Frontend Setup (IMPORTANT)
```bash
# Option 1: Use setup script (recommended)
setup_frontend.bat    # Windows
# or
setup_frontend.ps1    # PowerShell

# Option 2: Manual install
cd frontend
npm install
cd ..
```

### 5. Run the Application

#### Full Stack (Recommended)
```bash
python start_all.py
```

#### Individual Components
```bash
# Streamlit Dashboard
python run.py

# FastAPI Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# React Frontend (separate terminal)
cd frontend
npm start
```

## Access Points
- Streamlit Dashboard: http://localhost:8501
- FastAPI API: http://localhost:8000
- React Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Troubleshooting

### "Cannot find module" Errors
**Solution:** Run `npm install` in the frontend directory
```bash
cd frontend
npm install
```

### Permission Issues (Windows)
**Solution:** Run PowerShell as Administrator or use the batch file
```cmd
setup_frontend.bat
```

### Module Not Found Errors
**Solution:** Ensure you're in the correct directory and dependencies are installed
```bash
# Check you're in the right place
pwd
# Should show: .../AI_UseCase/frontend

# Install dependencies
npm install

# Verify installation
ls node_modules  # Should show many folders
```

### Backend Connection Issues
**Solution:** Ensure FastAPI is running on port 8000
```bash
# Test backend
curl http://localhost:8000/health
```

## Development Mode

For hot-reload development:
```bash
# Terminal 1: Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm start

# Terminal 3: Regulatory Monitor (optional)
python -c "from services.regulatory_monitor import monitor_regulatory_updates; import asyncio; asyncio.run(monitor_regulatory_updates())"
```

## Docker Setup
```bash
docker-compose up -d
```

## Verification

After installation, verify everything works:
1. Backend: http://localhost:8000/health should return `{"status": "ok"}`
2. Streamlit: http://localhost:8501 should show the dashboard
3. React: http://localhost:3000 should show the login page

## Demo Credentials
- Email: admin@example.com
- Password: admin123
