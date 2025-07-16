#!/usr/bin/env python3
"""
AI Memory Bank - Main Application
Provides both CLI and API interfaces for managing and searching your personal knowledge base
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

# Import our modules
from config import get_config, API_HOST, API_PORT, API_TITLE, API_DESCRIPTION, LOG_LEVEL, LOG_FORMAT
from parser import parse_file, get_supported_extensions
from utils.file_utils import (
    is_supported_file, validate_file_path, copy_file_to_uploads, 
    scan_directory_for_files, get_uploads_directory_info
)
from utils.store import get_store
from utils.search import get_search
from embedder.embedder import get_embedder

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_memory_bank.log')
    ]
)

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except:
    pass  # Frontend directory might not exist

# Pydantic models for API
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.3

class TextStoreRequest(BaseModel):
    text: str
    metadata: Optional[dict] = None

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    chunks_added: Optional[int] = None

class SearchResponse(BaseModel):
    success: bool
    results: List[dict]
    total_results: int
    query: str

class StatisticsResponse(BaseModel):
    success: bool
    statistics: dict

# CLI Functions
def add_file_cli(file_path: str, copy_to_uploads: bool = True) -> bool:
    """Add a file to the memory bank via CLI"""
    try:
        path = Path(file_path)
        
        if not validate_file_path(path):
            logger.error(f"File not found or not accessible: {file_path}")
            return False
        
        if not is_supported_file(path):
            logger.error(f"Unsupported file type: {path.suffix}")
            return False
        
        # Copy to uploads if requested
        if copy_to_uploads:
            path = copy_file_to_uploads(path)
        
        # Parse the file
        logger.info(f"Parsing file: {path}")
        parsed_content = parse_file(path)
        
        if not parsed_content:
            logger.warning(f"No content extracted from {path}")
            return False
        
        # Store the content
        store = get_store()
        success = store.store_file_content(path, parsed_content)
        
        if success:
            logger.info(f"Successfully added {len(parsed_content)} chunks from {path}")
        else:
            logger.error(f"Failed to store content from {path}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error adding file {file_path}: {e}")
        return False

def add_directory_cli(directory_path: str, recursive: bool = True) -> int:
    """Add all supported files from a directory via CLI"""
    try:
        directory = Path(directory_path)
        
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found: {directory_path}")
            return 0
        
        # Scan for supported files
        files = scan_directory_for_files(directory, recursive)
        
        if not files:
            logger.warning(f"No supported files found in {directory_path}")
            return 0
        
        logger.info(f"Found {len(files)} supported files to process")
        
        # Process each file
        success_count = 0
        for file_path in files:
            if add_file_cli(str(file_path)):
                success_count += 1
        
        logger.info(f"Successfully processed {success_count}/{len(files)} files")
        return success_count
        
    except Exception as e:
        logger.error(f"Error processing directory {directory_path}: {e}")
        return 0

def search_cli(query: str, top_k: int = 5) -> None:
    """Search the memory bank via CLI"""
    try:
        search = get_search()
        results = search.search(query, top_k=top_k)
        
        if not results:
            print(f"No results found for query: {query}")
            return
        
        print(f"\nSearch results for: '{query}'")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Similarity: {result['similarity_score']:.3f}")
            print(f"   File: {result['metadata']['file_path']}")
            print(f"   Type: {result['metadata']['file_type']}")
            print(f"   Content: {result['content'][:200]}...")
            
            # Show additional metadata if available
            if 'chunk_index' in result['metadata']:
                print(f"   Chunk: {result['metadata']['chunk_index'] + 1}/{result['metadata']['total_chunks']}")
        
        print(f"\nTotal results: {len(results)}")
        
    except Exception as e:
        logger.error(f"Search error: {e}")

def statistics_cli() -> None:
    """Show memory bank statistics via CLI"""
    try:
        store = get_store()
        stats = store.get_statistics()
        
        print("\nAI Memory Bank Statistics")
        print("=" * 30)
        print(f"Total entries: {stats.get('total_entries', 0)}")
        print(f"Total vectors: {stats.get('total_vectors', 0)}")
        print(f"Unique files: {stats.get('unique_files', 0)}")
        print(f"Total content size: {stats.get('total_content_length', 0):,} characters")
        
        if 'file_types' in stats:
            print("\nFile types:")
            for file_type, count in stats['file_types'].items():
                print(f"  {file_type}: {count}")
        
        # Show uploads directory info
        uploads_info = get_uploads_directory_info()
        print(f"\nUploads directory: {uploads_info['path']}")
        print(f"Files in uploads: {uploads_info['supported_files']}/{uploads_info['total_files']}")
        print(f"Uploads size: {uploads_info['total_size_mb']:.2f} MB")
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")

def clear_cli() -> None:
    """Clear all data from the memory bank via CLI"""
    try:
        search = get_search()
        success = search.clear()
        
        if success:
            print("Memory bank cleared successfully")
        else:
            print("Failed to clear memory bank")
            
    except Exception as e:
        logger.error(f"Error clearing memory bank: {e}")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint - serves frontend or API info"""
    try:
        # Try to serve the frontend
        return FileResponse("frontend/index.html")
    except:
        # Fallback to API info
        return {
            "name": "AI Memory Bank",
            "version": "1.0.0",
            "description": "A personal AI-powered memory bank for storing and retrieving knowledge",
            "endpoints": {
                "upload": "/upload",
                "search": "/search",
                "statistics": "/statistics",
                "clear": "/clear"
            },
            "frontend": "Visit /static/ to access the web interface"
        }

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file"""
    try:
        # Check file type
        file_path = Path(file.filename)
        if not is_supported_file(file_path):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_path.suffix}"
            )
        
        # Save uploaded file
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        saved_path = uploads_dir / file.filename
        with open(saved_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse and store the file
        parsed_content = parse_file(saved_path)
        
        if not parsed_content:
            raise HTTPException(
                status_code=400,
                detail="No content could be extracted from the file"
            )
        
        store = get_store()
        success = store.store_file_content(saved_path, parsed_content)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store file content"
            )
        
        return FileUploadResponse(
            success=True,
            message=f"File uploaded and processed successfully",
            file_path=str(saved_path),
            chunks_added=len(parsed_content)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_memory(request: SearchRequest):
    """Search the memory bank"""
    try:
        search = get_search()
        results = search.search(
            request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        return SearchResponse(
            success=True,
            results=results,
            total_results=len(results),
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/store-text")
async def store_text(request: TextStoreRequest):
    """Store raw text content"""
    try:
        store = get_store()
        success = store.store_text_content(request.text, request.metadata)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store text content"
            )
        
        return {"success": True, "message": "Text stored successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Store text error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Get memory bank statistics"""
    try:
        store = get_store()
        stats = store.get_statistics()
        
        return StatisticsResponse(
            success=True,
            statistics=stats
        )
        
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
async def clear_memory():
    """Clear all data from the memory bank"""
    try:
        search = get_search()
        success = search.clear()
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to clear memory bank"
            )
        
        return {"success": True, "message": "Memory bank cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/supported-extensions")
