from docx import Document
from pathlib import Path

def parse_word(file_path: str) -> str:
    """
    Parse Word document and extract text content.
    
    Args:
        file_path: Path to the Word document (.docx or .doc)
        
    Returns:
        Extracted text content as string
        
    Raises:
        Exception: If Word document parsing fails
    """
    try:
        doc = Document(file_path)
        text_content = []
        
        # Extract text from paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    text_content.append(" | ".join(row_text))
        
        if not text_content:
            raise Exception("No text content found in Word document")
            
        return "\n\n".join(text_content)
        
    except Exception as e:
        raise Exception(f"Failed to parse Word document {file_path}: {str(e)}") 