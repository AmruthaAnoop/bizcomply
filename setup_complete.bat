@echo off
title BizComply Complete Setup

echo ========================================
echo    BizComply Platform Setup
echo ========================================
echo.

:: Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)
python --version
echo ✅ Python found
echo.

:: Check Node.js
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 16+ first.
    pause
    exit /b 1
)
node --version
npm --version
echo ✅ Node.js and npm found
echo.

:: Setup Python virtual environment
echo [3/6] Setting up Python environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
)
call venv\Scripts\activate
echo ✅ Virtual environment activated
echo.

:: Install Python dependencies
echo [4/6] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✅ Python dependencies installed
echo.

:: Setup frontend
echo [5/6] Setting up frontend dependencies...
cd frontend
npm install
if errorlevel 1 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..
echo ✅ Frontend dependencies installed
echo.

:: Setup environment files
echo [6/6] Setting up environment files...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ .env file created from .env.example
        echo ⚠️  Please edit .env with your API keys
    ) else (
        echo ⚠️  No .env.example found, creating basic .env
        echo OPENAI_API_KEY=your_openai_api_key > .env
        echo WEB_SEARCH_API_KEY=your_web_search_api_key >> .env
        echo SECRET_KEY=your_secret_key_here >> .env
    )
) else (
    echo ✅ .env file already exists
)

if not exist "frontend\.env" (
    echo REACT_APP_API_URL=http://localhost:8000/api/v1 > frontend\.env
    echo REACT_APP_WS_URL=ws://localhost:8000/ws >> frontend\.env
    echo ✅ Frontend .env created
) else (
    echo ✅ Frontend .env already exists
)

:: Create data directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "documents" mkdir documents
echo ✅ Data directories created
echo.

echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo 🎉 BizComply platform is ready to use!
echo.
echo 📁 What was created:
echo    - venv\ (Python virtual environment)
echo    - frontend\node_modules\ (Node.js dependencies)
echo    - .env (Environment configuration)
echo    - data\, logs\, documents\ (Data directories)
echo.
echo 🚀 How to run:
echo    python start_all.py    # Full stack (recommended)
echo    python run.py          # Streamlit only
echo    python verify_installation.py    # Verify installation
echo.
echo 📖 See INSTALL.md for detailed instructions
echo.
echo ⚠️  Don't forget to:
echo    1. Edit .env with your API keys
echo    2. Edit frontend\.env if needed
echo.
pause
