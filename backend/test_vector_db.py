"""
Test script to verify ChromaDB vector database connection and operations
"""
import sys
from pathlib import Path

def test_chromadb():
    """Test ChromaDB connection and basic operations"""
    print("=" * 60)
    print("Testing ChromaDB Vector Database")
    print("=" * 60)
    
    try:
        # Test 1: Import ChromaDB
        print("\n1. Testing ChromaDB import...")
        import chromadb
        from chromadb.config import Settings
        print("   ✅ ChromaDB imported successfully")
        
        # Test 2: Check configuration
        print("\n2. Checking configuration...")
        from app.config import config
        db_path = config.VECTOR_DB_PATH
        print(f"   ✓ Vector DB Path: {db_path}")
        print(f"   ✓ Collection Name: medical_records")
        print(f"   ✓ Chunk Size: {config.CHUNK_SIZE}")
        print(f"   ✓ Top K Chunks: {config.TOP_K_CHUNKS}")
        
        # Test 3: Create directory
        print("\n3. Creating vector database directory...")
        db_path.mkdir(parents=True, exist_ok=True)
        if db_path.exists():
            print(f"   ✅ Directory created/exists: {db_path}")
        else:
            print(f"   ❌ Failed to create directory: {db_path}")
            return False
        
        # Test 4: Initialize ChromaDB client
        print("\n4. Initializing ChromaDB client...")
        try:
            client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            print("   ✅ ChromaDB client initialized")
        except Exception as e:
            print(f"   ❌ Failed to initialize client: {e}")
            return False
        
        # Test 5: Create/get collection
        print("\n5. Creating/getting collection...")
        try:
            collection_name = "test_collection"
            # Try to delete if exists (for clean test)
            try:
                client.delete_collection(name=collection_name)
                print(f"   ✓ Deleted existing test collection")
            except:
                pass
            
            collection = client.create_collection(
                name=collection_name,
                metadata={"description": "Test collection for MediVault"}
            )
            print(f"   ✅ Collection '{collection_name}' created")
        except Exception as e:
            print(f"   ❌ Failed to create collection: {e}")
            return False
        
        # Test 6: Add test documents
        print("\n6. Adding test documents...")
        try:
            test_documents = [
                "This is a test medical record about eye checkup.",
                "Patient has normal blood pressure readings.",
                "Prescription includes vitamins and supplements."
            ]
            test_embeddings = [
                [0.1] * 384,  # Dummy embeddings (384 dimensions for all-MiniLM-L6-v2)
                [0.2] * 384,
                [0.3] * 384
            ]
            test_ids = ["test_doc_1", "test_doc_2", "test_doc_3"]
            test_metadatas = [
                {"source_file": "test1.txt", "chunk_index": 0},
                {"source_file": "test2.txt", "chunk_index": 0},
                {"source_file": "test3.txt", "chunk_index": 0}
            ]
            
            collection.add(
                ids=test_ids,
                embeddings=test_embeddings,
                documents=test_documents,
                metadatas=test_metadatas
            )
            print(f"   ✅ Added {len(test_documents)} test documents")
        except Exception as e:
            print(f"   ❌ Failed to add documents: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 7: Query/search
        print("\n7. Testing search/query...")
        try:
            query_embedding = [0.15] * 384  # Similar to first document
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=2
            )
            
            if results['ids'] and len(results['ids'][0]) > 0:
                print(f"   ✅ Search successful - found {len(results['ids'][0])} results")
                print(f"   ✓ First result ID: {results['ids'][0][0]}")
                print(f"   ✓ First result text: {results['documents'][0][0][:50]}...")
            else:
                print("   ⚠️  Search returned no results")
        except Exception as e:
            print(f"   ❌ Failed to search: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 8: Count documents
        print("\n8. Counting documents...")
        try:
            count = collection.count()
            print(f"   ✅ Collection contains {count} documents")
        except Exception as e:
            print(f"   ❌ Failed to count: {e}")
            return False
        
        # Test 9: Clean up test collection
        print("\n9. Cleaning up test collection...")
        try:
            client.delete_collection(name=collection_name)
            print(f"   ✅ Test collection deleted")
        except Exception as e:
            print(f"   ⚠️  Could not delete test collection: {e}")
        
        # Test 10: Test VectorStore service
        print("\n10. Testing VectorStore service...")
        try:
            from app.services.vector_store import VectorStore
            vector_store = VectorStore()
            count = vector_store.get_collection_count()
            print(f"   ✅ VectorStore service initialized")
            print(f"   ✓ Current collection count: {count}")
        except Exception as e:
            print(f"   ❌ Failed to initialize VectorStore: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - ChromaDB is working correctly!")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Make sure ChromaDB is installed: pip install chromadb")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chromadb()
    sys.exit(0 if success else 1)
