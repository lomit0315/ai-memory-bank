from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from utils.search import search_similar_chunks
from utils.store import load_database
from logging_config import get_logger

logger = get_logger('advanced_search')

class AdvancedSearch:
    """Advanced search functionality with filters, sorting, and faceted search."""
    
    def __init__(self):
        self.database = None
        self._load_database()
    
    def _load_database(self):
        """Load the database for filtering operations."""
        self.database = load_database()
    
    def search_with_filters(
        self,
        query: str,
        file_types: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_chunk_length: Optional[int] = None,
        max_chunk_length: Optional[int] = None,
        sort_by: str = "relevance",
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Perform advanced search with multiple filters.
        
        Args:
            query: Search query
            file_types: List of file types to include (e.g., ['pdf', 'markdown'])
            date_from: Start date filter (ISO format)
            date_to: End date filter (ISO format)
            min_chunk_length: Minimum chunk length in characters
            max_chunk_length: Maximum chunk length in characters
            sort_by: Sort method ('relevance', 'date', 'length', 'file_type')
            top_k: Maximum number of results
            
        Returns:
            Enhanced search results with metadata
        """
        logger.info(f"Advanced search: '{query}' with filters")
        
        # Get initial results from semantic search
        initial_results = search_similar_chunks(query, top_k * 3)  # Get more for filtering
        
        # Apply filters
        filtered_results = self._apply_filters(
            initial_results,
            file_types=file_types,
            date_from=date_from,
            date_to=date_to,
            min_chunk_length=min_chunk_length,
            max_chunk_length=max_chunk_length
        )
        
        # Apply sorting
        sorted_results = self._apply_sorting(filtered_results, sort_by)
        
        # Limit results
        final_results = sorted_results[:top_k]
        
        # Add additional metadata
        enriched_results = self._enrich_results(final_results)
        
        # Generate faceted search data
        facets = self._generate_facets(filtered_results)
        
        return {
            "results": enriched_results,
            "total_results": len(filtered_results),
            "query": query,
            "filters_applied": self._get_applied_filters(
                file_types, date_from, date_to, min_chunk_length, max_chunk_length
            ),
            "sort_by": sort_by,
            "facets": facets
        }
    
    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        file_types: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_chunk_length: Optional[int] = None,
        max_chunk_length: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Apply various filters to search results."""
        filtered = results.copy()
        
        # File type filter
        if file_types:
            filtered = [
                r for r in filtered 
                if r["document_info"]["file_type"] in file_types
            ]
        
        # Date range filter
        if date_from or date_to:
            filtered = self._filter_by_date(filtered, date_from, date_to)
        
        # Chunk length filters
        if min_chunk_length is not None:
            filtered = [r for r in filtered if len(r["text"]) >= min_chunk_length]
        
        if max_chunk_length is not None:
            filtered = [r for r in filtered if len(r["text"]) <= max_chunk_length]
        
        return filtered
    
    def _filter_by_date(
        self,
        results: List[Dict[str, Any]],
        date_from: Optional[str],
        date_to: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Filter results by creation date."""
        filtered = []
        
        for result in results:
            doc_date_str = result["document_info"]["created_at"]
            doc_date = datetime.fromisoformat(doc_date_str.replace('Z', '+00:00'))
            
            include = True
            
            if date_from:
                from_date = datetime.fromisoformat(date_from)
                if doc_date < from_date:
                    include = False
            
            if date_to and include:
                to_date = datetime.fromisoformat(date_to)
                if doc_date > to_date:
                    include = False
            
            if include:
                filtered.append(result)
        
        return filtered
    
    def _apply_sorting(
        self,
        results: List[Dict[str, Any]],
        sort_by: str
    ) -> List[Dict[str, Any]]:
        """Apply sorting to results."""
        if sort_by == "relevance":
            # Already sorted by relevance score
            return results
        elif sort_by == "date":
            return sorted(
                results,
                key=lambda x: x["document_info"]["created_at"],
                reverse=True
            )
        elif sort_by == "length":
            return sorted(
                results,
                key=lambda x: len(x["text"]),
                reverse=True
            )
        elif sort_by == "file_type":
            return sorted(
                results,
                key=lambda x: x["document_info"]["file_type"]
            )
        else:
            logger.warning(f"Unknown sort method: {sort_by}")
            return results
    
    def _enrich_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add additional metadata to results."""
        enriched = []
        
        for result in results:
            enriched_result = result.copy()
            
            # Add word count
            enriched_result["word_count"] = len(result["text"].split())
            
            # Add file size if available
            doc_id = result["document_id"]
            if self.database and doc_id in self.database["documents"]:
                doc_data = self.database["documents"][doc_id]
                enriched_result["document_info"]["file_size"] = doc_data.get("file_size", 0)
                enriched_result["document_info"]["total_chunks"] = doc_data.get("chunk_count", 0)
            
            # Add contextual snippets (surrounding chunks)
            enriched_result["context_snippets"] = self._get_context_snippets(result)
            
            enriched.append(enriched_result)
        
        return enriched
    
    def _get_context_snippets(self, result: Dict[str, Any]) -> List[str]:
        """Get snippets from surrounding chunks for context."""
        doc_id = result["document_id"]
        chunk_index = result["chunk_index"]
        
        snippets = []
        
        # Find adjacent chunks
        if not self.database:
            return []
        
        for chunk_id, chunk_data in self.database["chunks"].items():
            if (chunk_data["document_id"] == doc_id and 
                abs(chunk_data["chunk_index"] - chunk_index) <= 2 and
                chunk_data["chunk_index"] != chunk_index):
                
                snippet = chunk_data["text"][:100] + "..." if len(chunk_data["text"]) > 100 else chunk_data["text"]
                snippets.append({
                    "text": snippet,
                    "index": chunk_data["chunk_index"],
                    "relative_position": chunk_data["chunk_index"] - chunk_index
                })
        
        # Sort by index
        snippets.sort(key=lambda x: x["index"])
        
        return snippets[:3]  # Return up to 3 context snippets
    
    def _generate_facets(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate faceted search data for UI filters."""
        if not results:
            return {}
        
        file_types = {}
        date_ranges = {}
        length_ranges = {"0-100": 0, "100-500": 0, "500-1000": 0, "1000+": 0}
        
        for result in results:
            # File type facets
            file_type = result["document_info"]["file_type"]
            file_types[file_type] = file_types.get(file_type, 0) + 1
            
            # Date facets (by month)
            date_str = result["document_info"]["created_at"]
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            month_key = date_obj.strftime("%Y-%m")
            date_ranges[month_key] = date_ranges.get(month_key, 0) + 1
            
            # Length facets
            text_length = len(result["text"])
            if text_length < 100:
                length_ranges["0-100"] += 1
            elif text_length < 500:
                length_ranges["100-500"] += 1
            elif text_length < 1000:
                length_ranges["500-1000"] += 1
            else:
                length_ranges["1000+"] += 1
        
        return {
            "file_types": file_types,
            "date_ranges": dict(sorted(date_ranges.items(), reverse=True)),
            "length_ranges": length_ranges
        }
    
    def _get_applied_filters(
        self,
        file_types: Optional[List[str]],
        date_from: Optional[str],
        date_to: Optional[str],
        min_chunk_length: Optional[int],
        max_chunk_length: Optional[int]
    ) -> Dict[str, Any]:
        """Get summary of applied filters."""
        filters = {}
        
        if file_types:
            filters["file_types"] = file_types
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        if min_chunk_length is not None:
            filters["min_chunk_length"] = min_chunk_length
        if max_chunk_length is not None:
            filters["max_chunk_length"] = max_chunk_length
        
        return filters
    
    def get_document_recommendations(
        self,
        document_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Get document recommendations based on similarity."""
        if not self.database or document_id not in self.database["documents"]:
            return []
        
        # Get the document content
        doc_data = self.database["documents"][document_id]
        doc_content = doc_data["content"]
        
        # Use the document content as a query to find similar documents
        similar_chunks = search_similar_chunks(doc_content[:1000], top_k * 3)
        
        # Group by document and exclude the source document
        doc_scores = {}
        for chunk in similar_chunks:
            chunk_doc_id = chunk["document_id"]
            if chunk_doc_id != document_id:
                if chunk_doc_id not in doc_scores:
                    doc_scores[chunk_doc_id] = {
                        "max_score": chunk["score"],
                        "doc_info": chunk["document_info"]
                    }
                else:
                    doc_scores[chunk_doc_id]["max_score"] = max(
                        doc_scores[chunk_doc_id]["max_score"],
                        chunk["score"]
                    )
        
        # Sort by score and return top recommendations
        recommendations = sorted(
            doc_scores.items(),
            key=lambda x: x[1]["max_score"],
            reverse=True
        )[:top_k]
        
        return [
            {
                "document_id": doc_id,
                "similarity_score": data["max_score"],
                "document_info": data["doc_info"]
            }
            for doc_id, data in recommendations
        ]

# Global advanced search instance
advanced_search = AdvancedSearch() 