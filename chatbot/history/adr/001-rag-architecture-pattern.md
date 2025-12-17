# ADR-001: RAG Architecture Pattern

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-15
- **Feature:** 001-rag-chatbot
- **Context:** The AI-Native Software Development Book chatbot needs to answer user questions about book content with strict grounding requirements. The constitution mandates zero hallucinations, complete traceability to source passages, and deterministic refusal when evidence is insufficient. The system must support book updates without model retraining.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core system design
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - RAG vs fine-tuning vs retrieval-only
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all components
-->

## Decision

Use **Retrieval-Augmented Generation (RAG)** over indexed book content instead of fine-tuning or retrieval-only approaches.

**Components**:
- Vector-based retrieval: Query→Qdrant→Top-K chunks
- LLM generation: Chunks as context→OpenAI Agents→Grounded answer
- Strict grounding: Generation only from retrieved passages (no external knowledge)
- Traceability: Return source citations with every response

## Consequences

### Positive

- **Traceability**: Every answer traceable to specific book passages (constitutional requirement)
- **Updatable**: Book content updates only require re-indexing (no retraining)
- **Transparency**: Retrieved chunks visible to users for verification
- **No training data**: Avoids copyright/licensing issues with fine-tuning
- **Cost-effective**: No fine-tuning cost ($0.02/1M tokens for embeddings vs $3+/1M for fine-tuning)
- **Flexible**: Easy to add/remove chapters or update content

### Negative

- **Latency**: Two-stage pipeline (retrieval + generation) adds ~1-2 seconds vs pure LLM
- **Retrieval dependency**: Requires Qdrant availability (single point of failure)
- **Context window limits**: Must fit retrieved chunks into LLM context (vs fine-tuned knowledge)
- **Retrieval quality**: Answers limited by retrieval precision (poor retrieval → poor answers)
- **Infrastructure complexity**: Requires vector database + embedding generation + orchestration

## Alternatives Considered

**Alternative 1: Fine-tuning only (no retrieval)**
- Approach: Fine-tune GPT-4 on book content, generate answers directly
- Why rejected:
  - Cannot trace answers to specific passages (violates constitution)
  - Book updates require expensive retraining
  - Risk of hallucination (model may blend book content with training data)
  - No transparency (users can't verify sources)
  - Higher cost ($3+/1M tokens for training)

**Alternative 2: Retrieval-only (no generation)**
- Approach: Return top matching chunks verbatim without LLM synthesis
- Why rejected:
  - Poor user experience (users get raw chunks, not synthesized answers)
  - No answer coherence (chunks may be contradictory or redundant)
  - Cannot handle complex questions requiring multi-chunk reasoning
  - Limited to keyword/semantic matching (no natural language understanding)

**Alternative 3: Hybrid (fine-tune + RAG)**
- Approach: Fine-tune on book content AND use RAG for citations
- Why rejected:
  - Over-engineering for single-book corpus
  - Fine-tuning unnecessary when RAG provides sufficient context
  - Higher cost and complexity
  - Risk of fine-tuned knowledge competing with retrieved knowledge

## References

- Feature Spec: specs/001-rag-chatbot/spec.md (not yet created)
- Implementation Plan: specs/001-rag-chatbot/plan.md
- Constitution: .specify/memory/constitution.md (Principle I: Grounded Accuracy, Principle III: Transparency)
- Research: specs/001-rag-chatbot/research.md (Sections 1-3: Chunking, Embeddings, Retrieval)
- Related ADRs: ADR-002 (Dual-Mode Interaction), ADR-003 (Content Processing and Retrieval Stack), ADR-004 (Grounding and Refusal Logic)
- Evaluator Evidence: history/prompts/001-rag-chatbot/002-implementation-plan-rag-chatbot.plan.prompt.md
