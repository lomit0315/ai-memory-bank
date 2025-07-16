"""
File parsers for AI Memory Bank
Supports multiple file formats: markdown, PDF, Excel, Word, PowerPoint, and plain text
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from .parse_md import parse_markdown
from .parse_pdf import parse_pdf
from .parse_excel import parse_excel
from .parse_txt import parse_text
from .parse_word import parse_word
from .parse_powerpoint import parse_powerpoint

logger = logging.getLogger(__name__)

# Parser registry
PARSERS = {
    "markdown": parse_markdown,
    "pdf": parse_pdf,
    "excel": parse_excel,
    "text": parse_text,
    "word": parse_word,
    "powerpoint": parse_powerpoint
}

def parse_file(file_path: Path, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Parse a file and return structured content with metadata
    
    Args:
        file_path: Path to the file to parse
        file_type: Type of file (auto-detected if None)
    
    Returns:
        List of dictionaries containing parsed content and metadata
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_type is None:
        file_type = _detect_file_type(file_path)
    
    if file_type not in PARSERS:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    try:
        logger.info(f"Parsing {file_path} as {file_type}")
        return PARSERS[file_type](file_path)
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {e}")
        raise

def _detect_file_type(file_path: Path) -> str:
    """Detect file type based on extension"""
    extension = file_path.suffix.lower()
    
    # Extension to type mapping
    extension_map = {
        ".md": "markdown",
        ".pdf": "pdf",
        ".xlsx": "excel",
        ".xls": "excel",
        ".txt": "text",
        ".docx": "word",
        ".doc": "word",
        ".pptx": "powerpoint",
        ".ppt": "powerpoint"
    }
    
    return extension_map.get(extension, "text")

def get_supported_extensions() -> Dict[str, str]:
    """Get mapping of file extensions to parser types"""
    return {
        ".md": "markdown",
        ".pdf": "pdf",
        ".xlsx": "excel",
        ".xls": "excel",
        ".txt": "text",
        ".docx": "word",
        ".doc": "word",
        ".pptx": "powerpoint",
        ".ppt": "powerpoint"
    } 