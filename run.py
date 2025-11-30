import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def start_regulatory_monitor():
    """Start the regulatory monitoring service in the background"""
    try:
        from services.regulatory_monitor import monitor_regulatory_updates
        import asyncio
        
        print("Starting regulatory monitoring service...")
        asyncio.run(monitor_regulatory_updates(interval_minutes=60))
    except Exception as e:
        print(f"Error starting regulatory monitor: {e}")

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

def main():
    """Main entry point"""
    print("🚀 Starting BizComply Portal...")
    print("=" * 50)
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Start regulatory monitor in background
    monitor_thread = threading.Thread(target=start_regulatory_monitor, daemon=True)
    monitor_thread.start()
    
    # Give monitor a moment to start
    time.sleep(2)
    
    # Start Streamlit app
    start_streamlit_app()

if __name__ == "__main__":
    main()
