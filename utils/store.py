"""
Storage utilities for AI Memory Bank
Handles saving parsed content to database and updating FAISS index
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from config import DB_FILE, MEMORY_DIR
from utils.search import get_search
from utils.file_utils import get_file_info

logger = logging.getLogger(__name__)

class MemoryStore:
    """Storage manager for the memory bank"""
    
    def __init__(self, db_file: Optional[Path] = None):
        """
        Initialize the storage manager
        
        Args:
            db_file: Path to the database file
        """
        self.db_file = db_file or DB_FILE
        self.search = get_search()
        
        # Ensure memory directory exists
        self.db_file.parent.mkdir(exist_ok=True)
    
    def store_file_content(self, file_path: Path, parsed_content: List[Dict[str, Any]]) -> bool:
        """
        Store parsed content from a file
        
        Args:
            file_path: Path to the source file
            parsed_content: List of parsed content chunks with metadata
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not parsed_content:
                logger.warning(f"No content to store for {file_path}")
                return False
            
            # Add file information to metadata
            file_info = get_file_info(file_path)
            timestamp = datetime.now().isoformat()
            
            # Enhance metadata for each chunk
            enhanced_content = []
            for chunk in parsed_content:
                enhanced_chunk = {
                    "content": chunk["content"],
                    "metadata": {
                        **chunk["metadata"],
                        "stored_at": timestamp,
                        "file_info": file_info
                    }
                }
                enhanced_content.append(enhanced_chunk)
            
            # Add to search index
            success = self.search.add_entries(enhanced_content)
            
            if success:
                logger.info(f"Stored {len(enhanced_content)} chunks from {file_path}")
            else:
                logger.error(f"Failed to store content from {file_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store file content for {file_path}: {e}")
            return False
    
    def store_text_content(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store raw text content with metadata
        
        Args:
            text: Text content to store
            metadata: Optional metadata dictionary
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not text or not text.strip():
                logger.warning("No text content to store")
                return False
            
            # Create entry
            entry = {
                "content": text.strip(),
                "metadata": {
                    **(metadata or {}),
                    "stored_at": datetime.now().isoformat(),
                    "source": "manual_input"
                }
            }
            
            # Add to search index
            success = self.search.add_entries([entry])
            
            if success:
                logger.info("Stored text content successfully")
            else:
                logger.error("Failed to store text content")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store text content: {e}")
            return False
    
    def get_entries_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Get all entries for a specific file
        
        Args:
            file_path: Path of the file
        
        Returns:
            List of entries for the file
        """
        try:
            entries = []
            for entry in self.search.data:
                if entry.get("metadata", {}).get("file_path") == file_path:
                    entries.append(entry)
            
            logger.info(f"Found {len(entries)} entries for file: {file_path}")
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get entries for file {file_path}: {e}")
            return []
    
    def get_entries_by_type(self, file_type: str) -> List[Dict[str, Any]]:
        """
        Get all entries for a specific file type
        
        Args:
            file_type: Type of file (e.g., 'pdf', 'markdown', 'excel')
        
        Returns:
            List of entries for the file type
        """
        try:
            entries = []
            for entry in self.search.data:
                if entry.get("metadata", {}).get("file_type") == file_type:
                    entries.append(entry)
            
            logger.info(f"Found {len(entries)} entries for file type: {file_type}")
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get entries for file type {file_type}: {e}")
            return []
    
    def remove_file_entries(self, file_path: str) -> int:
        """
        Remove all entries for a specific file
        
        Args:
            file_path: Path of the file to remove
        
        Returns:
            Number of entries removed
        """
        try:
            removed_count = self.search.remove_entries_by_file(file_path)
            logger.info(f"Removed {removed_count} entries for file: {file_path}")
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to remove entries for file {file_path}: {e}")
            return 0
    
    def get_all_entries(self) -> List[Dict[str, Any]]:
        """
        Get all entries in the memory bank
        
        Returns:
            List of all entries
        """
        return self.search.data.copy()
    
    def get_entry_count(self) -> int:
        """
        Get the total number of entries
        
        Returns:
            Number of entries
        """
        return len(self.search.data)
    
    def export_data(self, export_path: Path) -> bool:
        """
        Export all data to a JSON file
        
        Args:
            export_path: Path to export the data to
        
        Returns:
            True if successful, False otherwise
        """
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "total_entries": len(self.search.data),
                "entries": self.search.data
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(self.search.data)} entries to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export data to {export_path}: {e}")
            return False
    
    def import_data(self, import_path: Path, clear_existing: bool = False) -> bool:
        """
        Import data from a JSON file
        
        Args:
            import_path: Path to the import file
            clear_existing: Whether to clear existing data before import
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            entries = import_data.get("entries", [])
            
            if not entries:
                logger.warning("No entries found in import file")
                return False
            
            if clear_existing:
                self.search.clear()
            
            # Add entries
            success = self.search.add_entries(entries)
            
            if success:
                logger.info(f"Imported {len(entries)} entries from {import_path}")
            else:
                logger.error(f"Failed to import entries from {import_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to import data from {import_path}: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the stored data
        
        Returns:
            Dictionary with statistics
        """
        try:
            stats = self.search.get_statistics()
            
            # Add additional statistics
            if self.search.data:
                # File statistics
                files = set()
                file_types = {}
                total_content_length = 0
                
                for entry in self.search.data:
                    metadata = entry.get("metadata", {})
                    file_path = metadata.get("file_path", "unknown")
                    file_type = metadata.get("file_type", "unknown")
                    content = entry.get("content", "")
                    
                    files.add(file_path)
                    file_types[file_type] = file_types.get(file_type, 0) + 1
                    total_content_length += len(content)
                
                stats.update({
                    "unique_files": len(files),
                    "file_types": file_types,
                    "average_content_length": total_content_length / len(self.search.data) if self.search.data else 0,
                    "total_content_length": total_content_length
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}
    
    def backup_database(self, backup_path: Optional[Path] = None) -> bool:
        """
        Create a backup of the database
        
        Args:
            backup_path: Path for the backup file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.db_file.parent / f"backup_{timestamp}.json"
            
            return self.export_data(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def cleanup_old_entries(self, days_old: int = 30) -> int:
        """
        Remove entries older than specified days
        
        Args:
            days_old: Remove entries older than this many days
        
        Returns:
            Number of entries removed
        """
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cutoff_iso = cutoff_date.isoformat()
            
            indices_to_remove = []
            for i, entry in enumerate(self.search.data):
                stored_at = entry.get("metadata", {}).get("stored_at", "")
                if stored_at and stored_at < cutoff_iso:
                    indices_to_remove.append(i)
            
            if not indices_to_remove:
                logger.info("No old entries found to remove")
                return 0
            
            # Remove entries (in reverse order to maintain indices)
            for i in reversed(indices_to_remove):
                del self.search.data[i]
            
            # Rebuild index
            self.search._rebuild_index()
            
            logger.info(f"Removed {len(indices_to_remove)} old entries")
            return len(indices_to_remove)
            
        except Exception as e:
            logger.error(f"Failed to cleanup old entries: {e}")
            return 0

# Global store instance
_store_instance = None

def get_store() -> MemoryStore:
    """Get or create the global store instance"""
    global _store_instance
    if _store_instance is None:
        _store_instance = MemoryStore()
    return _store_instance

def reset_store():
    """Reset the global store instance (useful for testing)"""
    global _store_instance
    _store_instance = None 