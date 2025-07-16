"""
Global configuration for AI Memory Bank
"""
import os
from pathlib import Path
from typing import Dict, Any

# Base paths
BASE_DIR = Path(__file__).parent
MEMORY_DIR = BASE_DIR / "memory"
UPLOADS_DIR = BASE_DIR / "uploads"
MODEL_CACHE_DIR = BASE_DIR / "embedder" / "model_cache"

# Ensure directories exist
MEMORY_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
MODEL_CACHE_DIR.mkdir(exist_ok=True)

# Database and index files
DB_FILE = MEMORY_DIR / "db.json"
FAISS_INDEX_FILE = MEMORY_DIR / "faiss.index"

# Embedding model configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and effective for most use cases
EMBEDDING_DIMENSION = 384  # Dimension of the embedding vectors
MAX_SEQUENCE_LENGTH = 512  # Maximum token length for embeddings

# Search configuration
DEFAULT_TOP_K = 5  # Number of results to return by default
SIMILARITY_THRESHOLD = 0.3  # Minimum similarity score to include in results

# File processing configuration
SUPPORTED_EXTENSIONS = {
    ".txt": "text",
    ".md": "markdown", 
    ".pdf": "pdf",
    ".xlsx": "excel",
    ".xls": "excel",
    ".docx": "word",
    ".doc": "word",
    ".pptx": "powerpoint",
    ".ppt": "powerpoint"
}

# Chunking configuration for large documents
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks

# API configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "AI Memory Bank"
API_DESCRIPTION = "A personal AI-powered memory bank for storing and retrieving knowledge from various file formats"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Environment variables
ENV_FILE = BASE_DIR / ".env"

# Model cache configuration
CACHE_MODELS = True
MODEL_CACHE_SIZE = "2GB"  # Maximum cache size for downloaded models

# Performance settings
BATCH_SIZE = 32  # For processing multiple documents
MAX_WORKERS = 4  # For parallel processing

def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary"""
    return {
        "base_dir": str(BASE_DIR),
        "memory_dir": str(MEMORY_DIR),
        "uploads_dir": str(UPLOADS_DIR),
        "model_cache_dir": str(MODEL_CACHE_DIR),
        "db_file": str(DB_FILE),
        "faiss_index_file": str(FAISS_INDEX_FILE),
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimension": EMBEDDING_DIMENSION,
        "max_sequence_length": MAX_SEQUENCE_LENGTH,
        "default_top_k": DEFAULT_TOP_K,
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "supported_extensions": SUPPORTED_EXTENSIONS,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "api_host": API_HOST,
        "api_port": API_PORT,
        "api_title": API_TITLE,
        "api_description": API_DESCRIPTION,
        "log_level": LOG_LEVEL,
        "log_format": LOG_FORMAT,
        "cache_models": CACHE_MODELS,
        "model_cache_size": MODEL_CACHE_SIZE,
        "batch_size": BATCH_SIZE,
        "max_workers": MAX_WORKERS
    } 