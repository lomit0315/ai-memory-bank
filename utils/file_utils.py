"""
File utilities for AI Memory Bank
Handles file type checking, path validation, and file operations
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Set, Optional
import logging
from config import SUPPORTED_EXTENSIONS, UPLOADS_DIR

logger = logging.getLogger(__name__)

def get_file_type(file_path: Path) -> Optional[str]:
    """
    Get the file type based on extension
    
    Args:
        file_path: Path to the file
    
    Returns:
        File type string or None if not supported
    """
    extension = file_path.suffix.lower()
    return SUPPORTED_EXTENSIONS.get(extension)

def is_supported_file(file_path: Path) -> bool:
    """
    Check if a file is supported by the memory bank
    
    Args:
        file_path: Path to the file
    
    Returns:
        True if file is supported, False otherwise
    """
    return get_file_type(file_path) is not None

def get_supported_extensions() -> Set[str]:
    """
    Get all supported file extensions
    
    Returns:
        Set of supported file extensions
    """
    return set(SUPPORTED_EXTENSIONS.keys())

def validate_file_path(file_path: Path) -> bool:
    """
    Validate that a file path exists and is accessible
    
    Args:
        file_path: Path to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        return file_path.exists() and file_path.is_file() and os.access(file_path, os.R_OK)
    except Exception:
        return False

def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to the file
    
    Returns:
        File size in bytes
    """
    try:
        return file_path.stat().st_size
    except Exception as e:
        logger.error(f"Failed to get file size for {file_path}: {e}")
        return 0

def copy_file_to_uploads(source_path: Path, filename: Optional[str] = None) -> Path:
    """
    Copy a file to the uploads directory
    
    Args:
        source_path: Source file path
        filename: Optional new filename (uses original if None)
    
    Returns:
        Path to the copied file in uploads directory
    """
    if not validate_file_path(source_path):
        raise FileNotFoundError(f"Source file not found or not accessible: {source_path}")
    
    if filename is None:
        filename = source_path.name
    
    # Ensure uploads directory exists
    UPLOADS_DIR.mkdir(exist_ok=True)
    
    # Create destination path
    dest_path = UPLOADS_DIR / filename
    
    # Handle filename conflicts
    counter = 1
    original_name = dest_path.stem
    original_suffix = dest_path.suffix
    
    while dest_path.exists():
        filename = f"{original_name}_{counter}{original_suffix}"
        dest_path = UPLOADS_DIR / filename
        counter += 1
    
    try:
        shutil.copy2(source_path, dest_path)
        logger.info(f"Copied {source_path} to {dest_path}")
        return dest_path
    except Exception as e:
        logger.error(f"Failed to copy {source_path} to {dest_path}: {e}")
        raise

def scan_directory_for_files(directory: Path, recursive: bool = True) -> List[Path]:
    """
    Scan a directory for supported files
    
    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories
    
    Returns:
        List of supported file paths
    """
    if not directory.exists() or not directory.is_dir():
        logger.warning(f"Directory does not exist or is not a directory: {directory}")
        return []
    
    supported_files = []
    
    try:
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and is_supported_file(file_path):
                supported_files.append(file_path)
        
        logger.info(f"Found {len(supported_files)} supported files in {directory}")
        return supported_files
        
    except Exception as e:
        logger.error(f"Failed to scan directory {directory}: {e}")
        return []

def get_file_info(file_path: Path) -> Dict:
    """
    Get comprehensive information about a file
    
    Args:
        file_path: Path to the file
    
    Returns:
        Dictionary with file information
    """
    try:
        stat = file_path.stat()
        file_type = get_file_type(file_path)
        
        return {
            "path": str(file_path),
            "name": file_path.name,
            "stem": file_path.stem,
            "suffix": file_path.suffix,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "file_type": file_type,
            "is_supported": file_type is not None,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "accessed": stat.st_atime,
            "exists": file_path.exists(),
            "is_file": file_path.is_file(),
            "is_readable": os.access(file_path, os.R_OK)
        }
    except Exception as e:
        logger.error(f"Failed to get file info for {file_path}: {e}")
        return {
            "path": str(file_path),
            "error": str(e)
        }

def cleanup_uploads_directory(max_age_days: int = 30) -> int:
    """
    Clean up old files in the uploads directory
    
    Args:
        max_age_days: Maximum age of files to keep in days
    
    Returns:
        Number of files removed
    """
    if not UPLOADS_DIR.exists():
        return 0
    
    import time
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60
    removed_count = 0
    
    try:
        for file_path in UPLOADS_DIR.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        removed_count += 1
                        logger.info(f"Removed old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove old file {file_path}: {e}")
        
        logger.info(f"Cleanup completed: {removed_count} files removed")
        return removed_count
        
    except Exception as e:
        logger.error(f"Failed to cleanup uploads directory: {e}")
        return 0

def get_uploads_directory_info() -> Dict:
    """
    Get information about the uploads directory
    
    Returns:
        Dictionary with uploads directory information
    """
    try:
        if not UPLOADS_DIR.exists():
            return {
                "path": str(UPLOADS_DIR),
                "exists": False,
                "total_files": 0,
                "supported_files": 0,
                "total_size_mb": 0
            }
        
        total_files = 0
        supported_files = 0
        total_size = 0
        
        for file_path in UPLOADS_DIR.iterdir():
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
                
                if is_supported_file(file_path):
                    supported_files += 1
        
        return {
            "path": str(UPLOADS_DIR),
            "exists": True,
            "total_files": total_files,
            "supported_files": supported_files,
            "unsupported_files": total_files - supported_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error(f"Failed to get uploads directory info: {e}")
        return {
            "path": str(UPLOADS_DIR),
            "error": str(e)
        } 