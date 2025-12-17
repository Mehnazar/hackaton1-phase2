# Tasks: RAG Chatbot for AI-Native Software Development Book

**Input**: Design documents from `/specs/001-rag-chatbot/`
**Prerequisites**: plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included for all major functionality to ensure constitutional compliance (grounding, mode enforcement, refusal behavior).

**Organization**: Tasks are grouped by functional capability (content indexing, book-wide retrieval, selected-text mode, citation, refusal, frontend) to enable independent implementation.

## Format: `[ID] [P?] [Feature] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Feature]**: Which functional capability this task belongs to (e.g., INDEXING, RETRIEVAL, REFUSAL, FRONTEND)
- Include exact file paths in descriptions

## Path Conventions

**Web app structure**: `backend/src/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend project structure (backend/src/{models,services,api,utils}, backend/tests/{contract,integration,unit})
- [X] T002 Create frontend project structure (frontend/src/{components,services,hooks}, frontend/tests/components)
- [X] T003 [P] Initialize Python 3.11+ project with FastAPI dependencies in backend/requirements.txt
- [X] T004 [P] Initialize TypeScript/React project with ChatKit dependencies in frontend/package.json
- [X] T005 [P] Configure pytest, pytest-asyncio, httpx in backend/pyproject.toml
- [X] T006 [P] Configure linting (black, flake8, mypy) in backend/pyproject.toml
- [X] T007 [P] Configure TypeScript ESLint and Prettier in frontend/.eslintrc.json

**Checkpoint**: ✅ Project structure ready for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY feature can be implemented

**⚠️ CRITICAL**: No feature work can begin until this phase is complete

### Environment Configuration

- [ ] T008 Create backend/.env.example with all required env vars (QDRANT_URL, QDRANT_API_KEY, NEON_DATABASE_URL, OPENAI_API_KEY, etc.)
- [ ] T009 Implement config.py to load environment variables in backend/src/config.py
- [ ] T010 Add config validation (raise errors if required vars missing)

### Database Setup (Neon Postgres - Optional Logging)

- [ ] T011 Create SQL schema file backend/sql/schema.sql (queries, responses, sessions tables per data-model.md)
- [ ] T012 Add database indexes (queries.timestamp, responses.query_id, responses.refused) in schema.sql
- [ ] T013 [P] Implement database connection pool in backend/src/utils/database.py (psycopg2 or asyncpg)

### Base Models and Entities

- [ ] T014 [P] Create Chunk model in backend/src/models/chunk.py (id, text, embedding, chapter, section, page, passage_id, source_file, created_at)
- [ ] T015 [P] Create Query model in backend/src/models/query.py (id, session_id, text, mode, context, timestamp)
- [ ] T016 [P] Create Response model in backend/src/models/response.py (id, query_id, answer, sources, confidence, refused, refusal_reason, latency_ms, timestamp)
- [ ] T017 [P] Create Source model in backend/src/models/source.py (passage_id, chapter, section, page, snippet)

### Qdrant Setup

- [ ] T018 Implement Qdrant client initialization in backend/src/utils/qdrant_client.py (use QDRANT_URL and QDRANT_API_KEY)
- [ ] T019 Create Qdrant collection "book-chunks" with schema from contracts/qdrant-schema.json in qdrant_client.py
- [ ] T020 Implement health check for Qdrant connection

### FastAPI Application Setup

- [ ] T021 Create FastAPI app instance in backend/src/api/main.py with CORS middleware
- [ ] T022 [P] Implement error handling middleware in backend/src/api/middleware/errors.py (catch exceptions, return ErrorResponse format)
- [ ] T023 [P] Implement logging middleware in backend/src/api/middleware/logging.py (log requests/responses if ENABLE_LOGGING=true)
- [ ] T024 Add startup/shutdown event handlers (connect/disconnect Qdrant, Neon) in main.py

### Utilities

- [ ] T025 [P] Implement input validation utilities in backend/src/utils/validation.py (validate query length, mode values, context requirements)
- [ ] T026 [P] Implement chunking utilities in backend/src/utils/chunking.py (LangChain MarkdownTextSplitter with section boundary logic)

**Checkpoint**: Foundation ready - feature implementation can now begin in parallel

---

## Phase 3: Content Indexing (INDEXING Feature)

**Goal**: Extract, chunk, embed, and index book content into Qdrant

**Independent Test**: Query Qdrant for sample passage and verify retrieval

### Implementation

- [ ] T027 [P] [INDEXING] Implement Markdown extraction service in backend/src/services/indexing.py (read files from content/ directory)
- [ ] T028 [P] [INDEXING] Implement semantic chunking in indexing.py (call utils/chunking.py, generate passage IDs)
- [ ] T029 [INDEXING] Implement embedding generation service in backend/src/services/embedding.py (OpenAI text-embedding-3-small API)
- [ ] T030 [INDEXING] Implement Qdrant upload service in indexing.py (batch upload chunks with embeddings and metadata)
- [ ] T031 [INDEXING] Create POST /v1/admin/index endpoint in backend/src/api/routes/admin.py (trigger indexing pipeline)
- [ ] T032 [INDEXING] Add indexing progress tracking and error handling
- [ ] T033 [INDEXING] Create standalone indexing CLI script backend/scripts/index_content.py (for manual indexing)

### Tests

- [ ] T034 [P] [INDEXING] Unit test for Markdown extraction in backend/tests/unit/test_indexing.py
- [ ] T035 [P] [INDEXING] Unit test for chunking logic in backend/tests/unit/test_chunking.py (verify section boundaries preserved)
- [ ] T036 [P] [INDEXING] Integration test for full indexing pipeline in backend/tests/integration/test_indexing.py

**Checkpoint**: Book content indexed in Qdrant and retrievable by semantic search

---

## Phase 4: Book-Wide Retrieval Mode (RETRIEVAL Feature)

**Goal**: Implement book-wide retrieval with top-5 semantic search and reranking

**Independent Test**: Send query in book-wide mode, verify top-5 chunks retrieved and reranked

### Implementation

- [ ] T037 [RETRIEVAL] Implement Qdrant vector search service in backend/src/services/retrieval.py (query for top-10 candidates)
- [ ] T038 [RETRIEVAL] Implement section proximity reranking in retrieval.py (boost chunks from same chapter/section)
- [ ] T039 [RETRIEVAL] Implement document order sorting in retrieval.py (sort by page/section sequence)
- [ ] T040 [RETRIEVAL] Add retrieval error handling (Qdrant timeout, connection errors)

### Tests

- [ ] T041 [P] [RETRIEVAL] Unit test for Qdrant query logic in backend/tests/unit/test_retrieval.py
- [ ] T042 [P] [RETRIEVAL] Unit test for reranking logic (verify same-chapter boost)
- [ ] T043 [RETRIEVAL] Integration test for end-to-end retrieval in backend/tests/integration/test_retrieval.py

**Checkpoint**: Book-wide retrieval returns top-5 relevant and reranked chunks

---

## Phase 5: Answer Generation and Grounding (GENERATION Feature)

**Goal**: Generate grounded answers using OpenAI Agents SDK with strict constitutional compliance

**Independent Test**: Send query with retrieved chunks, verify answer grounded in chunks only

### Implementation

- [ ] T044 [GENERATION] Implement OpenAI Agents integration in backend/src/services/generation.py (define search_book and get_passage tools)
- [ ] T045 [GENERATION] Implement system prompt for grounding enforcement in generation.py ("Only answer using provided passages...")
- [ ] T046 [GENERATION] Implement answer generation with confidence scoring
- [ ] T047 [P] [GENERATION] Implement grounding validation service in backend/src/services/grounding.py (multi-gate refusal logic)
- [ ] T048 [GENERATION] Add generation error handling (OpenAI API failures, rate limits, retries)

### Tests

- [ ] T049 [P] [GENERATION] Unit test for system prompt format
- [ ] T050 [P] [GENERATION] Integration test for grounded generation in backend/tests/integration/test_generation.py (verify answer uses only provided chunks)

**Checkpoint**: Answer generation produces grounded answers from retrieved chunks

---

## Phase 6: Refusal Logic (REFUSAL Feature)

**Goal**: Implement multi-gate refusal logic with deterministic refusal message

**Independent Test**: Send query with low similarity or confidence, verify refusal with standard message

### Implementation

- [ ] T051 [REFUSAL] Implement Gate 1 (retrieval similarity threshold) in backend/src/services/grounding.py (refuse if top-1 similarity < 0.7)
- [ ] T052 [REFUSAL] Implement Gate 2 (context sufficiency check) in grounding.py (warn if keywords missing)
- [ ] T053 [REFUSAL] Implement Gate 3 (generation confidence threshold) in grounding.py (refuse if confidence < 0.6)
- [ ] T054 [REFUSAL] Implement standard refusal message format in grounding.py ("This information cannot be verified from the book content.")
- [ ] T055 [REFUSAL] Add refusal reason logging (similarity score, confidence score)

### Tests

- [ ] T056 [P] [REFUSAL] Contract test for refusal behavior in backend/tests/contract/test_refusal.py (low similarity → refuse)
- [ ] T057 [P] [REFUSAL] Contract test for confidence threshold (low confidence → refuse)
- [ ] T058 [REFUSAL] Integration test for multi-gate refusal in backend/tests/integration/test_grounding.py

**Checkpoint**: Refusal logic correctly refuses queries with insufficient context or confidence

---

## Phase 7: Citation and Traceability (CITATION Feature)

**Goal**: Implement structured citations with source metadata and verification

**Independent Test**: Send query, verify response includes sources array with passage IDs and snippets

### Implementation

- [ ] T059 [P] [CITATION] Implement citation formatting service in backend/src/services/citation.py (generate Source objects from chunks)
- [ ] T060 [P] [CITATION] Implement snippet extraction (50-200 chars from chunk text)
- [ ] T061 [CITATION] Add citation metadata to Response model (sources array populated)
- [ ] T062 [CITATION] Implement source verification (ensure passage_id exists in Qdrant)

### Tests

- [ ] T063 [P] [CITATION] Unit test for citation formatting in backend/tests/unit/test_citation.py
- [ ] T064 [P] [CITATION] Unit test for snippet extraction (verify truncation at 200 chars)
- [ ] T065 [CITATION] Contract test for source traceability in backend/tests/contract/test_chat_api.py (verify all sources valid)

**Checkpoint**: All responses include structured citations with verifiable passage IDs

---

## Phase 8: Selected-Text Mode (SELECTED-TEXT Feature)

**Goal**: Implement selected-text mode with retrieval bypass and mode enforcement

**Independent Test**: Send query in selected-text mode with context, verify no Qdrant retrieval and answer uses only provided context

### Implementation

- [ ] T066 [SELECTED-TEXT] Implement mode validation in backend/src/utils/validation.py (mode="selected-text" requires context)
- [ ] T067 [SELECTED-TEXT] Implement retrieval bypass in backend/src/services/retrieval.py (skip Qdrant if mode="selected-text")
- [ ] T068 [SELECTED-TEXT] Implement context-only generation in generation.py (use provided context, no chunks)
- [ ] T069 [SELECTED-TEXT] Implement user-selection citation in citation.py (passage_id="user-selection", chapter/section="User Selection")

### Tests

- [ ] T070 [P] [SELECTED-TEXT] Contract test for mode enforcement in backend/tests/contract/test_mode_switching.py (selected-text + context → no retrieval)
- [ ] T071 [P] [SELECTED-TEXT] Contract test for mode validation (selected-text without context → 400 error)
- [ ] T072 [SELECTED-TEXT] Integration test for selected-text mode in backend/tests/integration/test_selected_text.py

**Checkpoint**: Selected-text mode works correctly with no retrieval and uses only provided context

---

## Phase 9: Main Chat Endpoint (CHAT Feature)

**Goal**: Implement POST /v1/chat endpoint orchestrating full RAG pipeline

**Independent Test**: Send request to POST /v1/chat, verify correct mode routing and response format

### Implementation

- [ ] T073 [CHAT] Implement POST /v1/chat endpoint in backend/src/api/routes/chat.py
- [ ] T074 [CHAT] Add request validation (validate ChatRequest schema from contracts/chatbot-api.yaml)
- [ ] T075 [CHAT] Implement mode routing (book-wide → retrieval + generation, selected-text → context-only generation)
- [ ] T076 [CHAT] Implement latency tracking (measure end-to-end time)
- [ ] T077 [CHAT] Implement response formatting (return ChatResponse schema)
- [ ] T078 [CHAT] Add optional query/response logging to Neon Postgres (if ENABLE_LOGGING=true)

### Tests

- [ ] T079 [P] [CHAT] Contract test for POST /v1/chat book-wide mode in backend/tests/contract/test_chat_api.py
- [ ] T080 [P] [CHAT] Contract test for POST /v1/chat selected-text mode
- [ ] T081 [P] [CHAT] Contract test for POST /v1/chat refusal response
- [ ] T082 [CHAT] Integration test for end-to-end chat flow in backend/tests/integration/test_end_to_end.py

**Checkpoint**: POST /v1/chat endpoint fully functional for both modes

---

## Phase 10: Health and Admin Endpoints (ADMIN Feature)

**Goal**: Implement GET /v1/health and GET /v1/admin/stats endpoints

**Independent Test**: Call GET /v1/health, verify dependency statuses returned

### Implementation

- [ ] T083 [P] [ADMIN] Implement GET /v1/health endpoint in backend/src/api/routes/health.py (check Qdrant, Neon, OpenAI connectivity)
- [ ] T084 [P] [ADMIN] Implement GET /v1/admin/stats endpoint in backend/src/api/routes/admin.py (query Neon for metrics)
- [ ] T085 [ADMIN] Add API key authentication for /v1/admin/* endpoints (check X-API-Key header)

### Tests

- [ ] T086 [P] [ADMIN] Contract test for GET /v1/health
- [ ] T087 [P] [ADMIN] Contract test for GET /v1/admin/stats (with valid API key)
- [ ] T088 [ADMIN] Contract test for /v1/admin/* without API key (expect 401)

**Checkpoint**: Health and admin endpoints operational

---

## Phase 11: Frontend UI (FRONTEND Feature)

**Goal**: Integrate ChatKit UI into Docusaurus with text selection and mode switching

**Independent Test**: Open book page, select text, ask question, verify chatbot uses only selected text

### Implementation

- [ ] T089 [P] [FRONTEND] Implement ChatWidget component in frontend/src/components/ChatWidget.tsx (ChatKit integration)
- [ ] T090 [P] [FRONTEND] Implement TextSelector component in frontend/src/components/TextSelector.tsx (window.getSelection() API)
- [ ] T091 [P] [FRONTEND] Implement ModeToggle component in frontend/src/components/ModeToggle.tsx (book-wide vs selected-text toggle)
- [ ] T092 [FRONTEND] Implement useTextSelection hook in frontend/src/hooks/useTextSelection.ts (capture selection on mouseup)
- [ ] T093 [FRONTEND] Implement useChat hook in frontend/src/hooks/useChat.ts (manage chat state)
- [ ] T094 [FRONTEND] Implement API client in frontend/src/services/api.ts (call POST /v1/chat)
- [ ] T095 [FRONTEND] Implement citation rendering (inline citations [1], [2] with footnotes)
- [ ] T096 [FRONTEND] Implement clickable citations with deep links to book sections
- [ ] T097 [FRONTEND] Implement hover tooltips for citation snippets

### Tests

- [ ] T098 [P] [FRONTEND] Component test for ChatWidget in frontend/tests/components/ChatWidget.test.tsx
- [ ] T099 [P] [FRONTEND] Component test for TextSelector in frontend/tests/components/TextSelector.test.tsx
- [ ] T100 [P] [FRONTEND] Component test for ModeToggle

**Checkpoint**: ChatKit UI embedded in Docusaurus with text selection and citation rendering

---

## Phase 12: Validation and Constitutional Compliance (VALIDATION Feature)

**Goal**: Validate all constitutional requirements and success criteria

**Independent Test**: Run validation test suite, verify all constitutional gates pass

### Implementation

- [ ] T101 [VALIDATION] Create validation test suite in backend/tests/integration/test_constitutional_compliance.py
- [ ] T102 [P] [VALIDATION] Test SC-001: Every response traceable to explicit passages
- [ ] T103 [P] [VALIDATION] Test SC-002: Zero hallucinated facts (compare answers against chunks)
- [ ] T104 [P] [VALIDATION] Test SC-003: Consistent refusal behavior (same query → same refusal decision)
- [ ] T105 [P] [VALIDATION] Test SC-004: Selected-text mode never exceeds selection
- [ ] T106 [P] [VALIDATION] Test SC-005: Book-wide mode never uses external knowledge
- [ ] T107 [P] [VALIDATION] Test SC-006: Mode switching deterministic and user-controlled
- [ ] T108 [VALIDATION] Test SC-012: <3 seconds latency (measure p95)
- [ ] T109 [VALIDATION] Test SC-013: Qdrant Free Tier compliance (check vector count < 1M)
- [ ] T110 [VALIDATION] Run quickstart.md validation (follow setup guide end-to-end)

**Checkpoint**: All constitutional requirements validated and passing

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple features

- [ ] T111 [P] Update README.md with project overview, setup instructions, and architecture diagram
- [ ] T112 [P] Create CONTRIBUTING.md with development workflow and testing guidelines
- [ ] T113 [P] Add API documentation (serve OpenAPI spec from FastAPI at /docs)
- [ ] T114 [P] Implement rate limiting middleware for /v1/chat endpoint (prevent abuse)
- [ ] T115 [P] Add request timeout configuration (default 30s)
- [ ] T116 [P] Implement Qdrant Free Tier monitoring (alert if approaching 1M vectors)
- [ ] T117 Code cleanup and refactoring (remove debug print statements, unused imports)
- [ ] T118 Performance optimization (profile slow endpoints, optimize chunk retrieval)
- [ ] T119 Security hardening (validate all inputs, sanitize user-provided context)
- [ ] T120 Create deployment guide (Render/Fly.io deployment steps)

**Checkpoint**: Project ready for production deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all features
- **Content Indexing (Phase 3)**: Depends on Foundational (Phase 2)
- **Book-Wide Retrieval (Phase 4)**: Depends on Foundational (Phase 2) + Content Indexing (Phase 3)
- **Answer Generation (Phase 5)**: Depends on Foundational (Phase 2) + Book-Wide Retrieval (Phase 4)
- **Refusal Logic (Phase 6)**: Depends on Foundational (Phase 2) + Answer Generation (Phase 5)
- **Citation (Phase 7)**: Depends on Foundational (Phase 2) + Book-Wide Retrieval (Phase 4)
- **Selected-Text Mode (Phase 8)**: Depends on Foundational (Phase 2) + Answer Generation (Phase 5)
- **Main Chat Endpoint (Phase 9)**: Depends on ALL prior phases (3-8)
- **Health/Admin Endpoints (Phase 10)**: Depends on Foundational (Phase 2) - can run in parallel with features
- **Frontend UI (Phase 11)**: Depends on Main Chat Endpoint (Phase 9)
- **Validation (Phase 12)**: Depends on ALL prior phases (1-11)
- **Polish (Phase 13)**: Depends on Validation (Phase 12)

### Critical Path

1. Setup (Phase 1) → 2. Foundational (Phase 2) → 3. Content Indexing (Phase 3) → 4. Book-Wide Retrieval (Phase 4) → 5. Answer Generation (Phase 5) → 6. Refusal Logic (Phase 6) → 9. Main Chat Endpoint (Phase 9) → 11. Frontend UI (Phase 11) → 12. Validation (Phase 12) → 13. Polish (Phase 13)

### Parallel Opportunities

- **Phase 1**: All tasks marked [P] can run in parallel (T003-T007)
- **Phase 2**: All tasks marked [P] within each group can run in parallel (T011-T013, T014-T017, T022-T023, T025-T028)
- **Phase 3-8**: Tests marked [P] can run in parallel within each phase
- **Phase 10**: Can run in parallel with Phases 3-9 (health/admin independent of chat features)

### Within Each Phase

- Models before services
- Services before endpoints
- Tests can run in parallel with implementation (TDD: write tests first, ensure they fail)
- Commit after each task or logical group

---

## Implementation Strategy

### MVP First (Minimal Viable Product)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all features)
3. Complete Phase 3: Content Indexing
4. Complete Phase 4: Book-Wide Retrieval
5. Complete Phase 5: Answer Generation
6. Complete Phase 6: Refusal Logic
7. Complete Phase 9: Main Chat Endpoint
8. **STOP and VALIDATE**: Test POST /v1/chat with book-wide mode, verify grounding and refusal
9. Deploy backend to cloud platform (Render/Fly.io)
10. Test deployed endpoint

### Incremental Feature Addition

1. MVP deployed (book-wide mode working)
2. Add Phase 7: Citation → Deploy/Demo
3. Add Phase 8: Selected-Text Mode → Deploy/Demo
4. Add Phase 11: Frontend UI → Deploy/Demo
5. Each phase adds value without breaking previous functionality

### Full Production Deployment

1. Complete all phases 1-12
2. Run validation test suite (Phase 12)
3. Fix any failing constitutional compliance tests
4. Complete Phase 13: Polish
5. Deploy to production
6. Run quickstart.md validation on production environment

---

## Notes

- [P] tasks = different files, no dependencies (can run in parallel)
- [Feature] label maps task to functional capability for traceability
- Each feature should be independently completable and testable
- Verify tests fail before implementing (TDD)
- Commit after each task or logical group
- Stop at checkpoints to validate feature independently
- Avoid: vague tasks, same file conflicts, cross-feature dependencies that break independence

---

## Acceptance Criteria

The RAG chatbot is complete when ALL of the following are true:

- ✅ All 120 tasks completed
- ✅ All constitutional compliance tests pass (SC-001 through SC-015)
- ✅ Quickstart.md validation passes end-to-end
- ✅ Backend deployed to cloud platform and accessible
- ✅ Frontend integrated into Docusaurus book layout
- ✅ Zero hallucinated facts in evaluation (manual or automated grading)
- ✅ Refusal behavior consistent and deterministic
- ✅ Latency < 3 seconds p95
- ✅ Qdrant Free Tier compliance maintained (< 1M vectors)
