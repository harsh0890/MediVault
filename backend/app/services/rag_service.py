"""
RAG Service (Retrieval-Augmented Generation)
Orchestrates the entire RAG pipeline: chunking, embedding, storage, and retrieval
"""
from typing import List, Dict
from app.services.document_reader import DocumentReader
from app.services.text_chunker import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.gemini_service import GeminiService


class RAGService:
    """Main RAG service that orchestrates document ingestion and query processing"""
    
    def __init__(self):
        """Initialize all RAG components"""
        self.document_reader = DocumentReader()
        self.text_chunker = TextChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.gemini_service = GeminiService()
    
    def ingest_documents(self, rebuild: bool = False) -> Dict:
        """
        Process and store all medical records in the vector database
        
        Args:
            rebuild: If True, clear existing data before ingesting
            
        Returns:
            Dict: Summary of ingestion (number of documents, chunks, etc.)
        """
        # Clear collection if rebuilding
        if rebuild:
            print("Rebuilding vector index...")
            self.vector_store.clear_collection()
        
        # Read all medical records
        records = self.document_reader.get_records_with_metadata()
        
        if not records:
            return {
                "status": "no_documents",
                "message": "No medical records found to ingest",
                "documents_processed": 0,
                "chunks_created": 0
            }
        
        # Chunk all documents
        print(f"Chunking {len(records)} documents...")
        all_chunks = self.text_chunker.chunk_documents(records)
        
        if not all_chunks:
            return {
                "status": "no_chunks",
                "message": "No chunks created from documents",
                "documents_processed": len(records),
                "chunks_created": 0
            }
        
        # Generate embeddings for all chunks
        print(f"Generating embeddings for {len(all_chunks)} chunks...")
        chunk_texts = [chunk['text'] for chunk in all_chunks]
        embeddings = self.embedding_service.generate_embeddings_batch(chunk_texts)
        
        # Store in vector database
        print(f"Storing {len(all_chunks)} chunks in vector database...")
        self.vector_store.add_documents(all_chunks, embeddings)
        
        return {
            "status": "success",
            "message": f"Successfully ingested {len(records)} documents",
            "documents_processed": len(records),
            "chunks_created": len(all_chunks),
            "vector_store_count": self.vector_store.get_collection_count()
        }
    
    def query(self, question: str) -> Dict:
        """
        Answer a question using RAG: retrieve relevant chunks and generate answer
        
        Args:
            question: User's question
            
        Returns:
            Dict: Contains 'answer', 'recommendations', 'sources', 'needs_followup', 'has_records'
        """
        # Check if vector store has data
        if self.vector_store.get_collection_count() == 0:
            # If no data, try to ingest documents first
            print("Vector store is empty, attempting to ingest documents...")
            ingest_result = self.ingest_documents()
            if ingest_result['status'] != 'success':
                return {
                    "answer": "I don't have access to your medical records yet. Please upload your medical records first.",
                    "recommendations": [],
                    "sources": [],
                    "needs_followup": False,
                    "has_records": False
                }
        
        # Generate embedding for the question
        question_embedding = self.embedding_service.generate_embedding(question)
        
        # Search for similar chunks
        similar_chunks = self.vector_store.search_similar(question_embedding)
        
        # Determine if question is answerable from records
        has_relevant_records = len(similar_chunks) > 0
        
        # Combine retrieved chunks into context
        context_parts = []
        sources = []
        
        if has_relevant_records:
            for chunk in similar_chunks:
                source_file = chunk['metadata'].get('source_file', 'unknown')
                chunk_text = chunk['text']
                context_parts.append(f"[From {source_file}]\n{chunk_text}")
                
                # Track unique sources
                if source_file not in sources:
                    sources.append(source_file)
        
        context = "\n\n".join(context_parts) if context_parts else ""
        
        # Prepare prompt for Gemini with interactive behavior
        system_instruction = """You are a medical assistant helping patients understand their medical records and general health questions. 
When answering questions:
1. If the question can be answered from the patient's medical records, use that information and mention it came from their records
2. If the question is NOT in the medical records, inform the user clearly: "This information is not found in your medical records." Then IMMEDIATELY provide general medical information to answer the question - don't ask permission, just provide it
3. For diet plan questions, use the patient's medical records (if available) to provide personalized diet recommendations based on their health conditions
4. DO NOT provide recommendations directly in the answer - instead, at the end ask ONCE: "Would you like me to provide recommendations based on this information?"
5. Be conversational, helpful, and empathetic
6. Always include medical disclaimers that this is not a substitute for professional medical advice
7. Cite which document the information came from when using specific records
8. Answer questions directly and completely - don't ask multiple questions

Format your response:
- First, state whether the information is in their records or not (if not in records, say so but then immediately provide the answer)
- Provide the complete answer (from records if available, or general medical information if not)
- At the end, ask ONCE: "Would you like me to provide recommendations based on this information?"
- Include a medical disclaimer"""
        
        if has_relevant_records:
            prompt = f"""Please answer this question: {question}

Relevant Medical Records Sections:
{context}

Instructions:
1. First confirm that this information is found in the patient's medical records
2. Provide the complete answer based on the records above
3. If the question is about diet plans, use the patient's health conditions from the records to provide personalized diet recommendations
4. At the end, ask ONCE: "Would you like me to provide recommendations based on your medical records?"
5. Include a medical disclaimer"""
        else:
            prompt = f"""Please answer this question: {question}

IMPORTANT: This information is NOT found in the patient's medical records.

Instructions:
1. First inform the user: "This information is not found in your medical records."
2. Then IMMEDIATELY provide the complete general medical information to answer the question - don't ask permission, just provide it
3. If the question is about diet plans, provide a general diet plan that could help with the topic
4. At the end, ask ONCE: "Would you like me to provide recommendations based on this information?"
5. Include a medical disclaimer
6. Be helpful and provide complete information"""
        
        # Get answer from Gemini
        try:
            full_response = self.gemini_service._call_gemini_api(prompt, system_instruction)
            
            # Parse response
            answer = full_response.strip()
            recommendations = []  # Will be empty - recommendations come from separate request
            
            # Check if response asks for follow-up
            needs_followup = (
                "would you like" in answer.lower() or 
                "do you want" in answer.lower() or
                "can provide" in answer.lower() or
                "would you" in answer.lower()
            )
            
            return {
                "answer": answer,
                "recommendations": recommendations,  # Empty - user must request
                "sources": sources,
                "needs_followup": needs_followup,
                "has_records": has_relevant_records
            }
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "recommendations": [],
                "sources": sources,
                "needs_followup": False,
                "has_records": has_relevant_records
            }
    
    def get_recommendations(self, question: str, context_from_records: bool = True) -> Dict:
        """
        Get recommendations for a question (only when user requests)
        
        Args:
            question: Original user question
            context_from_records: Whether the answer came from records
            
        Returns:
            Dict: Contains 'recommendations' list and 'sources'
        """
        # Get relevant chunks if available
        question_embedding = self.embedding_service.generate_embedding(question)
        similar_chunks = self.vector_store.search_similar(question_embedding)
        
        context_parts = []
        sources = []
        
        if similar_chunks:
            for chunk in similar_chunks:
                source_file = chunk['metadata'].get('source_file', 'unknown')
                chunk_text = chunk['text']
                context_parts.append(f"[From {source_file}]\n{chunk_text}")
                if source_file not in sources:
                    sources.append(source_file)
        
        # Also get all records for context (especially for diet plans based on health conditions)
        all_records = self.document_reader.read_all_records()
        
        context = "\n\n".join(context_parts) if context_parts else ""
        
        system_instruction = """You are a medical assistant providing recommendations. 
Provide TWO types of recommendations:
1. Medical record-based recommendations (specific to the patient's records and health conditions, if available)
2. General health recommendations (best practices, lifestyle advice)

For diet plan questions, provide personalized diet recommendations based on the patient's specific health conditions from their records.

Format as a clear list. Always include a medical disclaimer."""
        
        if context_from_records and (context or all_records):
            full_context = context
            if all_records and context not in all_records:
                full_context = f"{context}\n\nAll Medical Records:\n{all_records}" if context else f"All Medical Records:\n{all_records}"
            
            prompt = f"""Based on the following question and medical records, provide recommendations:

Question: {question}

Medical Records Sections:
{full_context}

Please provide:
1. Medical record-based recommendations (specific to this patient's health conditions)
2. General health recommendations
3. If this is about diet plans, provide a personalized diet plan based on the patient's health conditions
4. Medical disclaimer"""
        else:
            prompt = f"""Based on the following question, provide general health recommendations:

Question: {question}

Please provide:
1. General health recommendations
2. If this is about diet plans, provide a general diet plan
3. Medical disclaimer"""
        
        try:
            full_response = self.gemini_service._call_gemini_api(prompt, system_instruction)
            
            # Parse recommendations
            recommendations = []
            for line in full_response.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*') or 
                           (len(line) > 2 and line[0].isdigit() and line[1] in ['.', ')'])):
                    rec = line.lstrip('-•*0123456789.) ').strip()
                    if rec and 'disclaimer' not in rec.lower() and len(rec) > 10:
                        recommendations.append(rec)
            
            if not recommendations:
                recommendations = ["Please consult with your healthcare provider for personalized medical advice."]
            
            return {
                "recommendations": recommendations,
                "sources": sources
            }
        except Exception as e:
            return {
                "recommendations": [f"Error generating recommendations: {str(e)}"],
                "sources": sources
            }
    
    def get_summary(self) -> str:
        """
        Get summary of all medical records using RAG approach
        
        Returns:
            str: Summary of medical records
        """
        # Check if vector store has data
        if self.vector_store.get_collection_count() == 0:
            # If no data, try to ingest documents first
            ingest_result = self.ingest_documents()
            if ingest_result['status'] != 'success':
                return "No medical records found."
        
        # Read all records for summary (can use direct approach or RAG)
        # For summary, we'll use direct approach as it needs all context
        medical_records = self.document_reader.read_all_records()
        
        if not medical_records.strip():
            return "No medical records found."
        
        # Use Gemini to summarize
        try:
            summary = self.gemini_service.summarize_medical_records(medical_records)
            return summary
        except Exception as e:
            return f"Error generating summary: {str(e)}"
