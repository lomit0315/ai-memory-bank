import PyPDF2
from pathlib import Path

def parse_pdf(file_path: str) -> str:
    """
    Parse PDF file and extract text content.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content as string
        
    Raises:
        Exception: If PDF parsing fails
    """
    try:
        text_content = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():  # Only add non-empty pages
                        text_content.append(f"=== Page {page_num + 1} ===\n{page_text}")
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_num + 1}: {e}")
                    continue
        
        if not text_content:
            raise Exception("No text content could be extracted from PDF")
            
        return "\n\n".join(text_content)
        
    except Exception as e:
        raise Exception(f"Failed to parse PDF file {file_path}: {str(e)}") 