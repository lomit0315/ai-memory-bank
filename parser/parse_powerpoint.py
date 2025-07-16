"""
PowerPoint presentation parser for AI Memory Bank
"""

from pathlib import Path
from typing import List, Dict, Any
import logging
import re
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

def parse_powerpoint(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a PowerPoint presentation and return structured content
    
    Args:
        file_path: Path to the PowerPoint file
    
    Returns:
        List of dictionaries containing parsed content and metadata
    """
    try:
        from pptx import Presentation
        
        # Load the presentation
        prs = Presentation(file_path)
        
        # Extract text from slides
        slides = []
        for slide_num, slide in enumerate(prs.slides, 1):
            slide_text = []
            slide_text.append(f"Slide {slide_num}")
            slide_text.append("-" * (len(f"Slide {slide_num}") + 2))
            
            # Extract text from shapes
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text.strip())
            
            # Extract text from tables
            for shape in slide.shapes:
                if shape.has_table:
                    table_text = []
                    for row in shape.table.rows:
                        row_text = []
                        for cell in row.cells:
                            if cell.text.strip():
                                row_text.append(cell.text.strip())
                        if row_text:
                            table_text.append(" | ".join(row_text))
                    if table_text:
                        slide_text.append("\n".join(table_text))
            
            if len(slide_text) > 2:  # More than just slide title
                slides.append("\n".join(slide_text))
        
        # Combine all content
        combined_text = "\n\n".join(slides)
        
        # Clean the text
        combined_text = _clean_powerpoint_text(combined_text)
        
        # Split into chunks
        chunks = _chunk_powerpoint_text(combined_text, slides)
        
        # Create structured output
        results = []
        for i, chunk in enumerate(chunks):
            if chunk["content"].strip():  # Skip empty chunks
                results.append({
                    "content": chunk["content"],
                    "metadata": {
                        "file_path": str(file_path),
                        "file_type": "powerpoint",
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk["content"]),
                        "file_size": len(combined_text),
                        "total_slides": len(prs.slides),
                        "slides_in_chunk": chunk.get("slides", []),
                        "powerpoint_info": {
                            "core_properties": {
                                "title": prs.core_properties.title or "",
                                "author": prs.core_properties.author or "",
                                "subject": prs.core_properties.subject or "",
                                "keywords": prs.core_properties.keywords or "",
                                "category": prs.core_properties.category or ""
                            }
                        }
                    }
                })
        
        logger.info(f"Parsed {file_path}: {len(results)} chunks created from {len(prs.slides)} slides")
        return results
        
    except ImportError:
        logger.error("python-pptx library not available. Install with: pip install python-pptx")
        raise
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
        raise

def _clean_powerpoint_text(text: str) -> str:
    """Clean and normalize PowerPoint text content"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Remove common PowerPoint artifacts
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\']+', ' ', text)
    
    # Clean up slide separators
    text = re.sub(r'Slide \d+\n-+\n', '\n\n', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def _chunk_powerpoint_text(text: str, slides: List[str]) -> List[Dict[str, Any]]:
    """
    Split PowerPoint text into overlapping chunks, preserving slide information
    
    Args:
        text: Full text content
        slides: List of slide texts
    
    Returns:
        List of chunk dictionaries with content and slide information
    """
    if len(text) <= CHUNK_SIZE:
        return [{"content": text, "slides": list(range(1, len(slides) + 1))}]
    
    chunks = []
    current_chunk = ""
    start_pos = 0
    
    # Create a mapping of text positions to slides
    slide_positions = _map_text_to_slides(text, slides)
    
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
            # Find which slides this chunk contains
            chunk_slides = set()
            for pos in range(start_pos, end_pos):
                if pos in slide_positions:
                    chunk_slides.update(slide_positions[pos])
            
            chunks.append({
                "content": chunk_text,
                "slides": sorted(list(chunk_slides))
            })
        
        # Move start position with overlap
        start_pos = end_pos - CHUNK_OVERLAP
        if start_pos >= len(text):
            break
    
    return chunks

def _map_text_to_slides(text: str, slides: List[str]) -> Dict[int, List[int]]:
    """
    Create a mapping from text positions to slide numbers
    
    Args:
        text: Full text content
        slides: List of slide texts
    
    Returns:
        Dictionary mapping text positions to list of slide numbers
    """
    position_to_slides = {}
    current_pos = 0
    
    for slide_num, slide_text in enumerate(slides, 1):
        # Find where this slide text appears in the full text
        slide_start = text.find(slide_text, current_pos)
        if slide_start != -1:
            slide_end = slide_start + len(slide_text)
            
            # Mark all positions in this slide
            for pos in range(slide_start, slide_end):
                if pos not in position_to_slides:
                    position_to_slides[pos] = []
                position_to_slides[pos].append(slide_num)
            
            current_pos = slide_end
    
    return position_to_slides 