import markdown
import re
from pathlib import Path

def parse_markdown(file_path: str) -> str:
    """
    Parse Markdown file and extract text content.
    
    Args:
        file_path: Path to the Markdown file
        
    Returns:
        Extracted text content as string
        
    Raises:
        Exception: If Markdown parsing fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        # Convert markdown to HTML then extract text
        html = markdown.markdown(markdown_content)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Failed to parse Markdown file {file_path}: {str(e)}") 