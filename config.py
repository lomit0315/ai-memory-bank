import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
MEMORY_DIR = PROJECT_ROOT / "memory"
UPLOADS_DIR = PROJECT_ROOT / "uploads"
MODEL_CACHE_DIR = PROJECT_ROOT / "embedder" / "model_cache"

# Ensure directories exist
MEMORY_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
MODEL_CACHE_DIR.mkdir(exist_ok=True)

# Database files
DB_FILE = MEMORY_DIR / "db.json"
FAISS_INDEX_FILE = MEMORY_DIR / "faiss.index"

# Embedding model configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2

# Text processing configuration
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
MAX_CHUNK_SIZE = 2000  # Maximum chunk size

# Search configuration
DEFAULT_TOP_K = 5  # Default number of search results
MIN_SIMILARITY_THRESHOLD = 0.3  # Minimum similarity score
BATCH_SIZE = 32  # Batch size for embedding generation

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.pdf': 'pdf',
    '.md': 'markdown', 
    '.markdown': 'markdown',
    '.txt': 'text',
    '.docx': 'word',
    '.doc': 'word',
    '.xlsx': 'excel',
    '.xls': 'excel', 
    '.pptx': 'powerpoint',
    '.ppt': 'powerpoint'
}

# API configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000
API_TITLE = "AI Memory Bank API"
API_DESCRIPTION = "AI-powered personal knowledge management system"
API_VERSION = "1.0.0"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = PROJECT_ROOT / "ai_memory_bank.log"

# Frontend configuration
FRONTEND_DIR = PROJECT_ROOT / "frontend" 