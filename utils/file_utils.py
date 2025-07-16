import os
import shutil
from pathlib import Path
from typing import List, Optional
import config

def get_file_type(file_path: str) -> Optional[str]:
    """
    Determine the file type based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File type string or None if not supported
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    return config.SUPPORTED_EXTENSIONS.get(extension)

def is_supported_file(file_path: str) -> bool:
    """
    Check if the file type is supported.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if supported, False otherwise
    """
    return get_file_type(file_path) is not None

def get_safe_filename(filename: str) -> str:
    """
    Generate a safe filename by removing/replacing problematic characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Replace problematic characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
    safe_filename = "".join(c if c in safe_chars else "_" for c in filename)
    
    # Ensure it doesn't start with a dot
    if safe_filename.startswith('.'):
        safe_filename = 'file_' + safe_filename
        
    return safe_filename

def copy_file_to_uploads(source_path: str, target_filename: Optional[str] = None) -> str:
    """
    Copy a file to the uploads directory.
    
    Args:
        source_path: Source file path
        target_filename: Optional target filename
        
    Returns:
        Path to the copied file
    """
    source = Path(source_path)
    
    if target_filename is None:
        target_filename = get_safe_filename(source.name)
    
    target_path = config.UPLOADS_DIR / target_filename
    
    # Handle duplicate filenames
    counter = 1
    original_target = target_path
    while target_path.exists():
        name = original_target.stem
        suffix = original_target.suffix
        target_path = config.UPLOADS_DIR / f"{name}_{counter}{suffix}"
        counter += 1
    
    shutil.copy2(source, target_path)
    return str(target_path)

def get_files_in_directory(directory: str, recursive: bool = True) -> List[str]:
    """
    Get all supported files in a directory.
    
    Args:
        directory: Directory path
        recursive: Whether to search recursively
        
    Returns:
        List of file paths
    """
    files = []
    directory = Path(directory)
    
    if not directory.exists():
        return files
    
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    for file_path in directory.glob(pattern):
        if file_path.is_file() and is_supported_file(str(file_path)):
            files.append(str(file_path))
    
    return files

def ensure_directory_exists(directory: str):
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    return Path(file_path).stat().st_size

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB" 