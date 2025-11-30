#!/usr/bin/env python3
"""
Installation verification script for BizComply platform
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Found:", f"{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_backend_dependencies():
    """Check Python dependencies"""
    print("\n📦 Checking backend dependencies...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().splitlines()
        
        missing = []
        for req in requirements:
            if req.strip() and not req.startswith('#'):
                package = req.split('==')[0].split('>=')[0].split('<=')[0]
                try:
                    __import__(package)
                    print(f"✅ {package}")
                except ImportError:
                    missing.append(package)
                    print(f"❌ {package}")
        
        if missing:
            print(f"\n⚠️  Missing packages: {', '.join(missing)}")
            print("Run: pip install -r requirements.txt")
            return False
        
        return True
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def check_frontend_dependencies():
    """Check Node.js and frontend dependencies"""
    print("\n📦 Checking frontend dependencies...")
    
    # Check if node_modules exists
    frontend_dir = Path("frontend")
    node_modules_dir = frontend_dir / "node_modules"
    
    if not node_modules_dir.exists():
        print("❌ Frontend dependencies not installed")
        print("Run: cd frontend && npm install")
        return False
    
    # Check package.json
    package_json_path = frontend_dir / "package.json"
    if not package_json_path.exists():
        print("❌ package.json not found")
        return False
    
    try:
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        deps = package_data.get('dependencies', {})
        required_deps = ['@mui/material', '@mui/icons-material', 'axios', 'react', 'react-dom']
        
        for dep in required_deps:
            if dep in deps:
                print(f"✅ {dep}")
            else:
                print(f"❌ {dep} not in package.json")
        
        return True
    except json.JSONDecodeError:
        print("❌ Invalid package.json")
        return False

def check_environment_files():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("⚠️  .env file not found, but .env.example exists")
            print("Run: cp .env.example .env")
        else:
            print("❌ No environment files found")
            return False
    else:
        print("✅ .env file exists")
    
    frontend_env = Path("frontend/.env")
    if not frontend_env.exists():
        print("⚠️  Frontend .env not found")
        print("Create frontend/.env with REACT_APP_API_URL")
    else:
        print("✅ Frontend .env exists")
    
    return True

def check_data_directories():
    """Check required directories"""
    print("\n📁 Checking directories...")
    
    dirs_to_check = ['data', 'logs', 'documents']
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"⚠️  {dir_name}/ directory not found (will be created automatically)")
    
    return True

def check_config_files():
    """Check configuration files"""
    print("\n⚙️  Checking configuration files...")
    
    config_files = [
        'config/config.py',
        'services/regulatory_monitor.py',
        'api/v1/endpoints/regulatory.py',
        'app/main.py',
        'frontend/src/App.tsx',
        'frontend/src/pages/Dashboard.tsx',
        'frontend/src/pages/RegulatoryUpdates.tsx'
    ]
    
    all_exist = True
    for file_path in config_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exist = False
    
    return all_exist

def check_node_npm():
    """Check Node.js and npm"""
    print("\n🟢 Checking Node.js and npm...")
    
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False
    
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm: {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False
    
    return True

def main():
    """Main verification function"""
    print("🔍 BizComply Installation Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Node.js/npm", check_node_npm),
        ("Backend Dependencies", check_backend_dependencies),
        ("Frontend Dependencies", check_frontend_dependencies),
        ("Environment Files", check_environment_files),
        ("Data Directories", check_data_directories),
        ("Configuration Files", check_config_files),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    warnings = 0
    
    for name, result in results:
        if result:
            print(f"✅ {name}")
            passed += 1
        else:
            print(f"❌ {name}")
            failed += 1
    
    print(f"\n📈 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 Installation verified successfully!")
        print("\n🚀 You can now run the application:")
        print("   python start_all.py    # Full stack")
        print("   python run.py          # Streamlit only")
        print("   uvicorn app.main:app    # FastAPI only")
    else:
        print("\n⚠️  Some issues found. Please fix them before running the application.")
        print("\n📖 See INSTALL.md for detailed instructions")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
