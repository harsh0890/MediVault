"""
Vector Store Service
Manages FAISS vector database for storing and retrieving document embeddings
"""
import faiss
import numpy as np
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional
from app.config import config


class VectorStore:
    """Service to manage vector database operations using FAISS"""
    
    def __init__(self):
        """Initialize FAISS index and metadata storage"""
        self.db_path = config.VECTOR_DB_PATH
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
        # Create directory if it doesn't exist
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.index_file = self.db_path / "medical_records.faiss"
        self.metadata_file = self.db_path / "medical_records_metadata.pkl"
        
        # Initialize index and metadata
        self.index = None
        self.metadata = []  # List of dicts, one per vector
        self._load_index()
    
    def _load_index(self):
        """Load existing index or create new one"""
        if self.index_file.exists() and self.metadata_file.exists():
            try:
                # Load index
                self.index = faiss.read_index(str(self.index_file))
                
                # Load metadata
                with open(self.metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                print(f"Loaded existing vector store: {self.index.ntotal} vectors")
            except Exception as e:
                print(f"Error loading index, creating new: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        # Use L2 (Euclidean) distance for similarity search
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata = []
        print("Created new vector store index")
    
    def add_documents(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Add document chunks with embeddings to the vector store
        
        Args:
            chunks: List of chunk dictionaries with text and metadata
            embeddings: List of embedding vectors (one per chunk)
        """
        if not chunks or not embeddings:
            return
        
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings")
        
        # Convert embeddings to numpy array
        embedding_array = np.array(embeddings, dtype='float32')
        
        # Validate dimensions
        if embedding_array.shape[1] != self.embedding_dim:
            raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dim}, got {embedding_array.shape[1]}")
        
        # Add to index
        self.index.add(embedding_array)
        
        # Store metadata for each chunk
        for chunk in chunks:
            metadata_entry = {
                'text': chunk.get('text', ''),
                'source_file': str(chunk.get('source_file', 'unknown')),
                'chunk_index': int(chunk.get('chunk_index', 0)),
                'total_chunks': int(chunk.get('total_chunks', 1))
            }
            
            # Add any additional metadata
            for key, value in chunk.items():
                if key not in ['text', 'source_file', 'chunk_index', 'total_chunks']:
                    if isinstance(value, (str, int, float, bool)):
                        metadata_entry[key] = value
                    else:
                        metadata_entry[key] = str(value)
            
            self.metadata.append(metadata_entry)
        
        # Save index and metadata
        self._save_index()
        
        print(f"Added {len(chunks)} chunks to vector store (total: {self.index.ntotal})")
    
    def search_similar(self, query_embedding: List[float], top_k: int = None) -> List[Dict]:
        """
        Search for similar chunks based on query embedding
        
        Args:
            query_embedding: Embedding vector of the query
            top_k: Number of results to return (defaults to config value)
            
        Returns:
            List[Dict]: List of similar chunks with metadata and similarity scores
        """
        if top_k is None:
            top_k = config.TOP_K_CHUNKS
        
        if self.index.ntotal == 0:
            return []
        
        # Convert query to numpy array
        query_array = np.array([query_embedding], dtype='float32')
        
        # Validate dimension
        if query_array.shape[1] != self.embedding_dim:
            raise ValueError(f"Query embedding dimension mismatch: expected {self.embedding_dim}, got {query_array.shape[1]}")
        
        # Search
        distances, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
        
        # Format results
        similar_chunks = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                chunk_data = {
                    'text': self.metadata[idx]['text'],
                    'metadata': {k: v for k, v in self.metadata[idx].items() if k != 'text'},
                    'id': f"chunk_{idx}",
                    'distance': float(distances[0][i])  # L2 distance (lower is more similar)
                }
                similar_chunks.append(chunk_data)
        
        return similar_chunks
    
    def clear_collection(self):
        """Clear all documents from the collection (for rebuilding)"""
        self._create_new_index()
        self._save_index()
        print("Cleared vector store")
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection"""
        return self.index.ntotal if self.index else 0
    
    def _save_index(self):
        """Save index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))
            
            # Save metadata
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            print(f"Error saving index: {e}")
