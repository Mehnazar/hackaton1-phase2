# RAG Chatbot Backend

A production-ready Retrieval-Augmented Generation (RAG) chatbot backend for the AI-Native Software Development Book. Built with FastAPI, OpenAI, Qdrant, and constitutional AI principles.

## Features

### Core Capabilities
- ✅ **Dual-Mode Operation**
  - **Book-wide mode**: Semantic search over entire book using Qdrant vector database
  - **Selected-text mode**: Answer only from user-provided context (no retrieval)
- ✅ **Grounded Responses**: All answers derived from retrieved content with citations
- ✅ **Deterministic Refusal**: Explicit refusal when context is insufficient
- ✅ **Full Traceability**: Every response includes source citations with passage IDs
- ✅ **Section Proximity Reranking**: Boost same-chapter chunks for better coherence
- ✅ **Admin API**: Content indexing, statistics, and search testing

### Constitutional Principles
1. **Grounded Accuracy**: All answers derived only from book content
2. **Faithful Retrieval**: Strict mode isolation (no cross-mode information leakage)
3. **Transparency**: Full source citations for every answer
4. **Academic Rigor**: Computer-science-appropriate explanations
5. **Deterministic Refusal**: Explicit refusal when context insufficient

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI App                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐      ┌────────────────┐                │
│  │ Chat Endpoint │      │ Admin Endpoint │                │
│  └───────┬───────┘      └────────┬───────┘                │
│          │                       │                         │
│  ┌───────▼─────────────────────────────────┐              │
│  │        Retrieval Service                │              │
│  │  • Query embedding                      │              │
│  │  • Qdrant semantic search               │              │
│  │  • Section proximity reranking          │              │
│  │  • Document-order sorting               │              │
│  └───────┬─────────────────────────────────┘              │
│          │                                                  │
│  ┌───────▼─────────────────────────────────┐              │
│  │   Answer Generation Service             │              │
│  │  • OpenAI GPT-3.5/4                     │              │
│  │  • Constitutional prompt engineering    │              │
│  │  • Confidence scoring                   │              │
│  │  • Refusal logic                        │              │
│  └─────────────────────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
           │                            │
           ▼                            ▼
    ┌─────────────┐           ┌──────────────────┐
    │   Qdrant    │           │  OpenAI API      │
    │   Cloud     │           │  (Embeddings +   │
    │             │           │   Chat)          │
    └─────────────┘           └──────────────────┘
```

## Technology Stack

- **Framework**: FastAPI 0.115.6
- **Language Models**: OpenAI GPT-3.5-turbo / GPT-4
- **Embeddings**: OpenAI text-embedding-3-small (1536 dims)
- **Vector Database**: Qdrant Cloud (HNSW index)
- **Optional Logging**: Neon Serverless Postgres
- **Chunking**: LangChain MarkdownTextSplitter
- **Configuration**: Pydantic Settings

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key with credits
- Qdrant Cloud account (free tier)
- (Optional) Neon Postgres for query logging

### Installation

1. **Clone and navigate**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Required environment variables**:
   ```env
   # Qdrant Cloud
   QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
   QDRANT_API_KEY=your_qdrant_api_key

   # OpenAI
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   OPENAI_CHAT_MODEL=gpt-3.5-turbo

   # Admin
   ADMIN_API_KEY=your_admin_secret_key
   ```

5. **Run the server**:
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access Swagger UI**:
   Open http://localhost:8000/docs

## Usage

### 1. Index Book Content

Place Markdown files in `backend/content/`:

```bash
backend/content/
├── chapter-1-introduction.md
├── chapter-2-rag-systems.md
└── chapter-3-deployment.md
```

Then index the content:

```bash
curl -X POST "http://localhost:8000/admin/index" \
  -H "X-API-Key: your_admin_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "content_dir": "content",
    "batch_size": 100
  }'
```

**Response**:
```json
{
  "success": true,
  "message": "Successfully indexed 45 chunks from 3 files",
  "stats": {
    "files_processed": 3,
    "chunks_created": 48,
    "chunks_embedded": 45,
    "chunks_indexed": 45
  }
}
```

### 2. Ask Questions (Book-Wide Mode)

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the optimal chunk size for RAG systems?",
    "mode": "book-wide"
  }'
```

**Response**:
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "answer": "The optimal chunk size for RAG systems is 500-1000 tokens with 100-200 tokens of overlap [ch2-sec2-p1]. This balance ensures semantic coherence while maintaining retrieval precision.",
  "sources": [
    {
      "passage_id": "ch2-sec2-p1",
      "chapter": "Chapter 2: RAG Systems",
      "section": "2.2 Chunking Strategies",
      "page": 1,
      "snippet": "Research and practice have shown that chunk sizes between 500-1000 tokens work well for most technical documentation..."
    }
  ],
  "refused": false,
  "confidence": 0.92,
  "latency_ms": 1250,
  "mode": "book-wide"
}
```

### 3. Ask Questions (Selected-Text Mode)

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the main concept in this text",
    "mode": "selected-text",
    "context": "RAG combines retrieval from a knowledge base with generative AI models. It helps reduce hallucinations by grounding answers in retrieved context."
  }'
```

