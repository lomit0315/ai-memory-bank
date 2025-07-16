"""
Search utilities for AI Memory Bank
Handles FAISS vector search and similarity matching
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
from pathlib import Path
import faiss
from config import DEFAULT_TOP_K, SIMILARITY_THRESHOLD, EMBEDDING_DIMENSION, DB_FILE
from embedder.embedder import get_embedder

logger = logging.getLogger(__name__)

class MemorySearch:
    """FAISS-based search for the memory bank"""
    
    def __init__(self, db_file: Optional[Path] = None, index_file: Optional[Path] = None):
        """
        Initialize the search system
        
        Args:
            db_file: Path to the database JSON file
            index_file: Path to the FAISS index file
        """
        self.db_file = db_file or DB_FILE
        self.index_file = index_file or self.db_file.parent / "faiss.index"
        self.embedder = get_embedder()
        self.index = None
        self.data = []
        self.is_loaded = False
        
        self._load_data()
        self._load_index()
    
    def _load_data(self):
        """Load data from the database file"""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded {len(self.data)} entries from database")
            else:
                logger.info("Database file not found, starting with empty database")
                self.data = []
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            self.data = []
    
    def _load_index(self):
        """Load or create the FAISS index"""
        try:
            if self.index_file.exists() and len(self.data) > 0:
                # Load existing index
                self.index = faiss.read_index(str(self.index_file))
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                # Create new index
                dimension = self.embedder.get_embedding_dimension()
                self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
                logger.info(f"Created new FAISS index with dimension {dimension}")
            
            self.is_loaded = True
            
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            # Create a new index as fallback
            dimension = self.embedder.get_embedding_dimension()
            self.index = faiss.IndexFlatIP(dimension)
            self.is_loaded = True
    
    def _save_index(self):
        """Save the FAISS index to disk"""
        try:
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_file))
                logger.debug("FAISS index saved")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
    
    def _save_data(self):
        """Save data to the database file"""
        try:
            self.db_file.parent.mkdir(exist_ok=True)
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.debug("Database saved")
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
    
    def add_entries(self, entries: List[Dict[str, Any]]) -> bool:
        """
        Add new entries to the memory bank
        
        Args:
            entries: List of entry dictionaries with 'content' and 'metadata' keys
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_loaded:
            logger.error("Search system not loaded")
            return False
        
        try:
            # Extract content for embedding
            contents = [entry['content'] for entry in entries if entry.get('content')]
            
            if not contents:
                logger.warning("No valid content found in entries")
                return False
            
            # Generate embeddings
            embeddings = self.embedder.encode(contents)
            
            if len(embeddings) == 0:
                logger.error("Failed to generate embeddings")
                return False
            
            # Add to FAISS index
            self.index.add(embeddings.astype('float32'))
            
            # Add to data
            self.data.extend(entries)
            
            # Save both index and data
            self._save_index()
            self._save_data()
            
            logger.info(f"Added {len(entries)} entries to memory bank")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add entries: {e}")
            return False
    
    def search(self, query: str, top_k: Optional[int] = None, 
               similarity_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search for similar content
        
        Args:
            query: Search query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of search results with content, metadata, and similarity score
        """
        if not self.is_loaded or self.index is None or len(self.data) == 0:
            logger.warning("Search system not ready or no data available")
            return []
        
        top_k = top_k or DEFAULT_TOP_K
        similarity_threshold = similarity_threshold or SIMILARITY_THRESHOLD
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode_single(query)
            
            if query_embedding is None or len(query_embedding) == 0:
                logger.error("Failed to generate query embedding")
                return []
            
            # Search the index
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            similarities, indices = self.index.search(query_embedding, min(top_k, len(self.data)))
            
            # Format results
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx < len(self.data) and similarity >= similarity_threshold:
                    result = {
                        "content": self.data[idx]["content"],
                        "metadata": self.data[idx]["metadata"],
                        "similarity_score": float(similarity),
                        "rank": i + 1
                    }
                    results.append(result)
            
            logger.info(f"Search returned {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def batch_search(self, queries: List[str], top_k: Optional[int] = None) -> List[List[Dict[str, Any]]]:
        """
        Perform batch search for multiple queries
        
        Args:
            queries: List of search queries
            top_k: Number of results per query
        
        Returns:
            List of search result lists
        """
        if not queries:
            return []
        
        results = []
        for query in queries:
            query_results = self.search(query, top_k=top_k)
            results.append(query_results)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the memory bank"""
        try:
            total_entries = len(self.data)
            total_vectors = self.index.ntotal if self.index else 0
            
            # Count by file type
            file_types = {}
            for entry in self.data:
                file_type = entry.get("metadata", {}).get("file_type", "unknown")
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            # Calculate total content size
            total_content_size = sum(len(entry.get("content", "")) for entry in self.data)
            
            return {
                "total_entries": total_entries,
                "total_vectors": total_vectors,
                "total_content_size": total_content_size,
                "file_types": file_types,
                "index_dimension": self.index.d if self.index else 0,
                "is_loaded": self.is_loaded
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}
    
    def clear(self) -> bool:
        """Clear all data from the memory bank"""
        try:
            # Clear data
            self.data = []
            
            # Recreate index
            dimension = self.embedder.get_embedding_dimension()
            self.index = faiss.IndexFlatIP(dimension)
            
            # Save empty state
            self._save_index()
            self._save_data()
            
            logger.info("Memory bank cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear memory bank: {e}")
            return False
    
    def remove_entries_by_file(self, file_path: str) -> int:
        """
        Remove all entries from a specific file
        
        Args:
            file_path: Path of the file to remove
        
        Returns:
            Number of entries removed
        """
        try:
            # Find entries to remove
            indices_to_remove = []
            for i, entry in enumerate(self.data):
                if entry.get("metadata", {}).get("file_path") == file_path:
                    indices_to_remove.append(i)
            
            if not indices_to_remove:
                logger.info(f"No entries found for file: {file_path}")
                return 0
            
            # Remove entries (in reverse order to maintain indices)
            for i in reversed(indices_to_remove):
                del self.data[i]
            
            # Rebuild index
            self._rebuild_index()
            
            logger.info(f"Removed {len(indices_to_remove)} entries for file: {file_path}")
            return len(indices_to_remove)
            
        except Exception as e:
            logger.error(f"Failed to remove entries for file {file_path}: {e}")
            return 0
    
    def _rebuild_index(self):
        """Rebuild the FAISS index from current data"""
        try:
            # Extract content for embedding
            contents = [entry['content'] for entry in self.data if entry.get('content')]
            
            if not contents:
                # Create empty index
                dimension = self.embedder.get_embedding_dimension()
                self.index = faiss.IndexFlatIP(dimension)
            else:
                # Generate embeddings for all content
                embeddings = self.embedder.encode(contents)
                
                # Create new index
                dimension = embeddings.shape[1]
                self.index = faiss.IndexFlatIP(dimension)
                self.index.add(embeddings.astype('float32'))
            
            # Save the rebuilt index
            self._save_index()
            self._save_data()
            
            logger.info(f"Rebuilt FAISS index with {len(contents)} vectors")
            
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")

# Global search instance
_search_instance = None

def get_search() -> MemorySearch:
    """Get or create the global search instance"""
    global _search_instance
    if _search_instance is None:
        _search_instance = MemorySearch()
    return _search_instance

def reset_search():
    """Reset the global search instance (useful for testing)"""
    global _search_instance
    _search_instance = None 