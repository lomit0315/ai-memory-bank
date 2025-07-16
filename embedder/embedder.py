import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
import config

class Embedder:
    """Handle text embedding using sentence-transformers."""
    
    def __init__(self):
        self.model = None
        self.model_name = config.EMBEDDING_MODEL
        self.dimension = config.EMBEDDING_DIMENSION
        
    def load_model(self):
        """Load the embedding model."""
        if self.model is None:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=str(config.MODEL_CACHE_DIR)
            )
            print("Model loaded successfully!")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            self.load_model()
            
        return self.model.encode([text])[0]
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            self.load_model()
            
        if not texts:
            return np.array([])
            
        return self.model.encode(
            texts,
            batch_size=config.BATCH_SIZE,
            show_progress_bar=len(texts) > 10
        )
    
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.dimension

# Global embedder instance
embedder = Embedder() 