"""
Embedding Service
Generates embeddings for text using sentence-transformers
"""
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import config


class EmbeddingService:
    """Service to generate embeddings for text chunks and queries"""
    
    def __init__(self):
        """Initialize the embedding model (loads on first use)"""
        self.model_name = config.EMBEDDING_MODEL
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model (only loads when first used)"""
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            print(f"Embedding model loaded successfully!")
        return self._model
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        if not text or not text.strip():
            # Return zero vector if text is empty
            # Get dimension from model (typically 384 for all-MiniLM-L6-v2)
            return [0.0] * 384
        
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [text if text and text.strip() else " " for text in texts]
        
        # Generate embeddings in batch (faster)
        embeddings = self.model.encode(
            valid_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        
        return embeddings.tolist()
