"""
Text Chunking Service
Splits documents into smaller chunks with overlap for better context retention
"""
from typing import List, Dict
from app.config import config


class TextChunker:
    """Service to chunk text documents into smaller pieces with overlap"""
    
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    def chunk_text(self, text: str, source_file: str = None, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text content to chunk
            source_file: Name of the source file (for metadata)
            metadata: Additional metadata to include with each chunk
            
        Returns:
            List[Dict]: List of chunks, each containing:
                - text: The chunk text
                - chunk_index: Index of chunk in document
                - source_file: Source file name
                - metadata: Additional metadata
        """
        if not text or not text.strip():
            return []
        
        # Clean and normalize text
        text = text.strip()
        
        # If text is shorter than chunk_size, return as single chunk
        if len(text) <= self.chunk_size:
            chunk_data = {
                "text": text,
                "chunk_index": 0,
                "source_file": source_file or "unknown",
                "total_chunks": 1
            }
            if metadata:
                chunk_data.update(metadata)
            return [chunk_data]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # Extract chunk
            chunk_text = text[start:end]
            
            # Try to break at word boundary if not at end of text
            if end < len(text):
                # Look for last space, newline, or period in the last 20% of chunk
                boundary_search_start = max(start + int(self.chunk_size * 0.8), start)
                boundary_chars = ['\n\n', '\n', '. ', ' ', '']
                
                for boundary in boundary_chars:
                    if boundary:
                        last_boundary = chunk_text.rfind(boundary, boundary_search_start - start)
                        if last_boundary != -1:
                            end = start + last_boundary + len(boundary)
                            chunk_text = text[start:end]
                            break
            
            # Create chunk data
            chunk_data = {
                "text": chunk_text.strip(),
                "chunk_index": chunk_index,
                "source_file": source_file or "unknown",
                "start_char": start,
                "end_char": end
            }
            
            # Add metadata if provided
            if metadata:
                chunk_data.update(metadata)
            
            chunks.append(chunk_data)
            
            # Move start position (with overlap)
            start = end - self.chunk_overlap
            chunk_index += 1
            
            # Safety check to avoid infinite loop
            if start >= len(text):
                break
        
        # Update total_chunks for all chunks
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk["total_chunks"] = total_chunks
        
        return chunks
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk multiple documents
        
        Args:
            documents: List of documents, each with 'content' and optionally 'name' and 'metadata'
            
        Returns:
            List[Dict]: List of all chunks from all documents
        """
        all_chunks = []
        
        for doc in documents:
            content = doc.get('content', '')
            source_file = doc.get('name', doc.get('source_file', 'unknown'))
            metadata = doc.get('metadata', {})
            
            # Add document-level metadata
            if 'name' in doc:
                metadata['document_name'] = doc['name']
            
            chunks = self.chunk_text(content, source_file=source_file, metadata=metadata)
            all_chunks.extend(chunks)
        
        return all_chunks
