# Data Model: RAG Chatbot

**Date**: 2025-12-15
**Purpose**: Define entities, relationships, and validation rules for the RAG chatbot system

## Core Entities

### 1. Chunk

**Purpose**: Represents a semantically coherent segment of book content with embedding and metadata

**Fields**:
- `id` (UUID): Unique identifier for the chunk
- `text` (str, 100-2000 chars): The actual text content of the chunk
- `embedding` (List[float], 1536 dims): Vector embedding from OpenAI text-embedding-3-small
- `chapter` (str): Chapter title or number (e.g., "Chapter 3: RAG Systems")
- `section` (str): Section title (e.g., "3.2 Retrieval Strategies")
- `page` (int, optional): Page number in the book (if available)
- `passage_id` (str): Human-readable identifier (e.g., "ch3-sec2-p45")
- `source_file` (str): Original Markdown file path (e.g., "content/chapter-3.md")
- `created_at` (datetime): Timestamp when chunk was indexed

**Relationships**:
- One chunk may appear in multiple `Response.sources` (many-to-many via sources array)

**Validation Rules**:
- `text` must not be empty and must be valid UTF-8
- `embedding` must have exactly 1536 dimensions
- `passage_id` must be unique across all chunks
- `chapter` and `section` must not be empty

**Storage**:
- Qdrant: `embedding`, `text`, `chapter`, `section`, `page`, `passage_id`, `source_file` (as payload)
- Neon Postgres: Optional metadata table for chunk statistics (not required for MVP)

**Example**:
```python
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "The optimal chunk size for technical documentation is 500-1000 tokens with 100-token overlap. This preserves context while avoiding information dilution.",
  "embedding": [0.023, -0.041, ...],  # 1536 dims
  "chapter": "Chapter 3: RAG Systems",
  "section": "3.2 Retrieval Strategies",
  "page": 45,
  "passage_id": "ch3-sec2-p45",
  "source_file": "content/chapter-3.md",
  "created_at": "2025-12-15T10:30:00Z"
}
```

---

### 2. Query

**Purpose**: Represents a user question or request to the chatbot

**Fields**:
- `id` (UUID): Unique identifier for the query
- `session_id` (UUID, optional): Links to a conversation session (for multi-turn, future)
- `text` (str, 1-500 chars): The user's question or prompt
- `mode` (enum: "selected-text" | "book-wide"): Retrieval mode
- `context` (str, optional): User-selected text (required if mode=selected-text)
- `timestamp` (datetime): When the query was submitted

**Relationships**:
- One query has one `Response` (one-to-one)
- One query may belong to one `Session` (many-to-one, future)

**Validation Rules**:
- `text` must not be empty and must be <= 500 chars
- `mode` must be exactly "selected-text" or "book-wide"
- If `mode="selected-text"`, `context` must be provided and non-empty
- If `mode="book-wide"`, `context` should be null or ignored

**State Transitions**:
- Created → Processed (when response generated)
- Processed → Logged (when stored in Neon Postgres, if logging enabled)

**Storage**:
- Neon Postgres: `queries` table (if logging enabled)

**Example**:
```python
# Book-wide mode
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "session_id": None,
  "text": "What is the optimal chunk size for RAG systems?",
  "mode": "book-wide",
  "context": None,
  "timestamp": "2025-12-15T14:22:00Z"
}

# Selected-text mode
{
  "id": "660e8400-e29b-41d4-a716-446655440002",
  "session_id": None,
  "text": "Explain this chunking approach",
  "mode": "selected-text",
  "context": "The optimal chunk size for technical documentation is 500-1000 tokens with 100-token overlap.",
  "timestamp": "2025-12-15T14:25:00Z"
}
```

---

### 3. Response

**Purpose**: Represents the chatbot's answer to a query, including sources and metadata

**Fields**:
- `id` (UUID): Unique identifier for the response
- `query_id` (UUID): Links to the originating query
- `answer` (str): The generated answer text
- `sources` (List[Source]): Array of source citations (see Source sub-entity below)
- `confidence` (float, 0.0-1.0, optional): Generation confidence score
- `refused` (bool): True if the chatbot refused to answer (insufficient context)
- `refusal_reason` (str, optional): Explanation for refusal (e.g., "similarity < 0.7")
- `latency_ms` (int): End-to-end latency (retrieval + generation) in milliseconds
- `timestamp` (datetime): When the response was generated

**Relationships**:
- One response belongs to one `Query` (one-to-one)
- One response references multiple `Chunk` objects via `sources` (many-to-many)

**Validation Rules**:
- `answer` must not be empty if `refused=false`
- `answer` must be the standard refusal message if `refused=true`
- `sources` must be a non-empty array if `refused=false`
- `sources` should be empty if `refused=true`
- `confidence` must be in [0.0, 1.0] if provided
- `latency_ms` must be positive

