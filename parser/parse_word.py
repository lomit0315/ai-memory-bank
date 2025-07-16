"""
Word document parser for AI Memory Bank
"""

from pathlib import Path
from typing import List, Dict, Any
import logging
import re
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

def parse_word(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a Word document and return structured content
    
    Args:
        file_path: Path to the Word document
    
    Returns:
        List of dictionaries containing parsed content and metadata
    """
    try:
        from docx import Document
        
        # Load the document
        doc = Document(file_path)
        
        # Extract text from paragraphs
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        
        # Extract text from tables
        tables = []
        for table in doc.tables:
            table_text = []
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    table_text.append(" | ".join(row_text))
            if table_text:
                tables.append("\n".join(table_text))
        
        # Combine all content
        all_content = []
        if paragraphs:
            all_content.extend(paragraphs)
        if tables:
            all_content.extend(tables)
        
        combined_text = "\n\n".join(all_content)
        
        # Clean the text
        combined_text = _clean_word_text(combined_text)
        
        # Split into chunks
        chunks = _chunk_word_text(combined_text)
        
        # Create structured output
        results = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Skip empty chunks
                results.append({
                    "content": chunk,
                    "metadata": {
                        "file_path": str(file_path),
                        "file_type": "word",
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk),
                        "file_size": len(combined_text),
                        "total_paragraphs": len(paragraphs),
                        "total_tables": len(tables),
                        "word_info": {
                            "core_properties": {
                                "title": doc.core_properties.title or "",
                                "author": doc.core_properties.author or "",
                                "subject": doc.core_properties.subject or "",
                                "keywords": doc.core_properties.keywords or "",
                                "category": doc.core_properties.category or ""
                            }
                        }
                    }
                })
        
        logger.info(f"Parsed {file_path}: {len(results)} chunks created from {len(paragraphs)} paragraphs and {len(tables)} tables")
        return results
        
    except ImportError:
        logger.error("python-docx library not available. Install with: pip install python-docx")
        raise
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
        raise

def _clean_word_text(text: str) -> str:
    """Clean and normalize Word document text content"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Remove common Word artifacts
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\']+', ' ', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def _chunk_word_text(text: str) -> List[str]:
    """
    Split Word document text into overlapping chunks
    
    Args:
        text: Text to chunk
    
    Returns:
        List of text chunks
    """
    if len(text) <= CHUNK_SIZE:
        return [text]
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed chunk size
        if len(current_chunk) + len(paragraph) > CHUNK_SIZE and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap
            overlap_start = max(0, len(current_chunk) - CHUNK_OVERLAP)
            current_chunk = current_chunk[overlap_start:] + '\n\n' + paragraph
        else:
            if current_chunk:
                current_chunk += '\n\n' + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk if it has content
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # If we still have chunks that are too long, split them further
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= CHUNK_SIZE:
            final_chunks.append(chunk)
        else:
            # Split long chunks by sentences
            sentences = re.split(r'(?<=[.!?])\s+', chunk)
            temp_chunk = ""
            
            for sentence in sentences:
                if len(temp_chunk) + len(sentence) > CHUNK_SIZE and temp_chunk:
                    final_chunks.append(temp_chunk.strip())
                    temp_chunk = sentence
                else:
                    if temp_chunk:
                        temp_chunk += ' ' + sentence
                    else:
                        temp_chunk = sentence
            
            if temp_chunk.strip():
                final_chunks.append(temp_chunk.strip())
    
    return final_chunks 