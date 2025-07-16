"""
PDF file parser for AI Memory Bank
"""

from pathlib import Path
from typing import List, Dict, Any
import logging
import PyPDF2
import re
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

def parse_pdf(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a PDF file and return structured content
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        List of dictionaries containing parsed content and metadata
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            all_text = ""
            page_texts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        page_texts.append({
                            "page": page_num + 1,
                            "text": page_text
                        })
                        all_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            # Clean the text
            all_text = _clean_pdf_text(all_text)
            
            # Split into chunks
            chunks = _chunk_pdf_text(all_text, page_texts)
            
            # Create structured output
            results = []
            for i, chunk in enumerate(chunks):
                if chunk["content"].strip():  # Skip empty chunks
                    results.append({
                        "content": chunk["content"],
                        "metadata": {
                            "file_path": str(file_path),
                            "file_type": "pdf",
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "chunk_size": len(chunk["content"]),
                            "file_size": len(all_text),
                            "total_pages": len(pdf_reader.pages),
                            "pages_in_chunk": chunk.get("pages", []),
                            "pdf_info": {
                                "title": pdf_reader.metadata.get('/Title', ''),
                                "author": pdf_reader.metadata.get('/Author', ''),
                                "subject": pdf_reader.metadata.get('/Subject', ''),
                                "creator": pdf_reader.metadata.get('/Creator', '')
                            }
                        }
                    })
            
            logger.info(f"Parsed {file_path}: {len(results)} chunks created from {len(pdf_reader.pages)} pages")
            return results
            
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
        raise

def _clean_pdf_text(text: str) -> str:
    """Clean and normalize PDF text content"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page separators
    text = re.sub(r'--- Page \d+ ---', '', text)
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Remove common PDF artifacts
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\']+', ' ', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def _chunk_pdf_text(text: str, page_texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Split PDF text into overlapping chunks, preserving page information
    
    Args:
        text: Full text content
        page_texts: List of page texts with page numbers
    
    Returns:
        List of chunk dictionaries with content and page information
    """
    if len(text) <= CHUNK_SIZE:
        return [{"content": text, "pages": [pt["page"] for pt in page_texts]}]
    
    chunks = []
    current_chunk = ""
    current_pages = set()
    start_pos = 0
    
    # Create a mapping of text positions to pages
    page_positions = _map_text_to_pages(text, page_texts)
    
    while start_pos < len(text):
        end_pos = start_pos + CHUNK_SIZE
        
        # Try to break at sentence boundaries
        if end_pos < len(text):
            for i in range(end_pos, max(start_pos + CHUNK_SIZE - 100, start_pos), -1):
                if text[i] in '.!?':
                    end_pos = i + 1
                    break
        
        chunk_text = text[start_pos:end_pos].strip()
        
        if chunk_text:
            # Find which pages this chunk contains
            chunk_pages = set()
            for pos in range(start_pos, end_pos):
                if pos in page_positions:
                    chunk_pages.update(page_positions[pos])
            
            chunks.append({
                "content": chunk_text,
                "pages": sorted(list(chunk_pages))
            })
        
        # Move start position with overlap
        start_pos = end_pos - CHUNK_OVERLAP
        if start_pos >= len(text):
            break
    
    return chunks

def _map_text_to_pages(text: str, page_texts: List[Dict[str, Any]]) -> Dict[int, List[int]]:
    """
    Create a mapping from text positions to page numbers
    
    Args:
        text: Full text content
        page_texts: List of page texts with page numbers
    
    Returns:
        Dictionary mapping text positions to list of page numbers
    """
    position_to_pages = {}
    current_pos = 0
    
    for page_info in page_texts:
        page_text = page_info["text"]
        page_num = page_info["page"]
        
        # Find where this page text appears in the full text
        page_start = text.find(page_text, current_pos)
        if page_start != -1:
            page_end = page_start + len(page_text)
            
            # Mark all positions in this page
            for pos in range(page_start, page_end):
                if pos not in position_to_pages:
                    position_to_pages[pos] = []
                position_to_pages[pos].append(page_num)
            
            current_pos = page_end
    
    return position_to_pages 