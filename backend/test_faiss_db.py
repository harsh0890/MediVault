"""
Test script to verify FAISS vector database connection and operations
"""
import sys
import numpy as np
from pathlib import Path

def test_faiss():
    """Test FAISS vector database connection and basic operations"""
    print("=" * 60)
    print("Testing FAISS Vector Database")
    print("=" * 60)
    
    try:
        # Test 1: Import FAISS
        print("\n1. Testing FAISS import...")
        import faiss
        print("   ✅ FAISS imported successfully")
        
        # Test 2: Check configuration
        print("\n2. Checking configuration...")
        from app.config import config
        db_path = config.VECTOR_DB_PATH
        print(f"   ✓ Vector DB Path: {db_path}")
        print(f"   ✓ Embedding Dimension: 384 (all-MiniLM-L6-v2)")
        print(f"   ✓ Top K Chunks: {config.TOP_K_CHUNKS}")
        
        # Test 3: Create directory
        print("\n3. Creating vector database directory...")
        db_path.mkdir(parents=True, exist_ok=True)
        if db_path.exists():
            print(f"   ✅ Directory created/exists: {db_path}")
        else:
            print(f"   ❌ Failed to create directory: {db_path}")
            return False
        
        # Test 4: Create FAISS index
        print("\n4. Creating FAISS index...")
        dimension = 384  # all-MiniLM-L6-v2 embedding dimension
        index = faiss.IndexFlatL2(dimension)  # L2 distance (Euclidean)
        print(f"   ✅ FAISS index created (dimension: {dimension})")
        
        # Test 5: Add test vectors
        print("\n5. Adding test vectors...")
        test_vectors = np.array([
            [0.1] * dimension,
            [0.2] * dimension,
            [0.3] * dimension
        ], dtype='float32')
        
        index.add(test_vectors)
        print(f"   ✅ Added {len(test_vectors)} test vectors")
        print(f"   ✓ Index size: {index.ntotal}")
        
        # Test 6: Search
        print("\n6. Testing search...")
        query_vector = np.array([[0.15] * dimension], dtype='float32')
        k = 2  # Top 2 results
        distances, indices = index.search(query_vector, k)
        
        print(f"   ✅ Search successful")
        print(f"   ✓ Found {len(indices[0])} results")
        print(f"   ✓ Top result index: {indices[0][0]}, distance: {distances[0][0]:.4f}")
        
        # Test 7: Save and load index
        print("\n7. Testing save/load...")
        index_file = db_path / "test_index.faiss"
        faiss.write_index(index, str(index_file))
        print(f"   ✅ Index saved to: {index_file}")
        
        loaded_index = faiss.read_index(str(index_file))
        print(f"   ✅ Index loaded successfully")
        print(f"   ✓ Loaded index size: {loaded_index.ntotal}")
        
        # Test 8: Clean up
        print("\n8. Cleaning up test files...")
        if index_file.exists():
            index_file.unlink()
            print(f"   ✅ Test index file deleted")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - FAISS is working correctly!")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Make sure FAISS is installed: pip install faiss-cpu")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_faiss()
    sys.exit(0 if success else 1)
