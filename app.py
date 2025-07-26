#!/usr/bin/env python3
"""
AI Memory Bank - Main Application
Personal AI-powered memory bank for storing and retrieving knowledge.
"""

import os
import sys
import click
import uvicorn
from pathlib import Path
from typing import List, Optional

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Local imports
import config
from parser import get_parser
from embedder.embedder import embedder
from utils.file_utils import (
    get_file_type, is_supported_file, copy_file_to_uploads,
    get_files_in_directory, format_file_size
)
from utils.store import (
    chunk_text, store_document, store_text_directly,
    get_database_stats, clear_all_data
)
from utils.search import search_similar_chunks, search_documents

# API Models
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    model: Optional[str] = None
    use_ollama: Optional[bool] = True

class StoreTextRequest(BaseModel):
    text: str

class SearchResponse(BaseModel):
    results: List[dict]
    total_results: int
    query: str

# Initialize FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory=str(config.FRONTEND_DIR)), name="static")

# CLI Commands
@click.group()
def cli():
    """AI Memory Bank - Personal knowledge management system."""
    pass

@cli.command("add-file")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--copy/--no-copy", default=True, help="Copy file to uploads directory")
def add_file_cli(file_path: str, copy: bool):
    """Add a single file to the memory bank."""
    try:
        result = process_file(file_path, copy_to_uploads=copy)
        click.echo(f"✅ Successfully added: {file_path}")
        click.echo(f"📄 Document ID: {result['document_id']}")
        click.echo(f"📊 Chunks created: {result['chunk_count']}")
    except Exception as e:
        click.echo(f"❌ Error processing file: {e}", err=True)
        sys.exit(1)

@cli.command("add-dir")
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--recursive/--no-recursive", default=True, help="Search recursively")
@click.option("--copy/--no-copy", default=True, help="Copy files to uploads directory")
def add_directory_cli(directory: str, recursive: bool, copy: bool):
    """Add all supported files from a directory."""
    try:
        files = get_files_in_directory(directory, recursive)
        
        if not files:
            click.echo("⚠️  No supported files found in directory")
            return
        
        click.echo(f"📁 Found {len(files)} supported files")
        
        with click.progressbar(files, label='Processing files') as bar:
            success_count = 0
            for file_path in bar:
                try:
                    process_file(file_path, copy_to_uploads=copy)
                    success_count += 1
                except Exception as e:
                    click.echo(f"\n❌ Error processing {file_path}: {e}")
        
        click.echo(f"✅ Successfully processed {success_count} out of {len(files)} files")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command("search")
@click.argument("query")
@click.option("--top-k", default=5, help="Number of results to return")
@click.option("--documents", is_flag=True, help="Search documents instead of chunks")
def search_cli(query: str, top_k: int, documents: bool):
    """Search the memory bank."""
    try:
        if documents:
            results = search_documents(query, top_k)
            display_document_results(results, query)
        else:
            results = search_similar_chunks(query, top_k)
            display_chunk_results(results, query)
            
    except Exception as e:
        click.echo(f"❌ Search error: {e}", err=True)
        sys.exit(1)

