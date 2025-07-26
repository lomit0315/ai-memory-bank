from typing import Dict, List, Any, Optional
import time
from utils.search import search_similar_chunks
from utils.ollama_client import ollama_client
from analytics.analytics import analytics
from logging_config import get_logger
import config

logger = get_logger('qa_system')

class QASystem:
    """Question Answering System that combines search and Ollama."""
    
    def __init__(self):
        self.ollama_enabled = config.OLLAMA_ENABLED
    
    async def answer_question(
        self,
        question: str,
        top_k: int = 5,
        model: Optional[str] = None,
        use_ollama: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question using the knowledge base and Ollama.
        
        Args:
            question: User's question
            top_k: Number of search results to use as context
            model: Ollama model to use (optional)
            use_ollama: Whether to use Ollama for generating answers
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        start_time = time.time()
        
        # Step 1: Search for relevant content
        logger.info(f"Searching for: '{question}'")
        search_results = search_similar_chunks(question, top_k)
        
        if not search_results:
            response = {
                "answer": "I couldn't find any relevant information in your knowledge base to answer this question.",
                "question": question,
                "search_results": [],
                "sources": [],
                "method": "search_only",
                "response_time": time.time() - start_time
            }
            
            # Record analytics
            analytics.record_search(question, 0, response["response_time"])
            return response
        
        # Step 2: Use Ollama to generate answer (if enabled)
        if use_ollama and self.ollama_enabled:
            ollama_available = await ollama_client.is_available()
            
            if ollama_available:
                try:
                    logger.info(f"Generating answer using Ollama model: {model or config.OLLAMA_MODEL}")
                    ollama_response = await ollama_client.ask_question(
                        question=question,
                        search_results=search_results,
                        model=model
                    )
                    
                    response = {
                        "answer": ollama_response["response"],
                        "question": question,
                        "search_results": search_results,
                        "sources": ollama_response.get("sources", []),
                        "method": "ollama_enhanced",
                        "model_used": model or config.OLLAMA_MODEL,
                        "response_time": time.time() - start_time,
                        "ollama_metadata": {
                            "context_chunks": ollama_response.get("context_chunks_count", 0),
                            "model_response_time": ollama_response.get("response_time", 0)
                        }
                    }
                    
                except Exception as e:
                    logger.error(f"Ollama error: {e}")
                    # Fallback to search-only response
                    response = self._create_search_only_response(question, search_results, start_time)
                    response["ollama_error"] = str(e)
            else:
                logger.warning("Ollama not available, falling back to search results")
                response = self._create_search_only_response(question, search_results, start_time)
        else:
            # Search-only response
            response = self._create_search_only_response(question, search_results, start_time)
        
        # Record analytics
        analytics.record_search(question, len(search_results), response["response_time"])
        
        return response
    
    def _create_search_only_response(
        self,
        question: str,
        search_results: List[Dict[str, Any]],
        start_time: float
    ) -> Dict[str, Any]:
        """Create a response based only on search results."""
        # Create a simple answer from top search results
        top_result = search_results[0] if search_results else None
        
        if top_result:
            answer = f"Based on the search results, here's the most relevant information:\n\n{top_result['text'][:500]}..."
            if len(top_result['text']) > 500:
                answer += f"\n\n[From: {top_result['document_info']['file_path']}]"
        else:
            answer = "No relevant information found in the knowledge base."
        
        return {
            "answer": answer,
            "question": question,
            "search_results": search_results,
            "sources": [r["document_info"]["file_path"] for r in search_results],
            "method": "search_only",
            "response_time": time.time() - start_time
        }
    
    async def get_available_models(self) -> List[str]:
        """Get list of available Ollama models."""
        if not self.ollama_enabled:
            return []
        
        try:
            models_data = await ollama_client.get_models()
            return [model["name"] for model in models_data]
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return config.AVAILABLE_OLLAMA_MODELS
    
    async def check_ollama_status(self) -> Dict[str, Any]:
        """Check Ollama service status."""
        if not self.ollama_enabled:
            return {"enabled": False, "available": False}
        
        available = await ollama_client.is_available()
        models = await self.get_available_models() if available else []
        
        return {
            "enabled": True,
            "available": available,
            "base_url": config.OLLAMA_BASE_URL,
            "default_model": config.OLLAMA_MODEL,
            "available_models": models
        }
    
    async def summarize_search_results(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a summary of search results."""
        if not search_results or not self.ollama_enabled:
            return {"summary": "No results to summarize."}
        
        # Combine search results into context
        context = "\n\n".join([
            f"From {result['document_info']['file_path']}:\n{result['text']}"
            for result in search_results[:3]  # Use top 3 results
        ])
        
        prompt = f"""Based on the search results for the query "{query}", provide a concise summary of the key information found:

{context}

Summary:"""
        
        try:
            response = await ollama_client.generate_response(
                prompt=prompt,
                model=model,
                system="You are a helpful assistant that creates clear summaries from search results."
            )
            
            return {
                "summary": response["response"],
                "query": query,
                "results_count": len(search_results),
                "model_used": model or config.OLLAMA_MODEL
            }
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {"summary": f"Error generating summary: {str(e)}"}

# Global QA system instance
qa_system = QASystem() 