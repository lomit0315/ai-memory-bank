from openpyxl import load_workbook
from pathlib import Path

def parse_excel(file_path: str) -> str:
    """
    Parse Excel file and extract text content.
    
    Args:
        file_path: Path to the Excel file (.xlsx or .xls)
        
    Returns:
        Extracted text content as string
        
    Raises:
        Exception: If Excel parsing fails
    """
    try:
        workbook = load_workbook(filename=file_path, read_only=True, data_only=True)
        text_content = []
        
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            sheet_content = [f"=== Sheet: {sheet_name} ==="]
            
            # Get all rows with data
            rows_with_data = []
            for row in sheet.iter_rows(values_only=True):
                # Skip empty rows
                if any(cell is not None and str(cell).strip() for cell in row):
                    row_text = []
                    for cell in row:
                        if cell is not None:
                            cell_value = str(cell).strip()
                            if cell_value:
                                row_text.append(cell_value)
                    if row_text:
                        rows_with_data.append(" | ".join(row_text))
            
            if rows_with_data:
                sheet_content.extend(rows_with_data)
                text_content.append("\n".join(sheet_content))
        
        workbook.close()
        
        if not text_content:
            raise Exception("No text content found in Excel file")
            
        return "\n\n".join(text_content)
        
    except Exception as e:
        raise Exception(f"Failed to parse Excel file {file_path}: {str(e)}") 