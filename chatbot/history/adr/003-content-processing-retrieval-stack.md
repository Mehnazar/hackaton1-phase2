# ADR-003: Content Processing and Retrieval Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-15
- **Feature:** 001-rag-chatbot
- **Context:** The RAG system requires a complete pipeline from raw book content (Markdown) to retrievable vectors. This pipeline must preserve comprehension context (constitutional Principle I: Grounded Accuracy), maintain section boundaries, and operate within Qdrant Free Tier limits (1 GB storage, 1M vectors). The retrieval strategy must balance precision (retrieval relevance) and recall (sufficient context) while meeting latency requirements (<3 seconds end-to-end).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core data pipeline
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Multiple chunking/embedding/retrieval strategies
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects indexing, storage, retrieval, generation
-->

## Decision

Implement an integrated **Content Processing and Retrieval Stack** with the following components:

**1. Semantic Chunking (500-1000 tokens, section boundaries)**
- Algorithm: LangChain `MarkdownTextSplitter` with custom header logic
- Chunk size: 800 tokens (target), 100-token overlap
- Boundary preservation: Split at Markdown headers (# ## ###) when possible
- Avoid splitting: code blocks, tables, lists (maintain semantic units)
- Metadata: chapter, section, page, passage_id, source_file

**2. Embedding Generation (OpenAI text-embedding-3-small, 1536 dims)**
- Model: `text-embedding-3-small` (1536 dimensions)
- Cost: $0.02 per 1M tokens (~$0.004 for 200K token book)
- Batch processing: 100 chunks per API call
- Storage: 1536-dim vectors fit well within Qdrant Free Tier

**3. Vector Indexing (Qdrant Cloud, HNSW)**
- Collection: Single `book-chunks` collection
- Index: HNSW (m=16, ef_construct=100) for fast approximate search
- Distance: Cosine similarity (normalized embeddings)
- Payload: text, chapter, section, page, passage_id, source_file

**4. Retrieval Strategy (Top-5 with section proximity reranking)**
- Step 1: Query Qdrant for top-10 candidates (cosine similarity)
- Step 2: Rerank by section proximity (boost chunks from same chapter/section)
- Step 3: Select top-5 reranked chunks
- Step 4: Sort by document order (page/section sequence)
- Total context: ~2500-5000 tokens (fits OpenAI context window)

## Consequences

### Positive

- **Context preservation**: Section-aware chunking maintains comprehension (constitutional requirement)
- **Cost-effective**: text-embedding-3-small balances quality and cost ($0.004 vs $0.02+ for larger models)
- **Free Tier compliance**: 1536-dim embeddings + 10K chunks << 1M vector limit
- **Fast retrieval**: HNSW index provides <200ms p95 latency on Qdrant Cloud
- **Section coherence**: Reranking by proximity keeps related chunks together
- **Document order**: Sorting by sequence prevents disjointed context
- **Scalability**: Single collection handles entire book (~500 pages, 200K tokens)

### Negative

- **Chunking complexity**: Section-aware splitting requires Markdown parsing logic
- **Overlap redundancy**: 100-token overlap increases storage (~10% overhead)
- **Reranking latency**: Additional ~50-100ms for reranking top-10 to top-5
- **Fixed thresholds**: 500-1000 token chunks may not suit all content types
- **Embedding model lock-in**: Changing models requires full re-indexing
- **Top-K tuning**: Top-5 may be insufficient for complex questions (vs top-10)

## Alternatives Considered

**Alternative 1: Fixed-Size Chunking (512 tokens, no overlap)**
- Approach: Split at fixed 512-token boundaries, no Markdown awareness
- Why rejected:
  - Breaks context mid-sentence or mid-paragraph
  - Ignores semantic structure (chapters, sections)
  - Higher false refusal rate (relevant info split across chunks)
  - Violates constitutional context preservation requirement

**Alternative 2: Larger Embedding Model (text-embedding-3-large, 3072 dims)**
- Approach: Use higher-quality but more expensive embedding model
- Why rejected:
  - Higher cost ($0.13 per 1M tokens vs $0.02)
  - Larger storage footprint (3072 dims vs 1536 dims)
  - Marginal quality improvement for book-scale corpus
  - Qdrant Free Tier limit reached sooner (fewer chunks)

**Alternative 3: Top-10 Retrieval (no reranking)**
- Approach: Return top-10 chunks directly without section proximity reranking
- Why rejected:
  - Dilutes context (10 chunks = ~5000-10000 tokens, too noisy)
  - Higher latency (more chunks to process in generation)
  - Lower precision (irrelevant chunks not filtered out)
  - Worse user experience (longer, less focused answers)

**Alternative 4: Sentence-Based Chunking**
- Approach: Split at sentence boundaries using spaCy or NLTK
- Why rejected:
  - Doesn't respect Markdown structure (sections, headings)
  - Sentences too small (poor retrieval granularity)
  - Requires NLP library (dependency overhead)
  - Slower than Markdown parsing

**Alternative 5: PostgreSQL pgvector (instead of Qdrant)**
- Approach: Use Neon Postgres with pgvector extension for embeddings
- Why rejected:
  - Qdrant optimized for vector search (HNSW index faster than pgvector IVFFlat)
  - Neon Postgres better suited for metadata/logs (not primary vector storage)
  - Qdrant Free Tier sufficient for book-scale corpus
  - Separation of concerns (vectors in Qdrant, metadata in Neon)

## References

- Feature Spec: specs/001-rag-chatbot/spec.md (not yet created)
- Implementation Plan: specs/001-rag-chatbot/plan.md (lines 208-218: Research Summary)
- Research: specs/001-rag-chatbot/research.md (Sections 1-3, 8: Chunking, Embeddings, Retrieval, Qdrant Schema)
- Qdrant Schema: specs/001-rag-chatbot/contracts/qdrant-schema.json
- Constitution: .specify/memory/constitution.md (Principle I: Grounded Accuracy; Architecture Constraints: Retrieval)
- Related ADRs: ADR-001 (RAG Architecture), ADR-005 (Technology Stack)
- Evaluator Evidence: history/prompts/001-rag-chatbot/002-implementation-plan-rag-chatbot.plan.prompt.md
