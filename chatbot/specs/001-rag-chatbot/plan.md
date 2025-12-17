# Implementation Plan: RAG Chatbot for AI-Native Software Development Book

**Branch**: `001-rag-chatbot` | **Date**: 2025-12-15 | **Spec**: [spec.md](./spec.md)
**Input**: User-provided phased implementation plan for RAG chatbot

**Note**: This plan follows the workflow defined in the constitution and implements strict grounding, mode enforcement, and traceability requirements.

## Summary

Build an integrated RAG (Retrieval-Augmented Generation) chatbot for the AI-Native Software Development Book that answers questions strictly grounded in book content or user-selected text. The chatbot operates in two modes: (1) book-wide retrieval using Qdrant vector search, and (2) selected-text-only analysis with retrieval disabled. All responses must be traceable to source passages, with deterministic refusal when evidence is insufficient.

Primary technical approach: FastAPI backend with OpenAI Agents SDK for orchestration, Qdrant Cloud for vector storage, Neon Serverless Postgres for metadata/logs, and ChatKit UI embedded in Docusaurus book layout.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, OpenAI Agents SDK (or ChatKit SDK), Qdrant Client, Neon Postgres Client, OpenAI Embeddings API
**Storage**: Qdrant Cloud Free Tier (vector storage), Neon Serverless Postgres (metadata, logs)
**Testing**: pytest, pytest-asyncio, httpx (for FastAPI testing)
**Target Platform**: Cloud-hosted backend (Linux server), browser-based frontend (Docusaurus integration)
**Project Type**: Web application (backend API + frontend UI integration)
**Performance Goals**: <3 seconds end-to-end latency (retrieval + generation), support 100+ concurrent users
**Constraints**: Qdrant Free Tier limits (1 GB storage, 1M vectors), <200ms p95 retrieval latency, zero hallucinations
**Scale/Scope**: Single book (~500 pages, ~200K tokens), 1K-10K chunks, 10-100 concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

**I. Grounded Accuracy**
- [ ] All responses derived strictly from retrieved or selected text
- [ ] No external knowledge or training data used
- [ ] Standard refusal message implemented: "This information cannot be verified from the book content."
- **Status**: ✅ PASS - Design enforces grounding through retrieval-only responses and explicit refusal logic

**II. Faithful Retrieval**
- [ ] Selected-text mode: retrieval disabled, reasoning restricted to user selection
- [ ] Book-wide mode: retrieval limited to Qdrant-indexed book chunks
- [ ] Fixed upper bound on retrieved context (top-5 chunks)
- **Status**: ✅ PASS - Two-mode architecture with explicit mode switching and retrieval controls

**III. Transparency and Traceability**
- [ ] Responses include source references (section, page, passage IDs)
- [ ] Retrieved context presented or summarized for verification
- [ ] No opaque reasoning chains
- **Status**: ✅ PASS - Citation metadata stored and returned with every response

**IV. Academic Rigor**
- [ ] Clear, precise explanations for technical audiences
- [ ] Neutral tone, no speculation
- [ ] Terminology consistent with book definitions
- **Status**: ✅ PASS - System prompt enforces academic tone and precision

**V. Deterministic Refusal**
- [ ] Explicit refusal when grounding fails
- [ ] No hedging or probabilistic statements
- [ ] No fallback to general knowledge
- **Status**: ✅ PASS - Confidence threshold and refusal logic implemented

### Architecture Constraints Compliance

**Technology Stack**
- [ ] OpenAI Agents SDK or ChatKit SDK for orchestration
- [ ] FastAPI for inference and retrieval
- [ ] Qdrant Cloud Free Tier for vector storage
- [ ] Neon Serverless Postgres for metadata and logs
- **Status**: ✅ PASS - All specified technologies used

**Retrieval Constraints**
- [ ] Semantic vector search only (no keyword/regex fallbacks)
- [ ] Fixed upper bound on retrieved context
- [ ] Chunk boundaries preserve comprehension context
- **Status**: ✅ PASS - Chunking strategy preserves section boundaries; top-K retrieval enforced

**Data Handling**
- [ ] No modification of book content at inference time
- [ ] User queries/logs stored only if enabled
- [ ] No PII stored without consent
- **Status**: ✅ PASS - Read-only book content; logging opt-in; no PII collection

**Performance and Reliability**
- [ ] Qdrant Free Tier limits respected (1 GB, 1M vectors)
- [ ] Graceful degradation on failures
- **Status**: ✅ PASS - Monitoring and error handling designed; Free Tier capacity sufficient

### Success Criteria Gates

**Grounding Validation**
- [ ] SC-001: Every response traceable to explicit passages
- [ ] SC-002: Zero hallucinated facts in evaluation
- [ ] SC-003: Consistent refusal behavior

**Mode Enforcement**
- [ ] SC-004: Selected-text mode never exceeds selection
- [ ] SC-005: Book-wide mode never uses external knowledge
- [ ] SC-006: Mode switching deterministic and user-controlled

**Accuracy and Precision**
- [ ] SC-007: >95% accuracy on evaluation set
- [ ] SC-008: Terminology consistent with book
- [ ] SC-009: No contradictory statements

**User Experience**
- [ ] SC-010: Source references verifiable
- [ ] SC-011: Academic tone and explanations
- [ ] SC-012: <3 seconds latency

**Operational Reliability**
- [ ] SC-013: Qdrant Free Tier compliance
- [ ] SC-014: Graceful error handling
- [ ] SC-015: Debugging logs sufficient

