#!/usr/bin/env python3
"""
AI Memory Bank Demo Script
Demonstrates the functionality of the AI Memory Bank system.
"""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def create_sample_files():
    """Create sample files for demonstration."""
    
    sample_files = {
        "sample_notes.md": """# AI and Machine Learning Notes

## Deep Learning
Deep learning is a subset of machine learning that uses neural networks with multiple layers. Key concepts include:

- **Neural Networks**: Computational models inspired by biological neural networks
- **Backpropagation**: Algorithm for training neural networks
- **Gradient Descent**: Optimization algorithm for minimizing loss functions

## Natural Language Processing
NLP focuses on the interaction between computers and human language:

- **Tokenization**: Breaking text into smaller units (words, sentences)
- **Word Embeddings**: Dense vector representations of words
- **Transformers**: Architecture that revolutionized NLP (BERT, GPT)

## Computer Vision
Computer vision enables machines to interpret visual information:

- **Convolutional Neural Networks (CNNs)**: Specialized for image processing
- **Object Detection**: Identifying and locating objects in images
- **Image Segmentation**: Pixel-level classification of images
""",
        
        "python_tips.txt": """Python Programming Tips and Tricks

1. List Comprehensions
   - More efficient than traditional loops
   - Example: [x**2 for x in range(10)]

2. F-strings for String Formatting
   - Modern and readable string formatting
   - Example: f"Hello, {name}!"

3. Context Managers
   - Automatic resource management
   - Example: with open('file.txt') as f: content = f.read()

4. Virtual Environments
   - Isolate project dependencies
   - Example: python -m venv myenv

5. Type Hints
   - Improve code readability and IDE support
   - Example: def greet(name: str) -> str: return f"Hello, {name}"

6. Decorators
   - Modify function behavior without changing the function
   - Common uses: logging, timing, authentication

7. Lambda Functions
   - Anonymous functions for simple operations
   - Example: sorted(data, key=lambda x: x['age'])
""",
        
        "project_ideas.md": """# Interesting Project Ideas

## Web Applications
1. **Personal Knowledge Base** - Search and organize your notes and documents
2. **Habit Tracker** - Track daily habits with visualization
3. **Recipe Manager** - Store and search cooking recipes
4. **Book Recommendation System** - AI-powered book suggestions

## Data Science Projects
1. **Stock Price Predictor** - Predict stock prices using historical data
2. **Sentiment Analysis Tool** - Analyze sentiment in social media posts
3. **Weather Pattern Analysis** - Analyze climate data and trends
4. **Customer Segmentation** - Group customers based on behavior

## Automation Scripts
1. **File Organizer** - Automatically organize downloads folder
2. **Backup Manager** - Automated backup system for important files
3. **Email Automation** - Send automated reports and reminders
4. **System Monitor** - Monitor system resources and send alerts

## Mobile Apps
1. **Expense Tracker** - Track personal expenses and budgets
2. **Language Learning** - Interactive language learning app
3. **Fitness Tracker** - Track workouts and progress
4. **Plant Care Reminder** - Remind users to water plants
"""
    }
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    print("📁 Creating sample files...")
    
    for filename, content in sample_files.items():
        file_path = uploads_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {file_path}")
    
    return list(sample_files.keys())

def demo_cli_functionality():
    """Demonstrate CLI functionality."""
    print("\n🔧 AI Memory Bank Demo")
    print("=" * 50)
    
    try:
        # Import the main modules
        from app import process_file
        from utils.search import search_similar_chunks
        from utils.store import get_database_stats
        
        # Create sample files
        sample_files = create_sample_files()
        
        print(f"\n📊 Processing {len(sample_files)} sample files...")
        
        # Process each sample file
        for filename in sample_files:
            file_path = Path("uploads") / filename
            try:
                result = process_file(str(file_path), copy_to_uploads=False)
                print(f"✅ Processed {filename}: {result['chunk_count']} chunks created")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
        
        print("\n📈 Database Statistics:")
        stats = get_database_stats()
        print(f"  📄 Documents: {stats['total_documents']}")
        print(f"  📝 Chunks: {stats['total_chunks']}")
        print(f"  💾 DB Size: {stats['database_size_mb']:.2f} MB")
        
        print("\n🔍 Demo Searches:")
        
        # Demo searches
        demo_queries = [
            "machine learning and neural networks",
            "Python programming tips",
            "web application projects",
            "deep learning concepts"
        ]
        
        for query in demo_queries:
            print(f"\n🔎 Searching: '{query}'")
            try:
                results = search_similar_chunks(query, top_k=3)
                if results:
                    for i, result in enumerate(results, 1):
                        score = result['score']
                        text_preview = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
                        file_path = result['document_info']['file_path']
                        print(f"  {i}. Score: {score:.3f} | File: {Path(file_path).name}")
                        print(f"     Preview: {text_preview}")
                else:
                    print("  No results found")
            except Exception as e:
                print(f"  ❌ Search error: {e}")
        
        print("\n✅ Demo completed successfully!")
        print("\n💡 Try the web interface:")
        print("   python start_frontend.py")
        print("\n💡 Or use the CLI:")
        print("   python app.py search 'your query here'")
        print("   python app.py stats")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies first:")
        print("  pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    demo_cli_functionality() 