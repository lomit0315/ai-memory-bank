"""
Markdown file parser for AI Memory Bank
"""

from pathlib import Path
from typing import List, Dict, Any
import logging
import markdown
import re
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

def parse_markdown(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a markdown file and return structured content
    
    Args:
        file_path: Path to the markdown file
    
    Returns:
        List of dictionaries containing parsed content and metadata
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse markdown to HTML first
        html_content = markdown.markdown(content, extensions=['extra'])
        
        # Convert HTML to plain text while preserving structure
        plain_text = _html_to_text(html_content)
        
        # Clean the text
        plain_text = _clean_markdown_text(plain_text)
        
        # Split into chunks
        chunks = _chunk_markdown_text(plain_text)
        
        # Create structured output
        results = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Skip empty chunks
                results.append({
                    "content": chunk,
                    "metadata": {
                        "file_path": str(file_path),
                        "file_type": "markdown",
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk),
                        "file_size": len(content),
                        "original_format": "markdown"
                    }
                })
        
        logger.info(f"Parsed {file_path}: {len(results)} chunks created")
        return results
        
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
        raise

def _html_to_text(html: str) -> str:
    """Convert HTML to plain text while preserving structure"""
    # Remove HTML tags but preserve line breaks
    text = re.sub(r'<br\s*/?>', '\n', html)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'</div>', '\n', text)
    text = re.sub(r'</h[1-6]>', '\n\n', text)
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'</ul>', '\n\n', text)
    text = re.sub(r'</ol>', '\n\n', text)
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    return text

def _clean_markdown_text(text: str) -> str:
    """Clean and normalize markdown text content"""
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def _chunk_markdown_text(text: str) -> List[str]:
    """
    Split markdown text into overlapping chunks, respecting structure
    
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