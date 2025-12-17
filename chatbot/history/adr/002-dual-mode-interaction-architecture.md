# ADR-002: Dual-Mode Interaction Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-15
- **Feature:** 001-rag-chatbot
- **Context:** The constitution (Principle II: Faithful Retrieval) mandates strict separation between book-wide questions and selected-text questions. Book-wide mode retrieves from the entire book corpus, while selected-text mode operates only on user-provided text. This separation ensures no contamination between localized analysis and corpus-wide search, guaranteeing grounding integrity.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core interaction model
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Dual-mode vs hybrid vs single-mode
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects API, frontend, backend logic
-->

## Decision

Support **two distinct interaction modes** with strict isolation:

**Mode 1: Book-Wide Retrieval**
- User submits question without providing text
- Backend performs vector search over entire Qdrant book collection
- Top-K chunks retrieved and used as generation context
- Response includes citations to retrieved chunks

**Mode 2: Selected-Text Only**
- User selects text in Docusaurus UI and submits question about selection
- Frontend captures selection via `window.getSelection()` API
- Backend receives `mode="selected-text"` + `context=<selected text>`
- **Retrieval is completely disabled** (no Qdrant query)
- Generation uses only provided text as context
- Response cites user selection (not book passages)

**Mode Enforcement**:
- API validation: `mode="selected-text"` requires `context`; `mode="book-wide"` ignores `context`
- Frontend toggle: Clear UI indicator of active mode
- Constitutional compliance: No hybrid mode allowed (violates Principle II)

## Consequences

### Positive

- **Constitutional compliance**: Guarantees strict grounding to intended scope (constitutional requirement)
- **User control**: Users explicitly choose scope of search (selected text vs entire book)
- **Predictable behavior**: No ambiguity about which content was consulted
- **Localized analysis**: Selected-text mode enables deep dive on specific passages
- **Traceability**: Clear attribution (book passages vs user selection)
- **Testing simplicity**: Mode isolation enables independent validation (SC-004, SC-005)

### Negative

- **UX complexity**: Users must understand and switch between two modes
- **Missed opportunities**: No hybrid mode to augment selection with related book content
- **Implementation overhead**: Dual code paths for retrieval logic
- **Mode confusion risk**: Users may forget which mode is active
- **No automatic detection**: System cannot infer mode from query (must be explicit)

## Alternatives Considered

**Alternative 1: Hybrid Mode (selection + retrieval)**
- Approach: Use selected text as primary context, retrieve related chunks as supplementary context
- Why rejected:
  - Violates constitutional mode separation (Principle II: Faithful Retrieval)
  - Risk of contamination: supplementary chunks may introduce info outside selection
  - User cannot verify whether answer came from selection or retrieved chunks
  - Breaks traceability guarantee (SC-004: selected-text mode never exceeds selection)

**Alternative 2: Single Book-Wide Mode Only**
- Approach: Only support book-wide retrieval, no selected-text mode
- Why rejected:
  - Users cannot ask questions scoped to specific passages
  - Retrieval may return irrelevant chunks for localized questions
  - Violates constitutional requirement for selected-text mode isolation
  - Misses use case: "Explain this specific paragraph"

**Alternative 3: Automatic Mode Detection**
- Approach: Infer mode from query (e.g., "Explain this" → selected-text, "What is RAG?" → book-wide)
- Why rejected:
  - Unreliable heuristics (many queries ambiguous)
  - Users lose control over scope
  - Risk of wrong mode selection → incorrect behavior
  - Violates determinism requirement (SC-006: mode switching deterministic and user-controlled)

## References

- Feature Spec: specs/001-rag-chatbot/spec.md (not yet created)
- Implementation Plan: specs/001-rag-chatbot/plan.md (lines 38-42: Faithful Retrieval principle)
- Constitution: .specify/memory/constitution.md (Principle II: Faithful Retrieval)
- Research: specs/001-rag-chatbot/research.md (Section 5: Selected-Text Mode Implementation)
- Data Model: specs/001-rag-chatbot/data-model.md (Query entity: mode field validation)
- API Contract: specs/001-rag-chatbot/contracts/chatbot-api.yaml (POST /chat: mode parameter)
- Related ADRs: ADR-001 (RAG Architecture), ADR-004 (Grounding and Refusal Logic)
- Evaluator Evidence: history/prompts/001-rag-chatbot/002-implementation-plan-rag-chatbot.plan.prompt.md
