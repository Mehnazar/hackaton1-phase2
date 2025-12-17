# Research: RAG Chatbot Implementation

**Date**: 2025-12-15
**Purpose**: Resolve technical unknowns and establish best practices for RAG chatbot implementation

## Research Areas

### 1. Chunking Strategy for Book Content

**Decision**: Semantic chunking with section boundary preservation

**Rationale**:
- Book content has natural section boundaries (chapters, sections, subsections)
- Splitting mid-explanation breaks comprehension context
- Optimal chunk size: 500-1000 tokens with 100-token overlap
- Preserve Markdown heading hierarchy to maintain document structure

**Chunking Algorithm**:
1. Parse Markdown to identify section boundaries (# headers)
2. Split content at section boundaries when section exceeds max chunk size
3. For long sections: split at paragraph boundaries with overlap
4. Include section metadata (chapter, section title, page number) in chunk metadata
5. Avoid splitting code blocks, tables, or lists

**Alternatives Considered**:
- Fixed-size chunking (512 tokens): Rejected - breaks context mid-sentence
- Sentence-based chunking: Rejected - doesn't respect semantic boundaries
- Recursive character splitting: Rejected - ignores document structure

**Implementation**: Use LangChain's `MarkdownTextSplitter` with custom header splitting logic

### 2. Embedding Model Selection

**Decision**: OpenAI `text-embedding-3-small` (1536 dimensions)

**Rationale**:
- Strong performance on technical/academic content
- Cost-effective ($0.02 per 1M tokens)
- Lower dimensionality than `text-embedding-3-large` (3072 dims) reduces Qdrant storage
- Sufficient for book-scale corpus (~200K tokens → ~10K chunks)
- Qdrant Free Tier (1M vectors) easily accommodates 1536-dim embeddings

**Cost Estimation**:
- Book size: ~200K tokens
- Embedding cost: ~$0.004 (one-time indexing)
- Re-indexing on updates: minimal cost

**Alternatives Considered**:
- `text-embedding-3-large`: Rejected - higher cost, unnecessary for this scale
- `text-embedding-ada-002`: Rejected - older model, slightly lower quality
- Open-source models (Sentence Transformers): Rejected - requires self-hosting, lower quality on technical content

### 3. Retrieval Strategy and Context Window Management

**Decision**: Top-5 semantic retrieval with reranking by section proximity

**Rationale**:
- Top-5 chunks balance context richness and noise reduction
- Qdrant HNSW search provides fast approximate nearest neighbors
- Rerank by section proximity: chunks from same chapter/section ranked higher
- Total context window: ~2500-5000 tokens (fits within OpenAI context limits)

**Retrieval Pipeline**:
1. Generate query embedding using same model (`text-embedding-3-small`)
2. Query Qdrant for top-10 candidates (cosine similarity)
3. Rerank by metadata: boost chunks from same chapter/section
4. Select top-5 reranked chunks
5. Sort by document order (page/section sequence) for coherent presentation

**Alternatives Considered**:
- Top-3 retrieval: Rejected - insufficient context for complex questions
- Top-10 retrieval: Rejected - dilutes context, increases latency
- Maximal Marginal Relevance (MMR): Rejected - adds complexity, minimal benefit for book content

### 4. Refusal Logic and Confidence Thresholds

**Decision**: Multi-gate refusal logic with similarity threshold and generation confidence

**Rationale**:
- Similarity threshold (cosine > 0.7): Ensures retrieved chunks are relevant
- Generation confidence: OpenAI Agents returns low confidence when context insufficient
- Explicit refusal message: "This information cannot be verified from the book content."

**Refusal Gates**:
1. **Retrieval Gate**: If top-1 similarity < 0.7 → refuse immediately
2. **Context Sufficiency Gate**: If retrieved chunks don't contain keywords from query → warn user
3. **Generation Confidence Gate**: If OpenAI Agents confidence < 0.6 → refuse
4. **Hallucination Detection Gate** (future): Compare generated answer against retrieved chunks for unsupported claims

**Threshold Calibration**:
- Start with conservative thresholds (0.7 similarity, 0.6 confidence)
- Monitor false refusal rate (questions that should be answerable but are refused)
- Adjust thresholds based on evaluation metrics (precision/recall of refusals)

**Alternatives Considered**:
- Single similarity threshold only: Rejected - doesn't catch generation hallucinations
- LLM-based verifier: Considered for future - adds latency and cost
- No refusal logic: Rejected - violates constitution

### 5. Selected-Text Mode Implementation

**Decision**: Client-side text selection capture with retrieval bypass flag

**Rationale**:
- Browser `window.getSelection()` API captures user-selected text
- Frontend sends selected text + bypass flag to backend
- Backend skips Qdrant retrieval when bypass=true
- Generation uses only provided text as context

**Implementation Flow**:
1. User selects text in Docusaurus page
2. Frontend captures selection on "Ask about this text" button click
3. POST /chat with `{"query": "...", "mode": "selected-text", "context": "<selected text>"}`
4. Backend validates mode, skips retrieval, generates answer from context only
5. Response includes citation to selection (character offset or passage ID)

**Mode Enforcement**:
- `mode="selected-text"`: context must be provided, retrieval disabled
- `mode="book-wide"`: context ignored, retrieval enabled
- Validation error if mode/context mismatch

**Alternatives Considered**:
- Server-side selection parsing: Rejected - requires full book HTML on backend
- Hybrid mode (selection + retrieval): Rejected - violates constitutional mode separation

### 6. Citation and Source Traceability

**Decision**: Structured citation metadata with passage IDs and section references

**Rationale**:
- Every chunk has metadata: `{chapter, section, page, passage_id, source_file}`
- Response includes `sources: [{passage_id, chapter, section, page, text_snippet}]`
- Frontend renders clickable citations linking to book sections
- Users can verify claims by navigating to source passages

**Citation Format**:
```json
{
  "answer": "...",
  "sources": [
    {
      "passage_id": "ch3-sec2-p45",
      "chapter": "Chapter 3: RAG Systems",
      "section": "3.2 Retrieval Strategies",
      "page": 45,
      "snippet": "The optimal chunk size for technical documentation is 500-1000 tokens..."
    }
  ]
}
```

**Frontend Rendering**:
- Inline citations: `[1]`, `[2]` with footnotes
- Hover tooltip: shows snippet preview
- Click: scrolls to source passage in book

**Alternatives Considered**:
- Plain text citations: Rejected - not machine-readable
- No citations: Rejected - violates traceability principle
- Full chunk text in response: Rejected - bloats response size

### 7. OpenAI Agents vs ChatKit SDK

**Decision**: Use OpenAI Agents SDK for initial implementation; evaluate ChatKit later

**Rationale**:
- OpenAI Agents SDK provides lower-level control over retrieval and generation
- Easier to implement custom grounding and refusal logic
- ChatKit SDK is higher-level, may abstract away needed controls
- Can migrate to ChatKit later if it supports required customization

**OpenAI Agents Integration**:
- Define tools: `search_book(query)`, `get_passage(passage_id)`
- Agent prompt enforces grounding: "Only answer using provided passages. If context insufficient, respond with refusal message."
- Function calling ensures structured tool invocation

**ChatKit Evaluation Criteria** (for future migration):
- Supports custom retrieval backends (Qdrant)
- Allows custom grounding validation logic
- Supports mode switching (selected-text vs book-wide)
- Provides citation metadata in responses

### 8. Qdrant Collection Schema and Indexing

**Decision**: Single collection with metadata filtering

**Rationale**:
- One collection: `book-chunks` (simplifies management)
- Metadata fields: `chapter`, `section`, `page`, `passage_id`, `source_file`
- Qdrant payload filtering enables chapter/section scoped search (future feature)
- HNSW index parameters: `m=16, ef_construct=100` (balance speed/accuracy)

**Collection Schema**:
```json
{
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload_schema": {
    "chapter": "keyword",
    "section": "keyword",
    "page": "integer",
    "passage_id": "keyword",
    "source_file": "keyword",
    "text": "text"
  }
}
```

**Indexing Pipeline**:
1. Extract Markdown files from book source
2. Parse and chunk content (research.md section 1)
3. Generate embeddings (research.md section 2)
4. Batch upload to Qdrant (100 chunks per batch)
5. Create HNSW index (automatic on upload)
6. Verify indexing: query for sample passages

**Alternatives Considered**:
- Multiple collections per chapter: Rejected - over-engineering, harder to manage
- PostgreSQL pgvector: Rejected - Qdrant optimized for vector search
- Flat index: Rejected - slow at scale, HNSW better for 10K+ vectors

### 9. Neon Postgres Schema for Logs and Metadata

**Decision**: Minimal schema for interaction logs and session tracking

**Rationale**:
- Logs optional (opt-in for users)
- Stores: queries, responses, sources, timestamps, latency
- Enables debugging, performance monitoring, hallucination detection
- Session tracking for multi-turn conversations (future)

**Schema**:
```sql
CREATE TABLE queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID,
  query_text TEXT NOT NULL,
  mode VARCHAR(20) NOT NULL, -- 'selected-text' or 'book-wide'
  context_text TEXT, -- selected text if mode=selected-text
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_id UUID REFERENCES queries(id),
  answer_text TEXT NOT NULL,
  sources JSONB NOT NULL, -- array of source citations
  confidence FLOAT,
  refused BOOLEAN DEFAULT FALSE,
  latency_ms INTEGER,
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(255), -- optional, for authenticated users
  created_at TIMESTAMP DEFAULT NOW(),
  last_active TIMESTAMP DEFAULT NOW()
);
```

**Privacy**:
- No PII stored by default
- User opt-in required for logging
- Queries anonymized (no user identifiers unless authenticated)
- Retention policy: 90 days (configurable)

**Alternatives Considered**:
- No logging: Rejected - needed for debugging and evaluation
- File-based logging: Rejected - harder to query and analyze
- Full conversation history: Deferred - implement later if multi-turn needed

### 10. Error Handling and Graceful Degradation

**Decision**: Tiered degradation with informative error messages

**Rationale**:
- Qdrant failure: return cached responses or defer to manual search
- Neon Postgres failure: disable logging, continue serving requests
- OpenAI API failure: retry with exponential backoff, then refuse
- Embedding API failure: block requests (cannot retrieve without embeddings)

**Error Response Format**:
```json
{
  "error": true,
  "message": "Retrieval service temporarily unavailable. Please try again.",
  "code": "RETRIEVAL_UNAVAILABLE",
  "retry_after": 30
}
```

**Monitoring**:
- Log all errors to Neon Postgres (if available) or stdout
- Track error rates: Qdrant timeouts, OpenAI rate limits, embedding failures
- Alert on Free Tier quota exhaustion (Qdrant 1M vectors)

**Alternatives Considered**:
- Fail fast on any error: Rejected - poor user experience
- Silent failures: Rejected - violates transparency principle
- Local fallback embeddings: Rejected - inconsistent with primary embeddings

## Summary of Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| Chunking | Semantic (500-1000 tokens, section boundaries) | Preserves comprehension context |
| Embeddings | OpenAI text-embedding-3-small (1536 dims) | Cost-effective, strong quality |
| Retrieval | Top-5 with section proximity reranking | Balances context and noise |
| Refusal | Multi-gate (similarity + confidence) | Enforces grounding rigorously |
| Selected-Text | Client-side capture + retrieval bypass | Constitutional mode enforcement |
| Citations | Structured metadata with passage IDs | Traceability and verifiability |
| Orchestration | OpenAI Agents SDK | Granular control over grounding |
| Qdrant | Single collection, HNSW index | Simplicity and performance |
| Neon Postgres | Minimal logging schema | Debugging without bloat |
| Error Handling | Tiered degradation | Availability with transparency |

## Next Steps

Proceed to Phase 1: Design
- Generate data-model.md (entities: Chunk, Query, Response, Session)
- Generate contracts/ (OpenAPI for FastAPI endpoints)
- Generate quickstart.md (setup, indexing, querying workflows)
