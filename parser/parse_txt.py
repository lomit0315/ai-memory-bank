from pathlib import Path

def parse_text(file_path: str) -> str:
    """
    Parse plain text file and extract content.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Text content as string
        
    Raises:
        Exception: If text file parsing fails
    """
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin1', 'cp1252', 'ascii']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                return content.strip()
            except UnicodeDecodeError:
                continue
                
        # If all encodings fail, read as binary and decode with errors='ignore'
        with open(file_path, 'rb') as file:
            content = file.read().decode('utf-8', errors='ignore')
            
        return content.strip()
        
    except Exception as e:
        raise Exception(f"Failed to parse text file {file_path}: {str(e)}") 