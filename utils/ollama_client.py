import httpx
import json
from typing import Dict, List, Any, Optional, AsyncGenerator
import config
from logging_config import get_logger

logger = get_logger('ollama')

class OllamaClient:
    """Client for interacting with Ollama local models."""
    
    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL
        self.timeout = config.OLLAMA_TIMEOUT
        self.default_model = config.OLLAMA_MODEL
    
    async def is_available(self) -> bool:
        """Check if Ollama is running and available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from Ollama."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return data.get("models", [])
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
    
    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate response from Ollama model."""
        if not model:
            model = self.default_model
        
        if not temperature:
            temperature = config.OLLAMA_TEMPERATURE
        
        if not max_tokens:
            max_tokens = config.OLLAMA_MAX_TOKENS
        
        # Prepare the request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if system:
            payload["system"] = system
        
        if context:
            # Combine system prompt with context
            full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
            payload["prompt"] = full_prompt
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                
                if stream:
                    # For streaming, we'll implement this later
                    data = response.json()
                else:
                    data = response.json()
                    return {
                        "response": data.get("response", ""),
                        "model": model,
                        "done": data.get("done", True),
                        "total_duration": data.get("total_duration", 0),
                        "load_duration": data.get("load_duration", 0),
                        "prompt_eval_count": data.get("prompt_eval_count", 0),
                        "eval_count": data.get("eval_count", 0)
                    }
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": f"Error generating response: {str(e)}",
                "error": True
            }
    
    async def chat_with_context(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a response using search results as context."""
        if not system_prompt:
            system_prompt = config.QA_SYSTEM_PROMPT
        
        # Prepare context from search results
        context_text = self._prepare_context(context_chunks)
        
        # Create the full prompt
        full_prompt = f"""System: {system_prompt}

Context from knowledge base:
{context_text}

Question: {question}

Answer:"""
        
        logger.info(f"Generating answer for: '{question}' using {len(context_chunks)} context chunks")
        
        start_time = time.time()
        result = await self.generate_response(
            prompt=full_prompt,
            model=model
        )
        response_time = time.time() - start_time
        
        # Add metadata
        result.update({
            "question": question,
            "context_chunks_count": len(context_chunks),
            "response_time": response_time,
            "sources": [chunk["document_info"]["file_path"] for chunk in context_chunks]
        })
        
        return result
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context text from search result chunks."""
        context_parts = []
        
        for i, chunk in enumerate(chunks[:config.QA_CONTEXT_CHUNKS]):
            file_path = chunk["document_info"]["file_path"]
            text = chunk["text"]
            score = chunk.get("score", 0)
            
            context_parts.append(
                f"[Document: {file_path} | Relevance: {score:.3f}]\n{text}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        # Truncate if too long
        if len(context) > config.QA_MAX_CONTEXT_LENGTH:
            context = context[:config.QA_MAX_CONTEXT_LENGTH] + "\n[Context truncated...]"
        
        return context
    
    async def ask_question(
        self,
        question: str,
        search_results: List[Dict[str, Any]],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ask a question based on search results."""
        if not search_results:
            return {
                "response": "I don't have any relevant information in the knowledge base to answer your question.",
                "question": question,
                "context_chunks_count": 0,
                "sources": []
            }
        
        return await self.chat_with_context(
            question=question,
            context_chunks=search_results,
            model=model
        )
    
    async def summarize_document(
        self,
        document_content: str,
        model: Optional[str] = None,
        max_length: int = 500
    ) -> Dict[str, Any]:
        """Generate a summary of a document."""
        prompt = f"""Please provide a concise summary of the following document in about {max_length} words:

{document_content[:4000]}  # Limit input length

Summary:"""
        
        return await self.generate_response(
            prompt=prompt,
            model=model,
            system="You are a helpful assistant that creates clear and informative summaries."
        )

# Global client instance
ollama_client = OllamaClient()

# Import time for response timing
import time 