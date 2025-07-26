import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from utils.store import clear_all_data, get_database_stats
import config

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    # Save original paths
    original_db = config.DB_FILE
    original_index = config.FAISS_INDEX_FILE
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    config.DB_FILE = temp_dir / "test_db.json"
    config.FAISS_INDEX_FILE = temp_dir / "test_index.faiss"
    
    yield temp_dir
    
    # Cleanup
    config.DB_FILE = original_db
    config.FAISS_INDEX_FILE = original_index
    
    # Remove temp files
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

class TestAPI:
    """Test API endpoints."""
    
    def test_frontend_loads(self, client):
        """Test that the frontend loads."""
        response = client.get("/")
        assert response.status_code == 200
        assert "AI Memory Bank" in response.text
    
    def test_statistics_endpoint(self, client, temp_db):
        """Test statistics endpoint."""
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "total_chunks" in data
    
    def test_store_text(self, client, temp_db):
        """Test storing text directly."""
        response = client.post("/store-text", json={
            "text": "This is a test document for the AI Memory Bank system."
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "document_id" in data
        assert data["chunk_count"] > 0
    
    def test_search_empty_database(self, client, temp_db):
        """Test search on empty database."""
        response = client.post("/search", json={
            "query": "test query",
            "top_k": 5
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] == 0
        assert len(data["results"]) == 0
    
    def test_search_with_content(self, client, temp_db):
        """Test search after adding content."""
        # First add some content
        client.post("/store-text", json={
            "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms."
        })
        
        # Now search for it
        response = client.post("/search", json={
            "query": "machine learning algorithms",
            "top_k": 5
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] > 0
        assert len(data["results"]) > 0
        assert "machine learning" in data["results"][0]["text"].lower()
    
    def test_file_upload_validation(self, client):
        """Test file upload with invalid file type."""
        with tempfile.NamedTemporaryFile(suffix=".xyz") as temp_file:
            temp_file.write(b"test content")
            temp_file.seek(0)
            
            response = client.post("/upload", files={
                "file": ("test.xyz", temp_file, "application/octet-stream")
            })
            assert response.status_code == 400
            assert "Unsupported file type" in response.json()["detail"]

class TestTextProcessing:
    """Test text processing functionality."""
    
    def test_chunk_text(self):
        """Test text chunking functionality."""
        from utils.store import chunk_text
        
        # Test short text (no chunking needed)
        short_text = "This is a short text."
        chunks = chunk_text(short_text)
        assert len(chunks) == 1
        assert chunks[0] == short_text
        
        # Test long text (chunking needed)
        long_text = "A" * 2000  # 2000 characters
        chunks = chunk_text(long_text, chunk_size=500, overlap=100)
        assert len(chunks) > 1
        
        # Test overlap
        if len(chunks) > 1:
            # Check that chunks have proper overlap
            assert chunks[0][-100:] == chunks[1][:100] or \
                   len(set(chunks[0][-50:]) & set(chunks[1][:50])) > 0

class TestFileUtils:
    """Test file utility functions."""
    
    def test_get_file_type(self):
        """Test file type detection."""
        from utils.file_utils import get_file_type
        
        assert get_file_type("document.pdf") == "pdf"
        assert get_file_type("notes.md") == "markdown"
        assert get_file_type("data.xlsx") == "excel"
        assert get_file_type("unsupported.xyz") is None
    
    def test_is_supported_file(self):
        """Test file support checking."""
        from utils.file_utils import is_supported_file
        
        assert is_supported_file("document.pdf") is True
        assert is_supported_file("notes.md") is True
        assert is_supported_file("unsupported.xyz") is False
    
    def test_safe_filename(self):
        """Test safe filename generation."""
        from utils.file_utils import get_safe_filename
        
        assert get_safe_filename("normal.txt") == "normal.txt"
        assert get_safe_filename("with spaces.txt") == "with_spaces.txt"
        assert get_safe_filename("with@special#chars.txt") == "with_special_chars.txt"

class TestEmbedder:
    """Test embedding functionality."""
    
    def test_embed_text(self):
        """Test single text embedding."""
        from embedder.embedder import embedder
        
        text = "This is a test sentence for embedding."
        embedding = embedder.embed_text(text)
        
        assert embedding is not None
        assert len(embedding) == config.EMBEDDING_DIMENSION
        assert embedding.dtype.name.startswith('float')
    
    def test_embed_batch(self):
        """Test batch text embedding."""
        from embedder.embedder import embedder
        
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence."
        ]
        embeddings = embedder.embed_batch(texts)
        
        assert embeddings is not None
        assert len(embeddings) == len(texts)
        assert embeddings.shape[1] == config.EMBEDDING_DIMENSION

if __name__ == "__main__":
    pytest.main([__file__]) 