@cli.command("ask")
@click.argument("question")
@click.option("--model", default=None, help="Ollama model to use")
@click.option("--top-k", default=5, help="Number of search results to use as context")
@click.option("--no-ollama", is_flag=True, help="Disable Ollama, use search results only")
def ask_cli(question: str, model: str, top_k: int, no_ollama: bool):
    """Ask an AI question using the knowledge base."""
    import asyncio
    
    async def run_ask():
        try:
            from utils.qa_system import qa_system
            
            click.echo(f"🤖 Asking: '{question}'")
            if model:
                click.echo(f"📱 Using model: {model}")
            
            result = await qa_system.answer_question(
                question=question,
                top_k=top_k,
                model=model,
                use_ollama=not no_ollama
            )
            
            click.echo("\n" + "="*50)
            click.echo(f"❓ Question: {question}")
            click.echo("="*50)
            click.echo(f"🤖 Answer:\n{result['answer']}")
            click.echo("="*50)
            
            # Display metadata
            method = result['method']
            response_time = result['response_time']
            click.echo(f"📊 Method: {method} | Time: {response_time:.2f}s")
            
            # Display sources
            if result['sources']:
                click.echo(f"📚 Sources:")
                for source in result['sources']:
                    click.echo(f"   • {source}")
            
            # Display search results if no AI answer
            if method == "search_only" and result.get('search_results'):
                click.echo(f"\n🔍 Related search results:")
                for i, res in enumerate(result['search_results'][:3], 1):
                    text_preview = res['text'][:100] + "..." if len(res['text']) > 100 else res['text']
                    click.echo(f"   {i}. {text_preview}")
                    click.echo(f"      From: {res['document_info']['file_path']}")
            
        except Exception as e:
            click.echo(f"❌ Ask error: {e}", err=True)
            sys.exit(1)
    
    try:
        asyncio.run(run_ask())
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command("ollama-status")
def ollama_status_cli():
    """Check Ollama service status."""
    import asyncio
    
    async def check_status():
        try:
            from utils.qa_system import qa_system
            status = await qa_system.check_ollama_status()
            
            click.echo("🤖 Ollama Status")
            click.echo("=" * 30)
            click.echo(f"Enabled: {'✅' if status['enabled'] else '❌'}")
            click.echo(f"Available: {'✅' if status.get('available') else '❌'}")
            
            if status.get('available'):
                click.echo(f"Base URL: {status.get('base_url')}")
                click.echo(f"Default Model: {status.get('default_model')}")
                
                models = status.get('available_models', [])
                if models:
                    click.echo(f"Available Models ({len(models)}):")
                    for model in models:
                        click.echo(f"  • {model}")
                else:
                    click.echo("No models found")
            else:
                click.echo("💡 Tip: Start Ollama with 'ollama serve'")
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
    
    try:
        asyncio.run(check_status())
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

@cli.command("stats")
def stats_cli():
    """Show memory bank statistics."""
    try:
        stats = get_database_stats()
        click.echo("📊 AI Memory Bank Statistics")
        click.echo("=" * 30)
        click.echo(f"📄 Total documents: {stats['total_documents']}")
        click.echo(f"📝 Total chunks: {stats['total_chunks']}")
        click.echo(f"💾 Database size: {stats['database_size_mb']:.2f} MB")
        click.echo(f"🔍 Index size: {stats['index_size_mb']:.2f} MB")
        click.echo(f"⏰ Last updated: {stats['last_updated']}")
        
    except Exception as e:
        click.echo(f"❌ Error getting stats: {e}", err=True)
        sys.exit(1)

@cli.command("clear")
@click.confirmation_option(prompt="Are you sure you want to clear all data?")
def clear_cli():
    """Clear all data from the memory bank."""
    try:
        clear_all_data()
        click.echo("✅ All data cleared successfully!")
    except Exception as e:
        click.echo(f"❌ Error clearing data: {e}", err=True)
        sys.exit(1)

