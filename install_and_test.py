#!/usr/bin/env python3
"""
Installation verification and test script for AI Memory Bank
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_imports():
    """Test if all modules can be imported"""
    print("\n🔍 Testing imports...")
    
    modules_to_test = [
        "fastapi",
        "uvicorn", 
        "sentence_transformers",
        "faiss",
        "torch",
        "PyPDF2",
        "openpyxl",
        "markdown",
        "pandas",
        "numpy"
    ]
    
    failed_imports = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All imports successful")
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test configuration
        from config import get_config
        config = get_config()
        print("✅ Configuration loaded")
        
        # Test embedder
        from embedder.embedder import get_embedder
        embedder = get_embedder()
        print("✅ Embedder initialized")
        
        # Test search
        from utils.search import get_search
        search = get_search()
        print("✅ Search system initialized")
        
        # Test store
        from utils.store import get_store
        store = get_store()
        print("✅ Storage system initialized")
        
        # Test file utils
        from utils.file_utils import get_supported_extensions
        extensions = get_supported_extensions()
        print(f"✅ File utils working ({len(extensions)} supported extensions)")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_file_processing():
    """Test file processing with sample file"""
    print("\n📄 Testing file processing...")
    
    try:
        from app import add_file_cli
        
        # Test with sample file
        sample_file = Path("test_sample.txt")
        if not sample_file.exists():
            print("❌ Sample file not found")
            return False
        
        success = add_file_cli(str(sample_file), copy_to_uploads=False)
        
        if success:
            print("✅ File processing test successful")
            return True
        else:
            print("❌ File processing test failed")
            return False
            
    except Exception as e:
        print(f"❌ File processing test failed: {e}")
        return False

def test_search():
    """Test search functionality"""
    print("\n🔍 Testing search functionality...")
    
    try:
        from app import search_cli
        
        # Test search
        search_cli("machine learning", top_k=3)
        print("✅ Search test successful")
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 AI Memory Bank - Installation Verification")
    print("=" * 50)
    
    tests = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies),
        ("Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("File Processing", test_file_processing),
        ("Search", test_search)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI Memory Bank is ready to use.")
        print("\n📖 Next steps:")
        print("1. Add files: python app.py add-file your_document.pdf")
        print("2. Search: python app.py search 'your query'")
        print("3. Start API: python app.py serve")
        print("4. View help: python app.py --help")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 