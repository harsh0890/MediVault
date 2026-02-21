"""
Comprehensive test script to verify the full MediVault RAG application
"""
import sys
from pathlib import Path

def test_full_application():
    """Test all components of the MediVault application"""
    print("=" * 70)
    print("MediVault RAG Application - Full System Check")
    print("=" * 70)
    
    all_tests_passed = True
    
    # Test 1: Configuration
    print("\n[1/8] Testing Configuration...")
    try:
        from app.config import config
        assert config.GEMINI_API_KEY, "GEMINI_API_KEY not set"
        assert config.GEMINI_MODEL, "GEMINI_MODEL not set"
        assert config.MEDICAL_RECORDS_DIR, "MEDICAL_RECORDS_DIR not set"
        assert config.VECTOR_DB_PATH, "VECTOR_DB_PATH not set"
        print("   ✅ Configuration loaded successfully")
        print(f"   ✓ Model: {config.GEMINI_MODEL}")
        print(f"   ✓ Vector DB: {config.VECTOR_DB_PATH}")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        all_tests_passed = False
    
    # Test 2: Document Reader
    print("\n[2/8] Testing Document Reader...")
    try:
        from app.services.document_reader import DocumentReader
        reader = DocumentReader()
        records = reader.get_records_with_metadata()
        print(f"   ✅ Document Reader initialized")
        print(f"   ✓ Found {len(records)} medical record(s)")
    except Exception as e:
        print(f"   ❌ Document Reader error: {e}")
        all_tests_passed = False
    
    # Test 3: Text Chunker
    print("\n[3/8] Testing Text Chunker...")
    try:
        from app.services.text_chunker import TextChunker
        chunker = TextChunker()
        test_text = "This is a test medical record. " * 20  # Long text
        chunks = chunker.chunk_text(test_text, source_file="test.txt")
        print(f"   ✅ Text Chunker initialized")
        print(f"   ✓ Created {len(chunks)} chunks from test text")
    except Exception as e:
        print(f"   ❌ Text Chunker error: {e}")
        all_tests_passed = False
    
    # Test 4: Embedding Service
    print("\n[4/8] Testing Embedding Service...")
    try:
        from app.services.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        # Test embedding generation (this will load the model)
        test_embedding = embedding_service.generate_embedding("Test text")
        print(f"   ✅ Embedding Service initialized")
        print(f"   ✓ Generated embedding (dimension: {len(test_embedding)})")
    except Exception as e:
        print(f"   ❌ Embedding Service error: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Test 5: Vector Store
    print("\n[5/8] Testing Vector Store (FAISS)...")
    try:
        from app.services.vector_store import VectorStore
        vector_store = VectorStore()
        count = vector_store.get_collection_count()
        print(f"   ✅ Vector Store initialized")
        print(f"   ✓ Current vector count: {count}")
    except Exception as e:
        print(f"   ❌ Vector Store error: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Test 6: Gemini Service
    print("\n[6/8] Testing Gemini Service...")
    try:
        from app.services.gemini_service import GeminiService
        gemini_service = GeminiService()
        print(f"   ✅ Gemini Service initialized")
        print(f"   ✓ Model: {gemini_service.model}")
        print(f"   ✓ API Key configured")
    except Exception as e:
        print(f"   ❌ Gemini Service error: {e}")
        all_tests_passed = False
    
    # Test 7: RAG Service
    print("\n[7/8] Testing RAG Service...")
    try:
        from app.services.rag_service import RAGService
        rag_service = RAGService()
        print(f"   ✅ RAG Service initialized")
        print(f"   ✓ All components loaded")
    except Exception as e:
        print(f"   ❌ RAG Service error: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Test 8: FastAPI Application
    print("\n[8/8] Testing FastAPI Application...")
    try:
        from app.main import app, get_rag_service
        print(f"   ✅ FastAPI application imported")
        print(f"   ✓ App title: {app.title}")
        # Test RAG service getter (lazy initialization)
        rag = get_rag_service()
        print(f"   ✅ RAG service getter works")
    except Exception as e:
        print(f"   ❌ FastAPI Application error: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_tests_passed:
        print("✅ ALL TESTS PASSED - Application is ready to run!")
        print("=" * 70)
        print("\nYou can now start the server with:")
        print("  python backend/run.py")
        print("\nOr:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("❌ SOME TESTS FAILED - Please fix the errors above")
        print("=" * 70)
    
    return all_tests_passed

if __name__ == "__main__":
    success = test_full_application()
    sys.exit(0 if success else 1)
