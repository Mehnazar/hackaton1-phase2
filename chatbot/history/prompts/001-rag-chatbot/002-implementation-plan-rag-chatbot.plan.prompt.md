---
id: 002
title: Implementation Plan RAG Chatbot
stage: plan
date: 2025-12-15
surface: agent
model: claude-sonnet-4-5
feature: 001-rag-chatbot
branch: main
user: Mehnazar
command: /sp.plan
labels: ["plan", "rag-chatbot", "architecture", "design"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-rag-chatbot/plan.md
  - specs/001-rag-chatbot/research.md
  - specs/001-rag-chatbot/data-model.md
  - specs/001-rag-chatbot/contracts/chatbot-api.yaml
  - specs/001-rag-chatbot/contracts/qdrant-schema.json
  - specs/001-rag-chatbot/quickstart.md
tests:
  - N/A (planning phase - no tests yet)
---

## Prompt

```text
/sp.plan

Phase 1: Requirements and scope confirmation
- Confirm chatbot goals, modes, and refusal behavior
- Define book-wide vs selected-text-only answering rules
- Finalize grounding and citation expectations
- Validate alignment with chatbot constitution

Phase 2: Content preparation and indexing
- Extract and normalize book content (Markdown)
- Define chunking strategy (size, overlap, section boundaries)
- Generate embeddings and index content in Qdrant
- Store source metadata in Neon Serverless Postgres

Phase 3: Backend RAG implementation
- Implement FastAPI endpoints for chatbot interaction
- Integrate OpenAI Agents for retrieval and answer generation
- Enforce selected-text-only mode (disable retrieval)
- Implement refusal logic for insufficient context

Phase 4: Frontend embedding and interaction
- Integrate ChatKit UI into Docusaurus book layout
- Enable text selection capture and mode switching
- Connect frontend to FastAPI backend
- Verify usability across book pages

Phase 5: Validation and grounding checks
- Test retrieval relevance and context accuracy
- Verify all responses are grounded in retrieved or selected text
- Validate strict isolation in selected-text-only mode
- Measure latency and stability under Free Tier limits

Phase 6: Evaluation, hardening, and deployment
- Run hallucination and refusal tests
- Review logs and traces in Neon Postgres
- Deploy backend and update production endpoints
- Final verification in deployed book environment
```

## Response snapshot

Generated comprehensive implementation plan with the following artifacts:

**Phase 0: Research (research.md)**
- Resolved 10 technical unknowns: chunking strategy, embedding model, retrieval strategy, refusal logic, selected-text mode, citations, orchestration SDK, Qdrant schema, Neon schema, error handling
- Key decisions: Semantic chunking (500-1000 tokens), OpenAI text-embedding-3-small, top-5 retrieval with reranking, multi-gate refusal (similarity + confidence thresholds)

**Phase 1: Design**
- **data-model.md**: Defined 5 entities (Chunk, Query, Response, Source, Session) with validation rules and storage mappings
- **contracts/chatbot-api.yaml**: OpenAPI 3.0 spec with 4 endpoints (POST /chat, GET /health, POST /admin/index, GET /admin/stats)
- **contracts/qdrant-schema.json**: Collection schema with HNSW index config and payload schema
- **quickstart.md**: 10-section guide covering setup, indexing, querying, frontend integration, testing, monitoring, troubleshooting, deployment

**plan.md Summary**:
- Technical Context: Python 3.11+, FastAPI, OpenAI Agents SDK, Qdrant Cloud, Neon Postgres
- Constitution Check: ✅ ALL GATES PASS (5 core principles, 4 architecture constraints, 15 success criteria)
- Project Structure: Web application (backend + frontend)
- Complexity Tracking: No violations

## Outcome

- ✅ Impact: Complete architectural plan for RAG chatbot with all constitutional requirements satisfied
- 🧪 Tests: Planning phase complete; testing strategy defined in quickstart.md
- 📁 Files: Created 6 planning artifacts (plan.md, research.md, data-model.md, 2 contracts, quickstart.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate actionable task list based on this plan
- 🧠 Reflection: Plan successfully addresses all 6 user-provided phases while maintaining strict adherence to constitutional principles (grounding, mode enforcement, traceability, academic rigor, deterministic refusal). All technical unknowns resolved through research phase.

## Evaluation notes (flywheel)

- Failure modes observed: None. All planning artifacts generated successfully with no constitutional violations.
- Graders run and results (PASS/FAIL): Manual validation PASS - Constitution Check shows all gates passing, all entities well-defined, API contracts complete, quickstart comprehensive.
- Prompt variant (if applicable): N/A (standard /sp.plan workflow)
- Next experiment (smallest change to try): Consider adding architectural decision record (ADR) for key decisions (chunking strategy, refusal logic design, mode enforcement architecture) - suggest to user: `/sp.adr chunking-and-retrieval-strategy`