**Overall Gate Status**: ✅ PASS - No violations identified; design aligns with all constitutional requirements

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (chunking, embeddings, refusal logic)
├── data-model.md        # Phase 1 output (entities: Chunk, Query, Response, Session)
├── quickstart.md        # Phase 1 output (setup, indexing, querying)
├── contracts/           # Phase 1 output (OpenAPI specs)
│   ├── chatbot-api.yaml # FastAPI endpoints
│   └── qdrant-schema.json # Vector collection schema
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── chunk.py          # Chunk entity (text, embedding, metadata)
│   │   ├── query.py          # Query entity (text, mode, context)
│   │   ├── response.py       # Response entity (answer, sources, confidence)
│   │   └── session.py        # Session entity (conversation history)
│   ├── services/
│   │   ├── indexing.py       # Book content extraction and chunking
│   │   ├── embedding.py      # OpenAI embeddings generation
│   │   ├── retrieval.py      # Qdrant vector search
│   │   ├── generation.py     # OpenAI Agents answer generation
│   │   ├── grounding.py      # Grounding validation and refusal logic
│   │   └── citation.py       # Source reference formatting
│   ├── api/
│   │   ├── main.py           # FastAPI app initialization
│   │   ├── routes/
│   │   │   ├── chat.py       # Chat endpoint (POST /chat)
│   │   │   ├── health.py     # Health check (GET /health)
│   │   │   └── admin.py      # Admin endpoints (indexing, stats)
│   │   └── middleware/
│   │       ├── logging.py    # Request/response logging
│   │       └── errors.py     # Error handling
│   ├── config.py             # Environment config (Qdrant, Neon, OpenAI keys)
│   └── utils/
│       ├── chunking.py       # Chunking utilities (overlap, boundaries)
│       └── validation.py     # Input validation
└── tests/
    ├── contract/
    │   ├── test_chat_api.py      # Contract test: POST /chat
    │   ├── test_refusal.py       # Contract test: insufficient context
    │   └── test_mode_switching.py # Contract test: selected-text vs book-wide
    ├── integration/
    │   ├── test_end_to_end.py    # Full retrieval + generation flow
    │   ├── test_grounding.py     # Grounding validation tests
    │   └── test_qdrant_neon.py   # Qdrant + Neon integration
    └── unit/
        ├── test_chunking.py      # Chunking logic
        ├── test_retrieval.py     # Qdrant query logic
        └── test_citation.py      # Citation formatting

frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget.tsx        # ChatKit UI wrapper
│   │   ├── TextSelector.tsx      # Text selection capture
│   │   └── ModeToggle.tsx        # Book-wide vs selected-text toggle
│   ├── services/
│   │   └── api.ts                # Backend API client
│   └── hooks/
│       ├── useChat.ts            # Chat state management
│       └── useTextSelection.ts   # Text selection detection
└── tests/
    └── components/
        ├── ChatWidget.test.tsx
        └── TextSelector.test.tsx
```

**Structure Decision**: Web application structure chosen because the system requires a backend API (FastAPI) for retrieval/generation orchestration and a frontend UI (ChatKit) embedded in the Docusaurus book. Backend handles Qdrant/Neon interactions and OpenAI Agents; frontend captures user input, text selections, and displays responses.

## Complexity Tracking

No constitutional violations detected. All design decisions align with constitutional requirements.

---

## Phase 0: Research Summary

**Status**: ✅ COMPLETED

**Artifacts Generated**: `research.md`

**Key Decisions Made**:
1. **Chunking**: Semantic chunking (500-1000 tokens, section boundaries) using LangChain MarkdownTextSplitter
2. **Embeddings**: OpenAI text-embedding-3-small (1536 dims) for cost-effectiveness and quality
3. **Retrieval**: Top-5 semantic retrieval with section proximity reranking
4. **Refusal Logic**: Multi-gate (similarity threshold 0.7, confidence threshold 0.6)
5. **Selected-Text Mode**: Client-side capture with retrieval bypass
6. **Citations**: Structured metadata with passage IDs and source references
7. **Orchestration**: OpenAI Agents SDK (granular control over grounding)
8. **Qdrant Schema**: Single collection with HNSW index (m=16, ef_construct=100)
9. **Neon Schema**: Minimal logging (queries, responses, sessions)
10. **Error Handling**: Tiered degradation with informative error messages

All "NEEDS CLARIFICATION" items from Technical Context resolved.

---

## Phase 1: Design Summary

**Status**: ✅ COMPLETED

**Artifacts Generated**:
- `data-model.md`: Entities (Chunk, Query, Response, Source, Session)
- `contracts/chatbot-api.yaml`: OpenAPI 3.0 spec for FastAPI endpoints
- `contracts/qdrant-schema.json`: Qdrant collection schema
- `quickstart.md`: Setup, indexing, and querying workflows

**Core Entities Defined**:
1. **Chunk**: Book content segment with embedding and metadata (stored in Qdrant)
2. **Query**: User question with mode (selected-text | book-wide) and optional context
3. **Response**: Generated answer with sources, confidence, and refusal metadata
4. **Source**: Citation sub-entity (passage_id, chapter, section, snippet)
5. **Session**: Multi-turn conversation tracking (deferred for MVP)

**API Endpoints Specified**:
- `POST /v1/chat`: Main chatbot interaction
- `GET /v1/health`: Service health check
- `POST /v1/admin/index`: Index book content
- `GET /v1/admin/stats`: System statistics

**Constitution Re-Check**: ✅ ALL GATES PASS - Design maintains full compliance with constitutional requirements

---

## Next Steps

**Command**: `/sp.tasks`

This will generate `tasks.md` with:
- Phase 1: Setup (project structure, dependencies)
- Phase 2: Foundational (database, config, base models)
- Phase 3+: User story implementation (book-wide mode, selected-text mode, citation, refusal, frontend)
- Final Phase: Validation, testing, deployment

**Note**: The `/sp.plan` command stops here. Task generation (`/sp.tasks`) is a separate command to avoid conflating planning with execution.
