import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from parser import get_parser, PARSERS
from parser.parse_txt import parse_text
from parser.parse_md import parse_markdown

class TestParsers:
    """Test file parser functionality."""
    
    def test_get_parser(self):
        """Test parser registry."""
        assert get_parser("text") is not None
        assert get_parser("markdown") is not None
        assert get_parser("pdf") is not None
        assert get_parser("unsupported") is None
    
    def test_text_parser(self):
        """Test text file parsing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            test_content = "This is a test text file.\nWith multiple lines."
            f.write(test_content)
            f.flush()
            
            try:
                content = parse_text(f.name)
                assert content == test_content
            finally:
                os.unlink(f.name)
    
    def test_markdown_parser(self):
        """Test markdown file parsing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            test_content = """# Test Markdown
            
This is a **test** markdown file with:
- List items
- And formatting

## Section 2
Some more content."""
            f.write(test_content)
            f.flush()
            
            try:
                content = parse_markdown(f.name)
                assert "Test Markdown" in content
                assert "test" in content
                assert "Section 2" in content
            finally:
                os.unlink(f.name)
    
    def test_parser_with_empty_file(self):
        """Test parser with empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")  # Empty file
            f.flush()
            
            try:
                content = parse_text(f.name)
                assert content == ""
            finally:
                os.unlink(f.name)
    
    def test_parser_with_unicode(self):
        """Test parser with unicode content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            test_content = "Unicode test: 你好世界 🌍 café naïve résumé"
            f.write(test_content)
            f.flush()
            
            try:
                content = parse_text(f.name)
                assert content == test_content
                assert "你好世界" in content
                assert "🌍" in content
            finally:
                os.unlink(f.name)

if __name__ == "__main__":
    pytest.main([__file__]) 