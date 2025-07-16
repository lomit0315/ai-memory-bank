#!/usr/bin/env python3
"""
Startup script for AI Memory Bank with Frontend
Launches the API server and serves the web interface
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sentence_transformers
        import faiss
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_frontend():
    """Check if frontend files exist"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    required_files = ["index.html", "styles.css", "script.js"]
    missing_files = []
    
    for file in required_files:
        if not (frontend_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing frontend files: {', '.join(missing_files)}")
        return False
    
    print("✅ Frontend files found")
    return True

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting AI Memory Bank...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check frontend
    if not check_frontend():
        print("⚠️  Frontend not found, starting API-only mode")
    
    # Start the server
    try:
        print("🌐 Starting server on http://localhost:8000")
        print("📖 API documentation: http://localhost:8000/docs")
        print("🖥️  Web interface: http://localhost:8000")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open("http://localhost:8000")
            except:
                pass
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return True
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main function"""
    print("🧠 AI Memory Bank - Frontend Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the AI Memory Bank directory.")
        return 1
    
    success = start_server()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 