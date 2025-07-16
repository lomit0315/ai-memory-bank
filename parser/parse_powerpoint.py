from pptx import Presentation
from pathlib import Path

def parse_powerpoint(file_path: str) -> str:
    """
    Parse PowerPoint presentation and extract text content.
    
    Args:
        file_path: Path to the PowerPoint file (.pptx or .ppt)
        
    Returns:
        Extracted text content as string
        
    Raises:
        Exception: If PowerPoint parsing fails
    """
    try:
        presentation = Presentation(file_path)
        text_content = []
        
        for slide_num, slide in enumerate(presentation.slides, 1):
            slide_content = [f"=== Slide {slide_num} ==="]
            
            # Extract text from all shapes in the slide
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_content.append(shape.text.strip())
                elif hasattr(shape, "table"):
                    # Extract text from tables
                    for row in shape.table.rows:
                        row_text = []
                        for cell in row.cells:
                            if cell.text.strip():
                                row_text.append(cell.text.strip())
                        if row_text:
                            slide_content.append(" | ".join(row_text))
            
            # Only add slide if it has content
            if len(slide_content) > 1:  # More than just the slide header
                text_content.append("\n".join(slide_content))
        
        if not text_content:
            raise Exception("No text content found in PowerPoint presentation")
            
        return "\n\n".join(text_content)
        
    except Exception as e:
        raise Exception(f"Failed to parse PowerPoint file {file_path}: {str(e)}") 