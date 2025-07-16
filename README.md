# AI Memory Bank

A personal AI-powered memory bank for storing and retrieving knowledge from various file formats. This system uses semantic search to help you find relevant information across your documents, notes, and files.

## Features

- **Multi-format Support**: Parse and index content from PDF, Markdown, Excel, Word, PowerPoint, and plain text files
- **Semantic Search**: Find relevant content using AI-powered vector embeddings
- **Smart Chunking**: Automatically split large documents into manageable chunks while preserving context
- **Triple Interface**: CLI, REST API, and modern web interface
- **Local Storage**: All data stored locally for privacy and security
- **Fast Retrieval**: FAISS-based vector search for quick and accurate results
- **Modern UI**: Beautiful, responsive web interface with drag-and-drop file upload
- **Real-time Feedback**: Progress indicators and live search results

## Project Structure

```
ai_memory_bank/
├── app.py                   # Main entry point (CLI or API)
├── config.py                # Global configs: paths, model names, constants
├── requirements.txt         # All dependencies
├── start_frontend.py        # Frontend launcher script
│
├── frontend/                # Web interface
│   ├── index.html           # Main HTML page
│   ├── styles.css           # Modern CSS styling
│   └── script.js            # Frontend JavaScript
│
├── memory/                  # Local database + FAISS index
│   ├── db.json              # Stores parsed text + metadata
│   └── faiss.index          # FAISS vector index
│
├── parser/                  # File parsers for each format
│   ├── parse_md.py          # Markdown → plain text
│   ├── parse_pdf.py         # PDF → plain text
│   ├── parse_excel.py       # Excel (.xlsx) → plain text
│   ├── parse_txt.py         # TXT → plain text
│   ├── parse_word.py        # Word (.docx) → plain text
│   ├── parse_powerpoint.py  # PowerPoint (.pptx) → plain text
│   └── __init__.py
│
├── embedder/                # Embedding model logic
│   ├── embedder.py          # Wraps sentence-transformers
│   └── model_cache/         # Local cache for transformer models
│
├── utils/                   # Utilities: search, storage, path
│   ├── file_utils.py        # File type checking, path handling
│   ├── search.py            # FAISS search logic (top-k retrieval)
│   └── store.py             # Save to db.json + update index
│
├── uploads/                 # Uploaded source files (.md, .pdf, .xlsx, etc.)
│   └── ...                  # Your personal notes & files
│
└── README.md                # Project overview & usage
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd ai-memory-bank
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python app.py --help
   ```

## Usage

### Command Line Interface (CLI)

#### Add Files to Memory Bank

```bash
# Add a single file
python app.py add-file document.pdf

# Add all files from a directory
python app.py add-dir /path/to/documents

# Add directory without copying files to uploads
python app.py add-dir /path/to/documents --no-recursive
```

#### Search Your Knowledge Base

```bash
# Basic search
python app.py search "machine learning algorithms"

# Search with custom number of results
python app.py search "neural networks" --top-k 10
```

#### View Statistics

```bash
# Show memory bank statistics
python app.py stats
```

#### Clear Data

```bash
# Clear all data from memory bank
python app.py clear
```

### Web Interface (Frontend)

#### Quick Start with Frontend

```bash
# Start the complete system with web interface
python start_frontend.py
```

This will:
- Start the API server on http://localhost:8000
- Automatically open your browser to the web interface
- Provide a modern, user-friendly interface for all operations

#### Manual Frontend Start

```bash
# Start server on default port (8000)
python app.py serve

# Then visit http://localhost:8000 in your browser
```

### REST API

#### Start the API Server

```bash
# Start server on default port (8000)
python app.py serve

# Start with custom host and port
python app.py serve --host 0.0.0.0 --port 8080

# Start with auto-reload for development
python app.py serve --reload
```

#### API Endpoints

Once the server is running, you can access the interactive API documentation at `http://localhost:8000/docs`

**Upload a File**:
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"
```

**Search Content**:
```bash
curl -X POST "http://localhost:8000/search" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"query": "machine learning", "top_k": 5}'
```

**Store Text**:
```bash
curl -X POST "http://localhost:8000/store-text" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"text": "This is some important information to remember."}'
```

**Get Statistics**:
```bash
curl -X GET "http://localhost:8000/statistics"
```

## Supported File Formats

| Format | Extensions | Parser |
|--------|------------|--------|
| **PDF** | `.pdf` | PyPDF2 |
| **Markdown** | `.md` | markdown + custom |
| **Excel** | `.xlsx`, `.xls` | openpyxl |
| **Word** | `.docx`, `.doc` | python-docx |
| **PowerPoint** | `.pptx`, `.ppt` | python-pptx |
| **Text** | `.txt` | built-in |

## Configuration

Key configuration options in `config.py`:

- **Embedding Model**: `all-MiniLM-L6-v2` (fast and effective)
- **Chunk Size**: 1000 characters per chunk
- **Chunk Overlap**: 200 characters between chunks
- **Search Results**: 5 results by default
- **Similarity Threshold**: 0.3 minimum similarity score

## How It Works

1. **File Processing**: Files are parsed and split into chunks while preserving metadata
2. **Embedding Generation**: Text chunks are converted to vector embeddings using sentence-transformers
3. **Indexing**: Embeddings are stored in a FAISS vector index for fast similarity search
4. **Search**: Queries are embedded and matched against stored vectors using cosine similarity
5. **Retrieval**: Most similar chunks are returned with relevance scores

## Performance Considerations

- **First Run**: The embedding model will be downloaded (~90MB) on first use
- **Large Files**: Files are automatically chunked to maintain search quality
- **Memory Usage**: FAISS index is loaded into memory for fast search
- **Storage**: All data is stored locally in JSON format

## Troubleshooting

### Common Issues

1. **Model Download Fails**:
   - Check internet connection
   - Try running with `--verbose` flag for more details

2. **Memory Issues**:
   - Reduce `BATCH_SIZE` in config.py
   - Process files in smaller batches

3. **File Parsing Errors**:
   - Check file format support
   - Ensure files are not corrupted
   - Try with different encoding

### Logs

Logs are written to `ai_memory_bank.log` and console output. Set `LOG_LEVEL` in config.py to control verbosity.

## Development

### Adding New File Formats

1. Create a new parser in the `parser/` directory
2. Add the file type to `SUPPORTED_EXTENSIONS` in `config.py`
3. Update the parser registry in `parser/__init__.py`

### Testing

```bash
# Run basic functionality test
python -c "
from app import add_file_cli, search_cli
# Test with a sample file
"

# Check system status
python app.py stats
```

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Roadmap

- [ ] Web interface for easier file management
- [ ] Support for more file formats (HTML, RTF, etc.)
- [ ] Advanced search filters (by date, file type, etc.)
- [ ] Export/import functionality
- [ ] Multi-language support
- [ ] Cloud storage integration
- [ ] Collaborative features

---

**Happy knowledge management!** 🧠📚 