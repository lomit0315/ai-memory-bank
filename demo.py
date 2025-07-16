#!/usr/bin/env python3
"""
AI Memory Bank - Complete Demo
Demonstrates all features including file processing, search, and web interface
"""

import sys
import time
from pathlib import Path
import subprocess
import webbrowser
import threading

def print_header():
    print("🧠 AI Memory Bank - Complete Demo")
    print("=" * 50)
    print("This demo will show you the complete functionality of your AI Memory Bank")
    print("=" * 50)

def check_setup():
    """Check if everything is set up correctly"""
    print("🔍 Checking setup...")
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this from the AI Memory Bank directory.")
        return False
    
    # Check if frontend exists
    if not Path("frontend/index.html").exists():
        print("❌ Frontend not found. Please ensure frontend files are present.")
        return False
    
    # Check if test file exists
    if not Path("test_sample.txt").exists():
        print("❌ Test file not found. Please ensure test_sample.txt is present.")
        return False
    
    print("✅ Setup looks good!")
    return True

def demo_cli_operations():
    """Demonstrate CLI operations"""
    print("\n📟 CLI Operations Demo")
    print("-" * 30)
    
    print("1. Adding test file to memory bank...")
    result = subprocess.run([
        sys.executable, "app.py", "add-file", "test_sample.txt"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Test file added successfully")
    else:
        print(f"❌ Failed to add test file: {result.stderr}")
        return False
    
    print("\n2. Searching for 'machine learning'...")
    result = subprocess.run([
        sys.executable, "app.py", "search", "machine learning", "--top-k", "3"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Search completed successfully")
        print("📄 Search results:")
        print(result.stdout)
    else:
        print(f"❌ Search failed: {result.stderr}")
        return False
    
    print("\n3. Getting statistics...")
    result = subprocess.run([
        sys.executable, "app.py", "stats"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Statistics retrieved")
        print("📊 Statistics:")
        print(result.stdout)
    else:
        print(f"❌ Statistics failed: {result.stderr}")
        return False
    
    return True

def demo_web_interface():
    """Demonstrate web interface"""
    print("\n🌐 Web Interface Demo")
    print("-" * 30)
    
    print("Starting web server...")
    
    # Start server in background
    server_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app:app", 
        "--host", "127.0.0.1", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        print("✅ Server started on http://localhost:8000")
        print("🌐 Opening web interface in browser...")
        
        # Open browser
        webbrowser.open("http://localhost:8000")
        
        print("\n🎉 Web interface is now running!")
        print("📖 You can:")
        print("   - Upload files using drag & drop")
        print("   - Search your knowledge base")
        print("   - View statistics")
        print("   - Add text content manually")
        print("\n🔄 The interface will automatically update as you add more content")
        
        print("\n⏰ Web interface will run for 30 seconds...")
        print("   (You can continue using it after this demo)")
        
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Failed to start web interface: {e}")
    finally:
        # Stop server
        server_process.terminate()
        server_process.wait()
        print("🛑 Server stopped")

def demo_api_endpoints():
    """Demonstrate API endpoints"""
    print("\n🔌 API Endpoints Demo")
    print("-" * 30)
    
    print("Starting server for API demo...")
    
    # Start server in background
    server_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app:app", 
        "--host", "127.0.0.1", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(3)
    
    try:
        import requests
        
        print("✅ Server started")
        base_url = "http://localhost:8000"
        
        print("\n1. Testing search endpoint...")
        response = requests.post(f"{base_url}/search", json={
            "query": "neural networks",
            "top_k": 3
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful: {data['total_results']} results found")
        else:
            print(f"❌ Search failed: {response.status_code}")
        
        print("\n2. Testing statistics endpoint...")
        response = requests.get(f"{base_url}/statistics")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statistics retrieved: {data['statistics']['total_entries']} entries")
        else:
            print(f"❌ Statistics failed: {response.status_code}")
        
        print("\n3. Testing supported extensions endpoint...")
        response = requests.get(f"{base_url}/supported-extensions")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Extensions retrieved: {len(data['supported_extensions'])} supported formats")
        else:
            print(f"❌ Extensions failed: {response.status_code}")
        
        print(f"\n📖 API documentation available at: {base_url}/docs")
        
    except ImportError:
        print("⚠️  requests library not available, skipping API demo")
    except Exception as e:
        print(f"❌ API demo failed: {e}")
    finally:
        # Stop server
        server_process.terminate()
        server_process.wait()

def show_next_steps():
    """Show next steps for the user"""
    print("\n🎯 Next Steps")
    print("=" * 50)
    print("Your AI Memory Bank is ready to use!")
    print("\n📖 Quick Start:")
    print("1. Start the web interface: python start_frontend.py")
    print("2. Upload your documents using drag & drop")
    print("3. Search your knowledge base")
    print("4. Explore the API at http://localhost:8000/docs")
    
    print("\n🔧 CLI Commands:")
    print("- Add files: python app.py add-file <file>")
    print("- Search: python app.py search <query>")
    print("- Statistics: python app.py stats")
    print("- Clear data: python app.py clear")
    
    print("\n📚 Supported File Types:")
    print("- PDF (.pdf)")
    print("- Markdown (.md)")
    print("- Excel (.xlsx, .xls)")
    print("- Word (.docx, .doc)")
    print("- PowerPoint (.pptx, .ppt)")
    print("- Text (.txt)")
    
    print("\n🚀 Advanced Usage:")
    print("- Process entire directories: python app.py add-dir <directory>")
    print("- Custom search parameters: python app.py search <query> --top-k 10")
    print("- API integration: Use the REST endpoints for automation")
    
    print("\n💡 Tips:")
    print("- The embedding model downloads automatically on first use (~90MB)")
    print("- Large files are automatically chunked for better search")
    print("- All data is stored locally for privacy")
    print("- Use the web interface for the best user experience")

def main():
    """Main demo function"""
    print_header()
    
    if not check_setup():
        return 1
    
    print("\n🎬 Starting demo...")
    
    # Demo CLI operations
    if not demo_cli_operations():
        print("❌ CLI demo failed")
        return 1
    
    # Demo web interface
    demo_web_interface()
    
    # Demo API endpoints
    demo_api_endpoints()
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 Demo completed successfully!")
    print("Your AI Memory Bank is ready to use!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 