async def get_supported_extensions():
    """Get list of supported file extensions"""
    return {
        "supported_extensions": list(get_supported_extensions())
    }

# CLI Main
def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Memory Bank - Personal knowledge management system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py add-file document.pdf
  python app.py add-dir /path/to/documents
  python app.py search "machine learning"
  python app.py stats
  python app.py serve
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add file command
    add_file_parser = subparsers.add_parser('add-file', help='Add a single file')
    add_file_parser.add_argument('file_path', help='Path to the file to add')
    add_file_parser.add_argument('--no-copy', action='store_true', 
                                help='Don\'t copy file to uploads directory')
    
    # Add directory command
    add_dir_parser = subparsers.add_parser('add-dir', help='Add all files from a directory')
    add_dir_parser.add_argument('directory_path', help='Path to the directory')
    add_dir_parser.add_argument('--no-recursive', action='store_true',
                               help='Don\'t scan subdirectories')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search the memory bank')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--top-k', type=int, default=5,
                              help='Number of results to return')
    
    # Statistics command
    subparsers.add_parser('stats', help='Show memory bank statistics')
    
    # Clear command
    subparsers.add_parser('clear', help='Clear all data from memory bank')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start the API server')
    serve_parser.add_argument('--host', default=API_HOST, help='Host to bind to')
    serve_parser.add_argument('--port', type=int, default=API_PORT, help='Port to bind to')
    serve_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'add-file':
            success = add_file_cli(args.file_path, not args.no_copy)
            sys.exit(0 if success else 1)
            
        elif args.command == 'add-dir':
            count = add_directory_cli(args.directory_path, not args.no_recursive)
            print(f"Successfully processed {count} files")
            
        elif args.command == 'search':
            search_cli(args.query, args.top_k)
            
        elif args.command == 'stats':
            statistics_cli()
            
        elif args.command == 'clear':
            clear_cli()
            
        elif args.command == 'serve':
            print(f"Starting AI Memory Bank API server on {args.host}:{args.port}")
            print("Press Ctrl+C to stop")
            uvicorn.run(
                "app:app",
                host=args.host,
                port=args.port,
                reload=args.reload
            )
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 