**Response**:
```json
{
  "query_id": "650e8400-e29b-41d4-a716-446655440001",
  "answer": "The main concept is Retrieval-Augmented Generation (RAG), which combines retrieval-based and generation-based approaches [selected-text]. RAG reduces hallucinations by grounding model outputs in retrieved evidence rather than relying solely on training data.",
  "sources": [
    {
      "passage_id": "selected-text",
      "chapter": "User-Selected Text",
      "section": "User Selection",
      "page": null,
      "snippet": "RAG combines retrieval from a knowledge base with generative AI models..."
    }
  ],
  "refused": false,
  "confidence": 0.88,
  "latency_ms": 980,
  "mode": "selected-text"
}
```

## API Reference

### Chat Endpoints

#### POST `/chat`
Ask a question using RAG.

**Request Body**:
```typescript
{
  query: string;           // User question (1-2000 chars)
  mode: "book-wide" | "selected-text";
  context?: string;        // Required for selected-text mode
  session_id?: UUID;       // Optional session tracking
}
```

**Response**:
```typescript
{
  query_id: UUID;
  answer: string;
  sources: Source[];
  refused: boolean;
  refusal_reason?: string;
  confidence?: number;     // 0.0-1.0
  latency_ms: number;
  mode: "book-wide" | "selected-text";
}
```

### Admin Endpoints (Require X-API-Key Header)

#### POST `/admin/index`
Index book content from Markdown files.

**Request**:
```json
{
  "content_dir": "content",
  "batch_size": 100
}
```

#### GET `/admin/stats`
Get indexing statistics.

**Response**:
```json
{
  "collection_name": "book-chunks",
  "total_chunks": 45,
  "vectors_count": 45,
  "status": "green",
  "optimizer_status": "ok"
}
```

#### POST `/admin/search-test`
Test semantic search.

**Request**:
```json
{
  "query": "What is RAG?",
  "limit": 5
}
```

#### DELETE `/admin/collection?confirm=true`
Delete all indexed content (requires confirm=true).

### Health Endpoints

#### GET `/`
API information.

#### GET `/health`
Health check with Qdrant status.

## Configuration

### Chunking
- **CHUNK_SIZE**: 800 tokens (range: 100-2000)
- **CHUNK_OVERLAP**: 100 tokens (range: 0-500)

### Retrieval
- **TOP_K_RETRIEVAL**: 10 candidates (range: 1-50)
- **TOP_K_RERANK**: 5 final chunks (range: 1-20)
- **SIMILARITY_THRESHOLD**: 0.7 (range: 0.0-1.0)

### Generation
- **CONFIDENCE_THRESHOLD**: 0.6 (range: 0.0-1.0)
- **OPENAI_CHAT_MODEL**: gpt-3.5-turbo or gpt-4
- **Temperature**: 0.0 (deterministic)

### Performance
- **MAX_CONCURRENT_REQUESTS**: 100
- **REQUEST_TIMEOUT_SEC**: 30

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   ├── dependencies.py      # API key auth
│   │   ├── middleware/          # Error handling, logging
│   │   └── routes/
│   │       ├── chat.py          # Chat endpoint
│   │       └── admin.py         # Admin endpoints
│   ├── models/
│   │   ├── chunk.py             # Chunk with embedding
│   │   ├── query.py             # Query with mode
│   │   ├── response.py          # Response with sources
│   │   └── source.py            # Citation model
│   ├── services/
│   │   ├── content_extractor.py        # Markdown processing
│   │   ├── chunking_service.py         # Text chunking
│   │   ├── indexing_service.py         # Full pipeline
│   │   ├── retrieval_service.py        # Semantic search
│   │   └── answer_generation_service.py # OpenAI generation
│   ├── utils/
│   │   ├── qdrant_client.py     # Qdrant wrapper
│   │   ├── chunking.py          # Chunking utilities
│   │   └── validation.py        # Input validation
│   └── config.py                # Pydantic settings
├── content/                     # Book markdown files
├── sql/
│   └── schema.sql               # Neon Postgres schema
├── requirements.txt
├── pyproject.toml
└── .env
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/ --line-length 100
flake8 src/ --max-line-length 100
mypy src/ --strict
```

### Database Migrations
If using Neon Postgres logging:
```bash
psql $NEON_DATABASE_URL -f sql/schema.sql
```

## Troubleshooting

### OpenAI API Errors
- **Error 404 (model_not_found)**: Update to gpt-3.5-turbo if no GPT-4 access
- **Error 429 (insufficient_quota)**: Add credits to OpenAI account

### Qdrant Errors
- **Connection errors**: Verify QDRANT_URL and QDRANT_API_KEY
- **Collection not found**: Run POST /admin/index first

### Empty Retrieval Results
- **No chunks indexed**: Check content/ directory has .md files
- **Similarity too high**: Lower SIMILARITY_THRESHOLD in .env

## Production Deployment

### Security
- Use strong ADMIN_API_KEY (32+ random characters)
- Enable HTTPS (Uvicorn behind nginx/Caddy)
- Rate limit endpoints (e.g., 100 req/min per IP)
- Validate CORS origins in production

### Scaling
- Use Redis for caching embeddings
- Deploy multiple Uvicorn workers
- Use Qdrant Cloud auto-scaling
- Monitor with Prometheus + Grafana

### Monitoring
- Enable ENABLE_LOGGING=true for query analytics
- Track latency_ms p95/p99 metrics
- Monitor refused query rates
- Set up alerts for API errors

## License

This project is built for educational purposes as part of the AI-Native Software Development Book.

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code is formatted with Black
- Type hints are complete
- Documentation is updated

---

**Built with ❤️ using FastAPI, OpenAI, and Qdrant**
