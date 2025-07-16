from .parse_pdf import parse_pdf
from .parse_md import parse_markdown
from .parse_txt import parse_text
from .parse_word import parse_word
from .parse_excel import parse_excel
from .parse_powerpoint import parse_powerpoint

# Parser registry mapping file types to parser functions
PARSERS = {
    'pdf': parse_pdf,
    'markdown': parse_markdown,
    'text': parse_text,
    'word': parse_word,
    'excel': parse_excel,
    'powerpoint': parse_powerpoint
}

def get_parser(file_type):
    """Get the appropriate parser function for a file type."""
    return PARSERS.get(file_type)

__all__ = ['PARSERS', 'get_parser'] 