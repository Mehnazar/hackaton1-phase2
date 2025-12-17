# ADR-005: Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-15
- **Feature:** 001-rag-chatbot
- **Context:** The RAG chatbot requires an integrated technology stack covering backend API, orchestration, vector storage, metadata/logging, and frontend UI. The constitution mandates specific technologies (FastAPI, Qdrant Cloud, Neon Postgres, OpenAI Agents/ChatKit SDK) while allowing flexibility in frontend choices. The stack must operate within Free Tier limits (Qdrant 1 GB, Neon Serverless), support <3 seconds latency, and enable constitutional compliance (grounding, traceability, refusal).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Foundation for all development
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Multiple framework/stack combinations
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all layers (backend, storage, frontend)
-->

## Decision

Adopt the following **integrated technology stack**:

**Backend API Layer**
- Framework: **FastAPI** (Python 3.11+)
- API specification: OpenAPI 3.0 (auto-generated from FastAPI)
- Testing: pytest, pytest-asyncio, httpx
- Deployment: Cloud platform (Render, Fly.io, or AWS Lambda)

**Orchestration and Generation**
- SDK: **OpenAI Agents SDK** (initial implementation)
- LLM: GPT-4 or GPT-4-Turbo for generation
- Function calling: Structured tool invocation (search_book, get_passage)
- Future migration path: ChatKit SDK (if requirements met)

**Vector Storage**
- Service: **Qdrant Cloud Free Tier**
- Limits: 1 GB storage, 1M vectors
- Index: HNSW (m=16, ef_construct=100)
- Client: Qdrant Python client

**Metadata and Logging**
- Service: **Neon Serverless Postgres**
- Schema: Minimal (queries, responses, sessions)
- Opt-in: Logging disabled by default (user consent required)
- Client: psycopg2 or asyncpg

**Embedding Generation**
- Model: **OpenAI text-embedding-3-small** (1536 dims)
- API: OpenAI Embeddings API
- Cost: $0.02 per 1M tokens

**Frontend UI**
- Framework: **ChatKit SDK** (OpenAI official UI components)
- Integration: Embedded in Docusaurus book layout
- Text selection: Native browser `window.getSelection()` API
- State management: React hooks (useChat, useTextSelection)

## Consequences

### Positive

- **Constitutional compliance**: All mandated technologies used (FastAPI, Qdrant, Neon, OpenAI)
- **Free Tier viability**: Qdrant (1M vectors) and Neon (Serverless) sufficient for book-scale corpus
- **Fast development**: FastAPI auto-generates OpenAPI docs; ChatKit provides pre-built UI
- **Python ecosystem**: Rich libraries for NLP, chunking (LangChain), testing (pytest)
- **Strong typing**: FastAPI + Pydantic enable type-safe API contracts
- **Low cost**: Free Tier for storage, minimal API costs (~$0.004 for embeddings)
- **OpenAI integration**: Official SDKs for Agents, Embeddings, ChatKit (consistent API)

### Negative

- **Vendor lock-in**: Heavy reliance on OpenAI (Agents, Embeddings, LLM) and Qdrant Cloud
- **Free Tier limits**: Must monitor Qdrant 1M vector limit and Neon storage
- **Python deployment**: Requires containerization or serverless platform (vs static site)
- **OpenAI Agents complexity**: Lower-level than ChatKit, more code to write
- **ChatKit uncertainty**: Not yet confirmed if ChatKit supports required customization (grounding, refusal)
- **Multi-service architecture**: Requires orchestration across FastAPI + Qdrant + Neon + OpenAI

## Alternatives Considered

**Alternative 1: Flask + Sentence Transformers + PostgreSQL pgvector**
- Backend: Flask instead of FastAPI
- Embeddings: Open-source Sentence Transformers (self-hosted) instead of OpenAI
- Vector storage: PostgreSQL pgvector extension instead of Qdrant
- Why rejected:
  - Flask lacks FastAPI's auto-generated OpenAPI docs and async support
  - Sentence Transformers lower quality on technical content vs OpenAI embeddings
  - pgvector slower than Qdrant HNSW for 10K+ vectors
  - Self-hosting embeddings adds infrastructure complexity
  - Higher operational cost (hosting embedding model) vs OpenAI API (~$0.004)

**Alternative 2: LangChain + Pinecone + Firebase**
- Orchestration: LangChain instead of OpenAI Agents SDK
- Vector storage: Pinecone instead of Qdrant
- Metadata: Firebase Firestore instead of Neon Postgres
- Why rejected:
  - LangChain higher-level abstractions reduce control over grounding logic
  - Pinecone Free Tier smaller (1M vectors, 1 index) than Qdrant (1M vectors, unlimited collections)
  - Firebase Firestore NoSQL not ideal for relational queries (sessions, query logs)
  - Constitutional mandate specifies Qdrant and Neon

**Alternative 3: Next.js Full-Stack (API Routes + Vercel Edge Functions)**
- Backend: Next.js API routes instead of separate FastAPI service
- Deployment: Vercel Edge Functions (serverless)
- Why rejected:
  - Next.js API routes TypeScript/JavaScript (vs Python for LangChain, NLP libraries)
  - Vercel Edge Functions limited execution time (30s max) vs long-running indexing
  - Python ecosystem richer for RAG (LangChain, embeddings, chunking)
  - Separation of concerns: FastAPI backend can scale independently of frontend

**Alternative 4: Django + Chroma + SQLite**
- Backend: Django instead of FastAPI
- Vector storage: Chroma (embedded) instead of Qdrant Cloud
- Metadata: SQLite instead of Neon Postgres
- Why rejected:
  - Django heavier framework (ORM, admin, migrations) vs lightweight FastAPI
  - Chroma embedded mode not suitable for production (Qdrant Cloud more robust)
  - SQLite not suitable for concurrent writes (Neon Postgres better for multi-user)
  - Constitutional mandate specifies Qdrant and Neon

## References

- Feature Spec: specs/001-rag-chatbot/spec.md (not yet created)
- Implementation Plan: specs/001-rag-chatbot/plan.md (lines 14-24: Technical Context)
- Constitution: .specify/memory/constitution.md (Architecture Constraints: Technology Stack)
- Research: specs/001-rag-chatbot/research.md (Sections 2, 7, 8, 9: Embeddings, Orchestration, Qdrant, Neon)
- API Contract: specs/001-rag-chatbot/contracts/chatbot-api.yaml
- Qdrant Schema: specs/001-rag-chatbot/contracts/qdrant-schema.json
- Quickstart: specs/001-rag-chatbot/quickstart.md (Setup and deployment)
- Related ADRs: ADR-001 (RAG Architecture), ADR-003 (Content Processing and Retrieval Stack)
- Evaluator Evidence: history/prompts/001-rag-chatbot/002-implementation-plan-rag-chatbot.plan.prompt.md
