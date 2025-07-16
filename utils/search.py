import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import faiss
import config
from utils.store import load_database, load_faiss_index
from embedder.embedder import embedder

def search_similar_chunks(
    query: str,
    top_k: Optional[int] = None,
    similarity_threshold: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Search for similar chunks using FAISS.
    
    Args:
        query: Search query
        top_k: Number of results to return
        similarity_threshold: Minimum similarity score
        
    Returns:
        List of search results with chunk data and scores
    """
    if top_k is None:
        top_k = config.DEFAULT_TOP_K
    if similarity_threshold is None:
        similarity_threshold = config.MIN_SIMILARITY_THRESHOLD
    
    # Load database and index
    database = load_database()
    index = load_faiss_index()
    
    if index is None or index.ntotal == 0:
        return []
    
    # Generate query embedding
    query_embedding = embedder.embed_text(query)
    
    # Normalize for cosine similarity
    query_embedding = query_embedding / np.linalg.norm(query_embedding)
    
    # Search in FAISS index
    scores, indices = index.search(query_embedding.reshape(1, -1), top_k * 2)  # Get more results to filter
    
    results = []
    chunk_ids = list(database["chunks"].keys())
    
    for score, idx in zip(scores[0], indices[0]):
        if idx >= len(chunk_ids) or score < similarity_threshold:
            continue
            
        chunk_id = chunk_ids[idx]
        chunk_data = database["chunks"][chunk_id]
        document_data = database["documents"][chunk_data["document_id"]]
        
        result = {
            "chunk_id": chunk_id,
            "document_id": chunk_data["document_id"],
            "text": chunk_data["text"],
            "score": float(score),
            "document_info": {
                "file_path": document_data["file_path"],
                "file_type": document_data["file_type"],
                "created_at": document_data["created_at"]
            },
            "chunk_index": chunk_data["chunk_index"]
        }
        
        results.append(result)
        
        if len(results) >= top_k:
            break
    
    return results

def search_documents(query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Search documents and aggregate chunk scores.
    
    Args:
        query: Search query
        top_k: Number of documents to return
        
    Returns:
        List of document results with aggregated scores
    """
    if top_k is None:
        top_k = config.DEFAULT_TOP_K
    
    chunk_results = search_similar_chunks(query, top_k * 3)  # Get more chunks
    
    # Aggregate scores by document
    document_scores = {}
    for result in chunk_results:
        doc_id = result["document_id"]
        score = result["score"]
        
        if doc_id not in document_scores:
            document_scores[doc_id] = {
                "max_score": score,
                "avg_score": score,
                "total_score": score,
                "chunk_count": 1,
                "document_info": result["document_info"],
                "best_chunk": result["text"]
            }
        else:
            doc_score = document_scores[doc_id]
            doc_score["max_score"] = max(doc_score["max_score"], score)
            doc_score["total_score"] += score
            doc_score["chunk_count"] += 1
            doc_score["avg_score"] = doc_score["total_score"] / doc_score["chunk_count"]
            
            # Keep the best chunk text
            if score > document_scores[doc_id]["max_score"]:
                document_scores[doc_id]["best_chunk"] = result["text"]
    
    # Sort by max score and return top_k
    sorted_docs = sorted(
        document_scores.items(),
        key=lambda x: x[1]["max_score"],
        reverse=True
    )[:top_k]
    
    results = []
    for doc_id, doc_data in sorted_docs:
        result = {
            "document_id": doc_id,
            "max_score": doc_data["max_score"],
            "avg_score": doc_data["avg_score"],
            "chunk_count": doc_data["chunk_count"],
            "document_info": doc_data["document_info"],
            "best_chunk": doc_data["best_chunk"]
        }
        results.append(result)
    
    return results

def get_document_chunks(document_id: str) -> List[Dict[str, Any]]:
    """
    Get all chunks for a specific document.
    
    Args:
        document_id: Document ID
        
    Returns:
        List of chunks for the document
    """
    database = load_database()
    
    chunks = []
    for chunk_id, chunk_data in database["chunks"].items():
        if chunk_data["document_id"] == document_id:
            chunks.append(chunk_data)
    
    # Sort by chunk index
    chunks.sort(key=lambda x: x["chunk_index"])
    
    return chunks

def get_chunk_context(chunk_id: str, context_size: int = 2) -> Dict[str, Any]:
    """
    Get a chunk with surrounding context chunks.
    
    Args:
        chunk_id: Chunk ID
        context_size: Number of chunks before and after to include
        
    Returns:
        Dictionary with chunk and context
    """
    database = load_database()
    
    if chunk_id not in database["chunks"]:
        return {}
    
    chunk_data = database["chunks"][chunk_id]
    document_id = chunk_data["document_id"]
    chunk_index = chunk_data["chunk_index"]
    
    # Get all chunks for the document
    document_chunks = get_document_chunks(document_id)
    
    # Find context chunks
    start_idx = max(0, chunk_index - context_size)
    end_idx = min(len(document_chunks), chunk_index + context_size + 1)
    
    context_chunks = document_chunks[start_idx:end_idx]
    
    return {
        "target_chunk": chunk_data,
        "context_chunks": context_chunks,
        "document_info": database["documents"][document_id]
    } 