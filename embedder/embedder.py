"""
Embedding model wrapper for AI Memory Bank
Uses sentence-transformers for generating vector embeddings
"""

import logging
import numpy as np
from typing import List, Union, Optional
from pathlib import Path
import torch
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, EMBEDDING_DIMENSION, MAX_SEQUENCE_LENGTH, MODEL_CACHE_DIR

logger = logging.getLogger(__name__)

class Embedder:
    """Wrapper for sentence-transformers embedding model"""
    
    def __init__(self, model_name: Optional[str] = None, cache_dir: Optional[Path] = None):
        """
        Initialize the embedder
        
        Args:
            model_name: Name of the sentence-transformers model to use
            cache_dir: Directory to cache the model
        """
        self.model_name = model_name or EMBEDDING_MODEL
        self.cache_dir = cache_dir or MODEL_CACHE_DIR
        self.model = None
        self.device = self._get_device()
        
        logger.info(f"Initializing embedder with model: {self.model_name}")
        logger.info(f"Using device: {self.device}")
        
        self._load_model()
    
    def _get_device(self) -> str:
        """Get the best available device for the model"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"  # Apple Silicon
        else:
            return "cpu"
    
    def _load_model(self):
        """Load the sentence-transformers model"""
        try:
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=str(self.cache_dir),
                device=self.device
            )
            
            # Verify the model loaded correctly
            test_embedding = self.model.encode("test", convert_to_numpy=True)
            logger.info(f"Model loaded successfully. Embedding dimension: {len(test_embedding)}")
            
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise
    
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode text(s) to embeddings
        
        Args:
            texts: Single text string or list of text strings
            batch_size: Batch size for processing multiple texts
        
        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            # Convert single text to list
            if isinstance(texts, str):
                texts = [texts]
            
            # Filter out empty texts
            valid_texts = [text for text in texts if text and text.strip()]
            
            if not valid_texts:
                logger.warning("No valid texts provided for encoding")
                return np.array([])
            
            # Encode texts
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=len(valid_texts) > 10
            )
            
            logger.debug(f"Encoded {len(valid_texts)} texts to embeddings of shape {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Encode a single text to embedding
        
        Args:
            text: Text string to encode
        
        Returns:
            Numpy array of embedding
        """
        return self.encode([text])[0]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        if self.model is None:
            return EMBEDDING_DIMENSION
        
        # Get dimension from model
        test_embedding = self.model.encode("test", convert_to_numpy=True)
        return len(test_embedding)
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Cosine similarity score between 0 and 1
        """
        embeddings = self.encode([text1, text2])
        if len(embeddings) < 2:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        
        return float(similarity)
    
    def batch_similarity(self, query_text: str, texts: List[str]) -> List[float]:
        """
        Calculate similarities between a query text and a list of texts
        
        Args:
            query_text: Query text
            texts: List of texts to compare against
        
        Returns:
            List of similarity scores
        """
        if not texts:
            return []
        
        # Encode all texts including query
        all_texts = [query_text] + texts
        embeddings = self.encode(all_texts)
        
        if len(embeddings) < 2:
            return [0.0] * len(texts)
        
        query_embedding = embeddings[0]
        text_embeddings = embeddings[1:]
        
        # Calculate cosine similarities
        similarities = []
        for text_embedding in text_embeddings:
            similarity = np.dot(query_embedding, text_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(text_embedding)
            )
            similarities.append(float(similarity))
        
        return similarities
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        if self.model is None:
            return {"error": "Model not loaded"}
        
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "device": self.device,
            "max_sequence_length": MAX_SEQUENCE_LENGTH,
            "cache_dir": str(self.cache_dir)
        }

# Global embedder instance
_embedder_instance = None

def get_embedder() -> Embedder:
    """Get or create the global embedder instance"""
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = Embedder()
    return _embedder_instance

def reset_embedder():
    """Reset the global embedder instance (useful for testing)"""
    global _embedder_instance
    _embedder_instance = None 