# High Level Design (HLD) - MediVault

## System Overview

MediVault is a GenAI-powered Personal Health Record Vault that enables users to store, query, and manage their medical records through natural language interactions using RAG (Retrieval-Augmented Generation).

---

## Architecture Components

### 1. **Frontend Layer**
- **Web Application**: React/Next.js for user interface
- **Mobile Application**: React Native for iOS/Android
- **Dual Views**:
  - Self Profile View (personal dashboard)
  - Emergency/Hospital View (authenticated access for healthcare providers)

### 2. **API Gateway**
- RESTful API endpoints
- Authentication & Authorization (OAuth 2.0, JWT)
- Rate limiting and request validation
- API versioning

### 3. **Application Services Layer**

#### 3.1 **Document Ingestion Service**
- PDF parsing and text extraction
- OCR for scanned documents and images
- FHIR/HL7 format support
- Document chunking and preprocessing

#### 3.2 **RAG Service**
- **Embedding Service**: Generate embeddings using open-source models (e.g., sentence-transformers)
- **Vector Database**: Store document chunks with embeddings (Pinecone, Weaviate, or ChromaDB)
- **Retrieval Service**: Semantic search and hybrid search (keyword + semantic)
- **LLM Service**: Integration with LLM APIs (OpenAI, Anthropic, or local models)

#### 3.3 **Query Processing Service**
- Natural language query understanding
- Query routing (summarization, Q&A, recommendations)
- Response generation with citations
- Medical disclaimer enforcement

#### 3.4 **Notification Service**
- Health monitoring alerts
- Diet plan recommendations
- Medication reminders
- Personalized health insights

#### 3.5 **Community Service**
- Verified user management
- Anonymous/anonymous participation
- Discussion forums and Q&A

#### 3.6 **Recommendation Service**
- Doctor/hospital recommendations based on medical history
- LLM-powered matching algorithm

#### 3.7 **Insurance Service**
- Insurance document ingestion
- Coverage analysis and Q&A
- Financial relief insights

### 4. **Data Storage Layer**

#### 4.1 **Document Storage**
- **Object Storage**: AWS S3 / Azure Blob Storage for raw documents
- **Metadata Database**: PostgreSQL for document metadata, user info, access logs

#### 4.2 **Vector Database**
- Embedding storage and similarity search
- Document chunk indexing

#### 4.3 **Cache Layer**
- Redis for frequently accessed data
- Query result caching

### 5. **External Integrations**
- EHR systems (FHIR/HL7)
- Insurance providers (APIs)
- Hospital systems (for emergency access)
- Wearable device APIs
- Lab network APIs

---

## Data Flow

### Document Upload Flow
```
User → Frontend → API Gateway → Document Ingestion Service
  → Object Storage (raw docs)
  → Text Extraction/OCR
  → Chunking
  → Embedding Generation
  → Vector Database (chunks + embeddings)
  → Metadata Database (document info)
```

### Query Flow
```
User Query → API Gateway → Query Processing Service
  → Query Understanding
  → Embedding Generation (query)
  → Vector Database (semantic search)
  → Retrieval Service (top-k chunks)
  → LLM Service (context + query)
  → Response Generation with Citations
  → User
```

### Emergency Access Flow
```
Hospital/Provider → Emergency/Hospital View
  → Authentication (OAuth/API key)
  → Access Control Check
  → Query Processing Service
  → Fast Retrieval (prioritized)
  → Medical History Summary
```

---

## Security & Privacy

- **Encryption**: End-to-end encryption for sensitive data
- **Access Control**: Role-based access (RBAC)
- **Audit Logging**: All access attempts logged
- **Data Isolation**: User data isolated by tenant/user
- **Privacy-by-Design**: No training on user data, optional local deployment

---

## Scalability Considerations

- **Horizontal Scaling**: Stateless services, load balancers
- **Database Sharding**: User-based sharding for metadata
- **Caching Strategy**: Multi-level caching (Redis, CDN)
- **Async Processing**: Message queues for document processing
- **CDN**: Static content delivery

---

## Technology Stack

- **Frontend**: React/Next.js, React Native
- **Backend**: Python (FastAPI) / Node.js
- **Database**: PostgreSQL, Redis
- **Vector DB**: Pinecone / Weaviate / ChromaDB
- **LLM**: OpenAI API / Anthropic / Local models (Llama, Mistral)
- **Embeddings**: sentence-transformers, OpenAI embeddings
- **Storage**: AWS S3 / Azure Blob Storage
- **Message Queue**: RabbitMQ / Apache Kafka
- **Containerization**: Docker, Kubernetes