@cli.command("serve")
@click.option("--host", default=config.DEFAULT_HOST, help="Host to bind to")
@click.option("--port", default=config.DEFAULT_PORT, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve_cli(host: str, port: int, reload: bool):
    """Start the API server."""
    click.echo(f"🚀 Starting AI Memory Bank server at http://{host}:{port}")
    click.echo("📖 API documentation available at http://{host}:{port}/docs")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

# Core Functions
def process_file(file_path: str, copy_to_uploads: bool = True) -> dict:
    """
    Process a file and add it to the memory bank.
    
    Args:
        file_path: Path to the file
        copy_to_uploads: Whether to copy file to uploads directory
        
    Returns:
        Dictionary with processing results
    """
    if not is_supported_file(file_path):
        raise ValueError(f"Unsupported file type: {file_path}")
    
    file_type = get_file_type(file_path)
    if not file_type:
        raise ValueError(f"Unable to determine file type for: {file_path}")
    
    parser = get_parser(file_type)
    if not parser:
        raise ValueError(f"No parser found for file type: {file_type}")
    
    # Parse the file
    content = parser(file_path)
    
    if not content.strip():
        raise ValueError("No content extracted from file")
    
    # Copy file to uploads if requested
    if copy_to_uploads:
        file_path = copy_file_to_uploads(file_path)
    
    # Chunk the content
    chunks = chunk_text(content)
    
    # Generate embeddings
    embeddings = embedder.embed_batch(chunks)
    
    # Store in database
    doc_id = store_document(file_path, content, file_type, embeddings, chunks)
    
    return {
        "document_id": doc_id,
        "file_path": file_path,
        "file_type": file_type,
        "chunk_count": len(chunks),
        "content_length": len(content)
    }

def display_chunk_results(results: List[dict], query: str):
    """Display search results for chunks."""
    if not results:
        click.echo("❌ No results found")
        return
    
    click.echo(f"🔍 Search results for: '{query}'")
    click.echo("=" * 50)
    
    for i, result in enumerate(results, 1):
        score = result['score']
        text = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
        doc_info = result['document_info']
        
        click.echo(f"\n{i}. Score: {score:.3f}")
        click.echo(f"   📄 File: {doc_info['file_path']}")
        click.echo(f"   📝 Text: {text}")

def display_document_results(results: List[dict], query: str):
    """Display search results for documents."""
    if not results:
        click.echo("❌ No results found")
        return
    
    click.echo(f"🔍 Document search results for: '{query}'")
    click.echo("=" * 50)
    
    for i, result in enumerate(results, 1):
        max_score = result['max_score']
        chunk_count = result['chunk_count']
        best_chunk = result['best_chunk'][:200] + "..." if len(result['best_chunk']) > 200 else result['best_chunk']
        doc_info = result['document_info']
        
        click.echo(f"\n{i}. Max Score: {max_score:.3f} ({chunk_count} chunks)")
        click.echo(f"   📄 File: {doc_info['file_path']}")
        click.echo(f"   📝 Best match: {best_chunk}")

# API Routes
@app.get("/", response_class=HTMLResponse)
async def frontend():
    """Serve the frontend HTML page."""
    html_file = config.FRONTEND_DIR / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return HTMLResponse("<h1>AI Memory Bank</h1><p>Frontend not found</p>")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file."""
    try:
        # Check file type
        if not is_supported_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {list(config.SUPPORTED_EXTENSIONS.keys())}"
            )
        
        # Save uploaded file
        temp_path = config.UPLOADS_DIR / file.filename
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the file
        result = process_file(str(temp_path), copy_to_uploads=False)
        
        return {
            "success": True,
            "message": "File uploaded and processed successfully",
            "document_id": result["document_id"],
            "chunk_count": result["chunk_count"],
            "file_size": len(content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_api(request: SearchRequest):
    """Search the memory bank."""
    try:
        results = search_similar_chunks(request.query, request.top_k)
        
        return SearchResponse(
            results=results,
            total_results=len(results),
            query=request.query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/store-text")
async def store_text_api(request: StoreTextRequest):
    """Store text directly without a file."""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Chunk the text
        chunks = chunk_text(request.text)
        
        # Generate embeddings
        embeddings = embedder.embed_batch(chunks)
        
        # Store in database
        doc_id = store_text_directly(request.text, embeddings, chunks)
        
        return {
            "success": True,
            "message": "Text stored successfully",
            "document_id": doc_id,
            "chunk_count": len(chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_statistics():
    """Get memory bank statistics."""
    try:
        return get_database_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question using the knowledge base and Ollama."""
    try:
        from utils.qa_system import qa_system
        
        result = await qa_system.answer_question(
            question=request.question,
            top_k=request.top_k,
            model=request.model,
            use_ollama=request.use_ollama
        )
        
        return {
            "success": True,
            "answer": result["answer"],
            "question": result["question"],
            "sources": result["sources"],
            "method": result["method"],
            "response_time": result["response_time"],
            "metadata": result.get("ollama_metadata", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ollama/status")
async def get_ollama_status():
    """Get Ollama service status and available models."""
    try:
        from utils.qa_system import qa_system
        return await qa_system.check_ollama_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ollama/models")
async def get_ollama_models():
    """Get list of available Ollama models."""
    try:
        from utils.qa_system import qa_system
        models = await qa_system.get_available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    cli() 