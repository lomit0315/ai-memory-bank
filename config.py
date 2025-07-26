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

# Ollama configuration
OLLAMA_ENABLED = True  # Set to False to disable Ollama integration
OLLAMA_BASE_URL = "http://localhost:11434"  # Default Ollama API URL
OLLAMA_MODEL = "llama2"  # Default model (use "qwen" for Chinese users)
OLLAMA_TIMEOUT = 60  # Request timeout in seconds
OLLAMA_MAX_TOKENS = 2048  # Maximum tokens for response
OLLAMA_TEMPERATURE = 0.7  # Model temperature for creativity

# Available Ollama models (add your installed models here)
AVAILABLE_OLLAMA_MODELS = [
    "llama2",
    "llama2:13b", 
    "codellama",
    "mistral",
    "vicuna",
    "orca-mini",
    "llama2-chinese",  # For Chinese support
    "qwen",  # Another Chinese model
]

# Question answering configuration
QA_CONTEXT_CHUNKS = 5  # Number of chunks to include in context
QA_MAX_CONTEXT_LENGTH = 4000  # Maximum context length for QA
QA_SYSTEM_PROMPT = """You are an AI assistant helping users find information from their personal knowledge base. 
Use the provided context to answer questions accurately and helpfully. 
If the context doesn't contain relevant information, say so clearly.
Always cite which document(s) your answer comes from.""" 