**Storage**:
- Neon Postgres: `responses` table (if logging enabled)
- Not stored in Qdrant

**Example**:
```python
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "query_id": "660e8400-e29b-41d4-a716-446655440001",
  "answer": "The optimal chunk size for technical documentation in RAG systems is 500-1000 tokens with 100-token overlap. This range preserves comprehension context while avoiding information dilution.",
  "sources": [
    {
      "passage_id": "ch3-sec2-p45",
      "chapter": "Chapter 3: RAG Systems",
      "section": "3.2 Retrieval Strategies",
      "page": 45,
      "snippet": "The optimal chunk size for technical documentation is 500-1000 tokens with 100-token overlap."
    }
  ],
  "confidence": 0.92,
  "refused": False,
  "refusal_reason": None,
  "latency_ms": 1450,
  "timestamp": "2025-12-15T14:22:02Z"
}
```

---

### 4. Source (Sub-entity)

**Purpose**: Represents a citation to a specific chunk used in the response

**Fields**:
- `passage_id` (str): Identifier of the source chunk (references Chunk.passage_id)
- `chapter` (str): Chapter title
- `section` (str): Section title
- `page` (int, optional): Page number
- `snippet` (str, 50-200 chars): Brief excerpt from the chunk for preview

**Validation Rules**:
- `passage_id` must reference a valid chunk in Qdrant
- `snippet` should be a substring of the original chunk text
- `snippet` should be <= 200 chars (truncate with "..." if needed)

**Example**:
```python
{
  "passage_id": "ch3-sec2-p45",
  "chapter": "Chapter 3: RAG Systems",
  "section": "3.2 Retrieval Strategies",
  "page": 45,
  "snippet": "The optimal chunk size for technical documentation is 500-1000 tokens..."
}
```

---

### 5. Session (Future)

**Purpose**: Tracks multi-turn conversations for context persistence

**Fields**:
- `id` (UUID): Unique identifier for the session
- `user_id` (str, optional): Identifier for authenticated users (future)
- `created_at` (datetime): When the session started
- `last_active` (datetime): Last interaction timestamp
- `conversation_history` (List[UUID]): Ordered list of query IDs in this session

**Relationships**:
- One session has many `Query` objects (one-to-many)

**Validation Rules**:
- `conversation_history` should be ordered by timestamp
- Sessions expire after 30 minutes of inactivity (configurable)

**Storage**:
- Neon Postgres: `sessions` table (deferred for MVP)

**State Transitions**:
- Active → Inactive (30 min timeout)
- Inactive → Archived (deleted after 90 days)

**Note**: Session support is deferred for MVP. Initial implementation is stateless (single-turn Q&A).

---

## Entity Relationships

```
Query (1) ←→ (1) Response
  ↓
  └─ (0..1) Session (future)

Response (1) ←→ (N) Source
  ↓
  └─ references Chunk via passage_id

Chunk: standalone entity (no direct relationships)
```

---

## Validation Rules Summary

| Entity | Key Validation |
|--------|----------------|
| Chunk | passage_id unique, embedding 1536 dims, text non-empty |
| Query | mode in {selected-text, book-wide}, context required if selected-text |
| Response | answer non-empty if not refused, sources non-empty if not refused |
| Source | passage_id references valid chunk, snippet <= 200 chars |
| Session | Deferred for MVP |

---

## Storage Mapping

| Entity | Qdrant | Neon Postgres |
|--------|--------|---------------|
| Chunk | ✅ (vectors + payload) | ❌ (optional metadata only) |
| Query | ❌ | ✅ (if logging enabled) |
| Response | ❌ | ✅ (if logging enabled) |
| Source | ❌ | ✅ (embedded in Response JSON) |
| Session | ❌ | ✅ (deferred) |

---

## Indexing Strategy

### Qdrant Indexes
- Primary index: HNSW on 1536-dim embeddings (cosine similarity)
- Metadata indexes: payload filtering on `chapter`, `section`, `page` (future scoped search)

### Neon Postgres Indexes
- `queries.timestamp` (B-tree): for time-range queries
- `responses.query_id` (B-tree): for join optimization
- `responses.refused` (B-tree): for analytics on refusal rates

---

## Future Extensions

1. **Multi-turn Sessions**: Implement `Session` entity with conversation history
2. **User Preferences**: Store user-specific settings (e.g., preferred citation format)
3. **Feedback**: Add `Feedback` entity for user ratings on answer quality
4. **Chunk Versioning**: Track book updates and chunk version history
5. **Scoped Search**: Use Qdrant payload filtering for chapter/section-scoped queries
