#!/usr/bin/env python3
"""
Frontend launcher script for AI Memory Bank
Starts the server and optionally opens the browser
"""

import webbrowser
import time
import threading
import sys
import os
from pathlib import Path

import uvicorn
import click

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import config

def open_browser(url, delay=2):
    """Open browser after a delay to ensure server is ready."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        print(f"🌐 Opened browser to {url}")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"Please manually open: {url}")

@click.command()
@click.option("--host", default=config.DEFAULT_HOST, help="Host to bind to")
@click.option("--port", default=config.DEFAULT_PORT, help="Port to bind to")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def main(host, port, no_browser, reload):
    """
    Start the AI Memory Bank frontend server.
    
    This script will:
    1. Start the FastAPI server
    2. Automatically open your browser (unless --no-browser is specified)
    3. Display helpful information about the running server
    """
    
    # Check if dependencies are available
    try:
        import app
    except ImportError as e:
        print(f"❌ Error importing dependencies: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Construct the URL
    url = f"http://{host}:{port}"
    
    # Start browser in background thread (unless disabled)
    if not no_browser:
        browser_thread = threading.Thread(
            target=open_browser, 
            args=(url,), 
            daemon=True
        )
        browser_thread.start()
    
    # Display startup information
    print("🧠 AI Memory Bank - Starting Server")
    print("=" * 40)
    print(f"🌐 Server URL: {url}")
    print(f"📖 API Docs: {url}/docs")
    print(f"🎯 Host: {host}")
    print(f"🔌 Port: {port}")
    print("=" * 40)
    print("Press Ctrl+C to stop the server")
    print()
    
    # Start the server
    try:
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 