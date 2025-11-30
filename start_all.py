import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def initialize_database():
    """Initialize the database with all required tables"""
    try:
        print("Initializing database...")
        subprocess.run([sys.executable, "init_database.py"], check=True)
        print("✅ Database initialized successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    except FileNotFoundError:
        print("⚠️ Database initialization script not found, continuing...")
    return True

def start_fastapi_backend():
    """Start the FastAPI backend"""
    try:
        print("Starting FastAPI backend...")
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except Exception as e:
        print(f"Error starting FastAPI backend: {e}")

def start_streamlit_app():
    """Start the Streamlit application"""
    try:
        print("Starting Streamlit application...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=false"
        ])
    except Exception as e:
        print(f"Error starting Streamlit app: {e}")

def start_regulatory_monitor():
    """Start the regulatory monitoring service"""
    try:
        from services.regulatory_monitor import monitor_regulatory_updates
        import asyncio
        
        print("Starting regulatory monitoring service...")
        asyncio.run(monitor_regulatory_updates(interval_minutes=60))
    except Exception as e:
        print(f"Error starting regulatory monitor: {e}")

def main():
    """Main entry point"""
    print("🚀 Starting BizComply Platform...")
    print("=" * 50)
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Ensure logs directory exists
    logs_dir = Path("logs")
    # Initialize database first
    if not initialize_database():
        print("❌ Failed to initialize database, exiting...")
        return
    
    logs_dir.mkdir(exist_ok=True)
    
    # Start regulatory monitor in background
    monitor_thread = threading.Thread(target=start_regulatory_monitor, daemon=True)
    monitor_thread.start()
    
    # Give monitor a moment to start
    time.sleep(2)
    
    # Start FastAPI backend in background
    backend_thread = threading.Thread(target=start_fastapi_backend, daemon=True)
    backend_thread.start()
    
    # Give backend a moment to start
    time.sleep(3)
    
    # Start Streamlit app (this will be the main process)
    start_streamlit_app()

if __name__ == "__main__":
    main()
