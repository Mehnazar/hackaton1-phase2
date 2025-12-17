---
id: 001
title: Create RAG Chatbot Constitution
stage: constitution
date: 2025-12-15
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: Mehnazar
command: /sp.constitution
labels: ["constitution", "rag-chatbot", "grounding", "retrieval"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution creation does not involve tests)
---

## Prompt

```text
/sp.constitution

Project: Integrated RAG Chatbot for AI-Native Software Development Book

Core principles:
- Grounded accuracy (all answers derived strictly from book content or user-selected text)
- Faithful retrieval (no hallucination beyond retrieved or provided context)
- Transparency (answers traceable to specific book sections or passages)
- Academic rigor (clear, precise explanations suitable for a computer science audience)
- Deterministic refusal (explicitly decline when evidence is insufficient)

Key standards:
- All factual statements must be supported by retrieved book passages or selected text
- No use of external knowledge, training data, or general world facts
- Selected-text mode:
  - Reasoning restricted exclusively to user-selected text
  - Vector retrieval disabled
- Book-wide mode:
  - Retrieval limited to indexed book content in Qdrant
- Answer tone must be explanatory, neutral, and non-speculative
- When an answer cannot be grounded, respond with:
  "This information cannot be verified from the book content."

Constraints:
- Architecture:
  - OpenAI Agents / ChatKit SDKs for interaction and orchestration
  - FastAPI for inference and retrieval orchestration
  - Qdrant Cloud Free Tier for vector storage
  - Neon Serverless Postgres for metadata and interaction logs
- Retrieval:
  - Semantic vector search only over indexed book chunks
  - Fixed upper bound on retrieved context (to prevent dilution)
- Data handling:
  - No modification of book content at inference time
  - User queries and logs stored only if explicitly enabled
- Performance:
  - Must operate within Qdrant Free Tier limits
  - Graceful degradation on retrieval or API failure

Success criteria:
- Every chatbot response is traceable to explicit book passages or selected text
- Selected-text-only questions never include information outside the selection
- Zero hallucinated facts detected during evaluation
- Chatbot consistently refuses unanswerable questions
- Passes grounding, mode-enforcement, and accuracy validation checks
```

## Response snapshot

Created the project constitution at `.specify/memory/constitution.md` with version 1.0.0.

The constitution establishes five core principles:
1. Grounded Accuracy - zero tolerance for extrapolation beyond retrieved context
2. Faithful Retrieval - strict mode enforcement (selected-text vs. book-wide)
3. Transparency and Traceability - all responses traceable to source passages
4. Academic Rigor - computer science academic standards for explanations
5. Deterministic Refusal - explicit refusal when evidence is insufficient

Added sections for Architecture Constraints, Success Criteria (15 measurable outcomes), and Governance (amendment procedure, compliance review, complexity justification).

All template files (.specify/templates/plan-template.md, spec-template.md, tasks-template.md) verified for alignment with the new constitution.

## Outcome

- ✅ Impact: Project constitution established as the authoritative governance document for the RAG chatbot project
- 🧪 Tests: N/A (constitution is a governance artifact, not code)
- 📁 Files: Created `.specify/memory/constitution.md` (206 lines)
- 🔁 Next prompts: Create feature specification with `/sp.specify`, then implementation plan with `/sp.plan`
- 🧠 Reflection: Constitution successfully captures all user-provided principles and constraints. The five-principle structure provides clear, testable governance rules. Success criteria (SC-001 through SC-015) are measurable and aligned with principles.

## Evaluation notes (flywheel)

- Failure modes observed: None. Constitution template fully populated with no remaining placeholders.
- Graders run and results (PASS/FAIL): Manual validation PASS - all placeholders resolved, version semantics correct, dates in ISO format, principles declarative and testable.
- Prompt variant (if applicable): N/A (initial constitution creation)
- Next experiment (smallest change to try): N/A (constitution is complete and ready for use)
