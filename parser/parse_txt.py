"""
Plain text file parser for AI Memory Bank
"""

from pathlib import Path
from typing import List, Dict, Any
import logging
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

def parse_text(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a plain text file and return structured content
    
    Args:
        file_path: Path to the text file
    
    Returns:
        List of dictionaries containing parsed content and metadata
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean the content
        content = _clean_text(content)
        
        # Split into chunks
        chunks = _chunk_text(content)
        
        # Create structured output
        results = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Skip empty chunks
                results.append({
                    "content": chunk,
                    "metadata": {
                        "file_path": str(file_path),
                        "file_type": "text",
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk),
                        "file_size": len(content)
                    }
                })
        
        logger.info(f"Parsed {file_path}: {len(results)} chunks created")
        return results
        
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            content = _clean_text(content)
            chunks = _chunk_text(content)
            
            results = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    results.append({
                        "content": chunk,
                        "metadata": {
                            "file_path": str(file_path),
                            "file_type": "text",
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "chunk_size": len(chunk),
                            "file_size": len(content),
                            "encoding": "latin-1"
                        }
                    })
            
            logger.info(f"Parsed {file_path} with latin-1 encoding: {len(results)} chunks created")
            return results
            
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

def _clean_text(text: str) -> str:
    """Clean and normalize text content"""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    return text

def _chunk_text(text: str) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
    
    Returns:
        List of text chunks
    """
    if len(text) <= CHUNK_SIZE:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + CHUNK_SIZE
        
        # Try to break at sentence boundaries
        if end < len(text):
            # Look for sentence endings
            for i in range(end, max(start + CHUNK_SIZE - 100, start), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - CHUNK_OVERLAP
        if start >= len(text):
            break
    
    return chunks 