# ADR-004: Grounding and Refusal Logic

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-15
- **Feature:** 001-rag-chatbot
- **Context:** The constitution (Principle V: Deterministic Refusal) mandates that the chatbot refuse to answer when evidence is insufficient rather than speculate or hallucinate. This is a critical safety mechanism to maintain book credibility and prevent false information. The system must balance strictness (avoiding hallucinations) with usability (minimizing false refusals). Refusal logic must be transparent, deterministic, and testable (SC-002, SC-003).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core safety mechanism
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Multi-gate vs single-gate vs no refusal
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects retrieval, generation, response formatting
-->

## Decision

Implement **multi-gate refusal logic** with similarity threshold and generation confidence:

**Gate 1: Retrieval Similarity Threshold**
- Threshold: Top-1 chunk cosine similarity > 0.7
- Action: If top-1 similarity < 0.7 → refuse immediately (no generation)
- Rationale: Low similarity indicates no relevant content in book

**Gate 2: Context Sufficiency Check** (warning, not refusal)
- Check: Retrieved chunks contain query keywords
- Action: If keywords missing → warn user (still attempt generation)
- Rationale: Catches semantic drift (high similarity but different topic)

**Gate 3: Generation Confidence Threshold**
- Threshold: OpenAI Agents confidence score > 0.6
- Action: If confidence < 0.6 → refuse (even if retrieval passed)
- Rationale: Catches cases where retrieved chunks insufficient for coherent answer

**Gate 4: Hallucination Detection** (future, deferred for MVP)
- Check: Compare generated answer against retrieved chunks for unsupported claims
- Action: If unsupported claims detected → refuse
- Rationale: Final safety net to catch LLM hallucinations

**Refusal Message** (standard across all gates):
- Text: "This information cannot be verified from the book content."
- Optional: Refusal reason (e.g., "Top-1 similarity (0.62) below threshold (0.7)")
- Response format: `{"answer": "<refusal message>", "sources": [], "refused": true, "refusal_reason": "<reason>"}`

**Threshold Calibration** (iterative process):
- Start: Conservative thresholds (0.7 similarity, 0.6 confidence)
- Monitor: False refusal rate (answerable questions refused) via Neon Postgres logs
- Adjust: Lower thresholds if false refusal rate > 10%; raise if hallucination rate > 1%

## Consequences

### Positive

- **Zero hallucinations**: Multi-gate approach catches failures at multiple stages (constitutional requirement SC-002)
- **Deterministic refusal**: Same query always produces same refusal decision (constitutional requirement SC-003)
- **Transparency**: Refusal reason explains why answer unavailable
- **Testable**: Each gate independently testable (unit tests)
- **Calibratable**: Thresholds tunable based on evaluation metrics
- **Constitutional compliance**: Explicit refusal better than speculative answer (Principle V)

### Negative

- **False refusals**: Conservative thresholds may refuse answerable questions (poor UX)
- **Threshold sensitivity**: Small changes in threshold drastically affect refusal rate
- **Calibration complexity**: Requires evaluation set and iterative tuning
- **User frustration**: Users may not understand why valid questions are refused
- **Latency overhead**: Multi-gate checks add ~50-100ms to response time
- **Confidence score reliability**: OpenAI Agents confidence may not correlate with answer quality

## Alternatives Considered

**Alternative 1: Single Similarity Threshold Only**
- Approach: Refuse only if top-1 similarity < 0.7, no generation confidence check
- Why rejected:
  - Doesn't catch generation failures (high similarity but poor answer quality)
  - LLM may hallucinate even with relevant chunks (e.g., combining contradictory info)
  - Violates constitutional zero-hallucination requirement (SC-002)
  - No safety net after retrieval stage

**Alternative 2: No Refusal Logic (always answer)**
- Approach: Generate answer regardless of retrieval quality or confidence
- Why rejected:
  - Violates constitutional deterministic refusal requirement (Principle V)
  - High risk of hallucinations (unacceptable for book credibility)
  - No way to signal insufficient evidence to user
  - Fails SC-002 (zero hallucinated facts) and SC-003 (consistent refusal behavior)

**Alternative 3: LLM-Based Hallucination Verifier**
- Approach: Use separate LLM call to verify answer against chunks (fact-checking)
- Why rejected:
  - Adds significant latency (~1-2 seconds per query)
  - Higher cost (double LLM calls)
  - Verifier LLM may also hallucinate (who verifies the verifier?)
  - Over-engineering for MVP (deferred to Gate 4 for future)

**Alternative 4: Adaptive Thresholds (per-chapter)**
- Approach: Learn different similarity/confidence thresholds for each chapter based on historical data
- Why rejected:
  - Requires large dataset (cold start problem for new chapters)
  - Non-deterministic refusal (same query may be refused in Chapter 1 but not Chapter 2)
  - Violates constitutional determinism requirement (SC-003)
  - Over-engineering for single-book corpus

## References

- Feature Spec: specs/001-rag-chatbot/spec.md (not yet created)
- Implementation Plan: specs/001-rag-chatbot/plan.md (lines 56-60: Deterministic Refusal principle)
- Research: specs/001-rag-chatbot/research.md (Section 4: Refusal Logic and Confidence Thresholds)
- Constitution: .specify/memory/constitution.md (Principle V: Deterministic Refusal; SC-002, SC-003)
- Data Model: specs/001-rag-chatbot/data-model.md (Response entity: refused, refusal_reason fields)
- API Contract: specs/001-rag-chatbot/contracts/chatbot-api.yaml (ChatResponse schema: refused, refusal_reason)
- Related ADRs: ADR-001 (RAG Architecture), ADR-003 (Content Processing and Retrieval Stack)
- Evaluator Evidence: history/prompts/001-rag-chatbot/002-implementation-plan-rag-chatbot.plan.prompt.md
