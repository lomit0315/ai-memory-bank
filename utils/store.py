import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
import config

def load_database() -> Dict[str, Any]:
    """
    Load the JSON database.
    
    Returns:
        Database dictionary
    """
    if config.DB_FILE.exists():
        try:
            with open(config.DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Return empty database structure
    return {
        "documents": {},
        "chunks": {},
        "metadata": {
            "total_documents": 0,
            "total_chunks": 0,
            "last_updated": datetime.now().isoformat()
        }
    }

def save_database(database: Dict[str, Any]):
    """
    Save the database to JSON file.
    
    Args:
        database: Database dictionary to save
    """
    database["metadata"]["last_updated"] = datetime.now().isoformat()
    
    with open(config.DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)

def load_faiss_index() -> Optional[faiss.Index]:
    """
    Load the FAISS index.
    
    Returns:
        FAISS index or None if not found
    """
    if config.FAISS_INDEX_FILE.exists():
        try:
            return faiss.read_index(str(config.FAISS_INDEX_FILE))
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            return None
    return None

def save_faiss_index(index: faiss.Index):
    """
    Save the FAISS index.
    
    Args:
        index: FAISS index to save
    """
    faiss.write_index(index, str(config.FAISS_INDEX_FILE))

def create_faiss_index(dimension: int) -> faiss.Index:
    """
    Create a new FAISS index.
    
    Args:
        dimension: Embedding dimension
        
    Returns:
        New FAISS index
    """
    # Use IndexFlatIP for cosine similarity
    index = faiss.IndexFlatIP(dimension)
    return index

def chunk_text(text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None) -> List[str]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = config.CHUNK_SIZE
    if overlap is None:
        overlap = config.CHUNK_OVERLAP
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at a sentence or word boundary
        if end < len(text):
            # Look for sentence end
            sentence_end = text.rfind('.', start, end)
            if sentence_end > start:
                end = sentence_end + 1
            else:
                # Look for word boundary
                word_end = text.rfind(' ', start, end)
                if word_end > start:
                    end = word_end
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        if end >= len(text):
            break
            
        start = end - overlap
    
    return chunks

def store_document(
    file_path: str,
    content: str,
    file_type: str,
    embeddings: np.ndarray,
    chunks: List[str]
) -> str:
    """
    Store a document and its chunks in the database and FAISS index.
    
    Args:
        file_path: Path to the original file
        content: Full text content
        file_type: Type of the file
        embeddings: Chunk embeddings
        chunks: Text chunks
        
    Returns:
        Document ID
    """
    database = load_database()
    index = load_faiss_index()
    
    if index is None:
        index = create_faiss_index(config.EMBEDDING_DIMENSION)
    
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    # Store document metadata
    document_data = {
        "id": doc_id,
        "file_path": file_path,
        "file_type": file_type,
        "content": content,
        "chunk_count": len(chunks),
        "created_at": datetime.now().isoformat(),
        "file_size": len(content)
    }
    
    database["documents"][doc_id] = document_data
    
    # Store chunks and add to FAISS index
    chunk_ids = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = f"{doc_id}_{i}"
        chunk_ids.append(chunk_id)
        
        chunk_data = {
            "id": chunk_id,
            "document_id": doc_id,
            "chunk_index": i,
            "text": chunk,
            "created_at": datetime.now().isoformat()
        }
        
        database["chunks"][chunk_id] = chunk_data
        
        # Add to FAISS index
        # Normalize embedding for cosine similarity
        normalized_embedding = embedding / np.linalg.norm(embedding)
        index.add(normalized_embedding.reshape(1, -1))
    
    # Update metadata
    database["metadata"]["total_documents"] += 1
    database["metadata"]["total_chunks"] += len(chunks)
    
    # Save everything
    save_database(database)
    save_faiss_index(index)
    
    return doc_id

def store_text_directly(text: str, embeddings: np.ndarray, chunks: List[str]) -> str:
    """
    Store text directly without a file.
    
    Args:
        text: Text content
        embeddings: Chunk embeddings
        chunks: Text chunks
        
    Returns:
        Document ID
    """
    return store_document(
        file_path="<direct_text>",
        content=text,
        file_type="text",
        embeddings=embeddings,
        chunks=chunks
    )

def get_database_stats() -> Dict[str, Any]:
    """
    Get database statistics.
    
    Returns:
        Statistics dictionary
    """
    database = load_database()
    
    stats = {
        "total_documents": database["metadata"]["total_documents"],
        "total_chunks": database["metadata"]["total_chunks"],
        "last_updated": database["metadata"]["last_updated"],
        "database_size_mb": config.DB_FILE.stat().st_size / (1024 * 1024) if config.DB_FILE.exists() else 0,
        "index_size_mb": config.FAISS_INDEX_FILE.stat().st_size / (1024 * 1024) if config.FAISS_INDEX_FILE.exists() else 0
    }
    
    return stats

def clear_all_data():
    """Clear all data from the database and FAISS index."""
    if config.DB_FILE.exists():
        config.DB_FILE.unlink()
    if config.FAISS_INDEX_FILE.exists():
        config.FAISS_INDEX_FILE.unlink()
    print("All data cleared successfully!") 