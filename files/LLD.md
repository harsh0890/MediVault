# Low Level Design (LLD) - MediVault

## Component Details

---

## 1. Document Ingestion Service

### Classes

#### `DocumentParser`
```python
class DocumentParser:
    def parse_pdf(self, file_path: str) -> Document
    def extract_text_from_image(self, image_path: str) -> str
    def parse_fhir(self, fhir_data: dict) -> Document
    def parse_hl7(self, hl7_data: str) -> Document
```

#### `DocumentChunker`
```python
class DocumentChunker:
    def chunk_by_size(self, text: str, chunk_size: int) -> List[Chunk]
    def chunk_by_sentences(self, text: str) -> List[Chunk]
    def chunk_by_semantic(self, text: str) -> List[Chunk]
    def add_overlap(self, chunks: List[Chunk], overlap_size: int) -> List[Chunk]
```

#### `OCRProcessor`
```python
class OCRProcessor:
    def extract_text(self, image: bytes) -> str
    def preprocess_image(self, image: bytes) -> bytes
```

---

## 2. RAG Service

### Classes

#### `EmbeddingService`
```python
class EmbeddingService:
    def __init__(self, model_name: str)
    def generate_embedding(self, text: str) -> np.ndarray
    def generate_batch_embeddings(self, texts: List[str]) -> np.ndarray
    def get_model_dimension(self) -> int
```

#### `VectorStore`
```python
class VectorStore:
    def add_documents(self, chunks: List[Chunk], embeddings: np.ndarray)
    def search(self, query_embedding: np.ndarray, top_k: int) -> List[Chunk]
    def delete_documents(self, document_ids: List[str])
    def update_document(self, chunk_id: str, chunk: Chunk, embedding: np.ndarray)
```

#### `RetrievalService`
```python
class RetrievalService:
    def semantic_search(self, query: str, top_k: int) -> List[Chunk]
    def hybrid_search(self, query: str, top_k: int) -> List[Chunk]
    def keyword_search(self, query: str, top_k: int) -> List[Chunk]
    def rerank_results(self, query: str, chunks: List[Chunk]) -> List[Chunk]
```

#### `LLMService`
```python
class LLMService:
    def generate_summary(self, chunks: List[Chunk]) -> str
    def answer_question(self, query: str, context: List[Chunk]) -> Answer
    def explain_plain_language(self, medical_text: str) -> str
    def generate_recommendations(self, medical_history: dict) -> List[Recommendation]
```

---

## 3. Query Processing Service

### Classes

#### `QueryRouter`
```python
class QueryRouter:
    def route_query(self, query: str) -> QueryType
    def classify_intent(self, query: str) -> Intent
```

#### `QueryProcessor`
```python
class QueryProcessor:
    def process_summarization_query(self, query: str, filters: dict) -> str
    def process_qa_query(self, query: str) -> Answer
    def process_recommendation_query(self, query: str) -> List[Recommendation]
    def add_citations(self, response: str, chunks: List[Chunk]) -> str
```

---

## 4. Database Schemas

### PostgreSQL Tables

#### `users`
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_verified BOOLEAN,
    privacy_settings JSONB
);
```

#### `documents`
```sql
CREATE TABLE documents (
    document_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    file_size BIGINT,
    storage_path VARCHAR(500),
    upload_date TIMESTAMP,
    document_type VARCHAR(100), -- report, prescription, lab_result, etc.
    metadata JSONB,
    is_processed BOOLEAN
);
```

#### `chunks`
```sql
CREATE TABLE chunks (
    chunk_id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(document_id),
    chunk_index INTEGER,
    text_content TEXT,
    start_char INTEGER,
    end_char INTEGER,
    metadata JSONB
);
```

#### `access_logs`
```sql
CREATE TABLE access_logs (
    log_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    accessed_by UUID, -- user or hospital/provider
    access_type VARCHAR(50), -- read, query, emergency
    timestamp TIMESTAMP,
    ip_address VARCHAR(45),
    query_text TEXT
);
```

#### `insurance_policies`
```sql
CREATE TABLE insurance_policies (
    policy_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    provider_name VARCHAR(255),
    policy_number VARCHAR(100),
    coverage_details JSONB,
    documents JSONB, -- EOBs, policy docs
    created_at TIMESTAMP
);
```

---

## 5. API Endpoints

### Document Management
```
POST   /api/v1/documents/upload
GET    /api/v1/documents/{document_id}
DELETE /api/v1/documents/{document_id}
GET    /api/v1/documents
```

### Query Endpoints
```
POST   /api/v1/query/summarize
POST   /api/v1/query/ask
POST   /api/v1/query/explain
POST   /api/v1/query/recommend
```

### Emergency Access
```
POST   /api/v1/emergency/access
GET    /api/v1/emergency/history/{user_id}
```

### Insurance
```
POST   /api/v1/insurance/upload
GET    /api/v1/insurance/coverage
POST   /api/v1/insurance/query
```

### Community
```
GET    /api/v1/community/posts
POST   /api/v1/community/posts
POST   /api/v1/community/posts/{post_id}/reply
```

---

## 6. Data Models

### Document Model
```python
@dataclass
class Document:
    document_id: str
    user_id: str
    file_name: str
    file_type: str
    file_size: int
    storage_path: str
    upload_date: datetime
    document_type: str
    metadata: dict
    is_processed: bool
```

### Chunk Model
```python
@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    chunk_index: int
    text_content: str
    start_char: int
    end_char: int
    embedding: np.ndarray
    metadata: dict
```

### Answer Model
```python
@dataclass
class Answer:
    answer_text: str
    citations: List[Citation]
    confidence_score: float
    source_chunks: List[Chunk]
    timestamp: datetime
```

### Citation Model
```python
@dataclass
class Citation:
    document_id: str
    chunk_id: str
    page_number: int
    excerpt: str
```

---

## 7. Service Interfaces

### Document Ingestion Interface
```python
class IDocumentIngestion:
    def ingest_document(self, file: bytes, metadata: dict) -> Document
    def process_document(self, document_id: str) -> bool
    def extract_text(self, document: Document) -> str
```

### RAG Interface
```python
class IRAGService:
    def index_document(self, document: Document, chunks: List[Chunk])
    def search(self, query: str, top_k: int) -> List[Chunk]
    def generate_response(self, query: str, context: List[Chunk]) -> Answer
```

---

## 8. Error Handling

### Custom Exceptions
```python
class DocumentProcessingError(Exception)
class EmbeddingGenerationError(Exception)
class VectorStoreError(Exception)
class LLMServiceError(Exception)
class AuthenticationError(Exception)
class AuthorizationError(Exception)
```

---

## 9. Configuration

### Environment Variables
```python
DATABASE_URL
VECTOR_DB_URL
LLM_API_KEY
LLM_MODEL_NAME
EMBEDDING_MODEL_NAME
STORAGE_BUCKET_NAME
REDIS_URL
JWT_SECRET_KEY
```

---

## 10. Testing Strategy

- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **E2E Tests**: Full workflow testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Authentication, authorization, data privacy
