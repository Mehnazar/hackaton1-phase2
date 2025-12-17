---
id: 003
title: Document Architectural Decisions
stage: misc
date: 2025-12-15
surface: agent
model: claude-sonnet-4-5
feature: 001-rag-chatbot
branch: main
user: Mehnazar
command: /sp.adr
labels: ["adr", "architecture", "decisions", "documentation"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: history/adr/001-rag-architecture-pattern.md
  pr: null
files:
  - history/adr/001-rag-architecture-pattern.md
  - history/adr/002-dual-mode-interaction-architecture.md
  - history/adr/003-content-processing-retrieval-stack.md
  - history/adr/004-grounding-refusal-logic.md
  - history/adr/005-technology-stack.md
  - history/adr/006-citation-traceability-system.md
tests:
  - N/A (ADR documentation - no tests)
---

## Prompt

```text
/sp.adr

Review the RAG chatbot plan and record key architectural decisions that affect
system behavior, correctness, and long-term maintainability.

---

ADR-001: Use RAG instead of fine-tuning
Decision:
- The chatbot uses Retrieval-Augmented Generation over indexed book content.

Why:
- Ensures answers are traceable and updatable without retraining.

---

ADR-002: Separate interaction modes
Decision:
- Support two modes:
  - Book-wide retrieval
  - Selected-text-only (retrieval disabled)

Why:
- Guarantees strict grounding when users reference specific passages.

---

ADR-003: OpenAI Agents for orchestration
Decision:
- Use OpenAI Agents to manage retrieval and answer generation.

Why:
- Enables enforceable tool boundaries and refusal logic.

---

ADR-004: Qdrant Cloud Free Tier for vectors
Decision:
- Use Qdrant Cloud Free Tier for embeddings storage.

Why:
- Cost-effective and sufficient for book-scale retrieval.

---

ADR-005: FastAPI as backend layer
Decision:
- Use FastAPI to orchestrate RAG workflows.

Why:
- Clear separation of UI and inference logic.

---

ADR-006: Deterministic refusal on missing context
Decision:
- Chatbot refuses to answer when grounding is insufficient.

Why:
- Prevents hallucination and preserves book credibility.

---

End of ADR.
```

## Response snapshot

Extracted and documented 6 architectural decision clusters from RAG chatbot planning artifacts:

1. **ADR-001: RAG Architecture Pattern** - RAG vs fine-tuning; traceability and updatability
2. **ADR-002: Dual-Mode Interaction Architecture** - Book-wide vs selected-text modes; constitutional mode enforcement
3. **ADR-003: Content Processing and Retrieval Stack** - Chunking (500-1000 tokens) + embeddings (text-embedding-3-small) + retrieval (top-5 with reranking) + Qdrant HNSW indexing
4. **ADR-004: Grounding and Refusal Logic** - Multi-gate refusal (similarity 0.7, confidence 0.6); deterministic refusal message
5. **ADR-005: Technology Stack** - FastAPI + OpenAI Agents SDK + Qdrant Cloud + Neon Postgres + ChatKit UI
6. **ADR-006: Citation and Traceability System** - Structured metadata with passage IDs; clickable citations with deep links

All ADRs include:
- Decision statement with components
- Positive and negative consequences
- Alternatives considered with rejection rationale
- References to plan, research, data-model, contracts, constitution

Applied significance test (3 criteria): impact on software structure, notable tradeoffs, will be questioned later. All 6 clusters passed.

## Outcome

- ✅ Impact: Permanent architectural record for RAG chatbot decisions; enables team alignment and future reference
- 🧪 Tests: N/A (ADRs are documentation, not code)
- 📁 Files: Created 6 ADR files in history/adr/
- 🔁 Next prompts: Run `/sp.specify` to create formal feature spec, then `/sp.tasks` for implementation tasks
- 🧠 Reflection: Decision clustering (not atomic choices) improved ADR quality. Grouping chunking + embeddings + retrieval into single ADR (ADR-003) captured integrated pipeline tradeoffs better than 3 separate ADRs. All ADRs directly reference constitutional principles and success criteria, ensuring alignment with governance.

## Evaluation notes (flywheel)

- Failure modes observed: None. All 6 ADRs passed significance test and include explicit alternatives + consequences.
- Graders run and results (PASS/FAIL): Manual validation PASS - All ADRs have clustered decisions, explicit alternatives, positive/negative consequences, references to planning artifacts.
- Prompt variant (if applicable): User provided initial ADR suggestions (6 decisions); agent expanded into full clustered ADRs with tradeoff analysis.
- Next experiment (smallest change to try): Consider grouping ADR-001 + ADR-002 (RAG + Dual-Mode) into single "Core Architecture" ADR if decisions too tightly coupled. Current separation OK for independent evolution.
