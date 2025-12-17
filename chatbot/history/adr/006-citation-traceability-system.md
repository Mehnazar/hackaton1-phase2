# ADR-006: Citation and Traceability System

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-15
- **Feature:** 001-rag-chatbot
- **Context:** The constitution (Principle III: Transparency and Traceability) mandates that every chatbot response be traceable to explicit book sections or selected passages. Users must be able to verify all factual claims by navigating to source material (SC-001, SC-010). This requires structured citation metadata, frontend rendering of clickable citations, and integration with the Docusaurus book layout. The citation system must support both book-wide mode (passages from Qdrant) and selected-text mode (user-provided selections).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core trust mechanism
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Structured vs plain text, various rendering approaches
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects data model, API, frontend, Qdrant schema
-->

## Decision

Implement a **structured citation and traceability system** with the following components:

**1. Citation Metadata Schema** (embedded in Chunk and Response entities)
- Fields: passage_id (unique ID), chapter, section, page (optional), snippet (50-200 chars)
- Storage: Qdrant payload (Chunk), Response JSONB array (Neon Postgres)
- Format: JSON for machine-readability

**2. Passage ID Convention**
- Pattern: `ch{chapter_num}-sec{section_num}-p{page}` (e.g., "ch3-sec2-p45")
- Uniqueness: passage_id unique across all chunks
- Human-readable: easy to reference in discussions/documentation

**3. Source Citation Structure** (returned with every response)
```json
{
  "answer": "...",
  "sources": [
    {
      "passage_id": "ch3-sec2-p45",
      "chapter": "Chapter 3: RAG Systems",
      "section": "3.2 Retrieval Strategies",
      "page": 45,
      "snippet": "The optimal chunk size for technical documentation is 500-1000 tokens..."
    }
  ]
}
```

**4. Frontend Citation Rendering**
- Inline citations: Superscript numbers `[1]`, `[2]` in answer text
- Footnote list: Below answer, showing all sources with snippets
- Hover tooltip: Snippet preview on hover over citation number
- Click action: Scroll to source passage in Docusaurus book (deep link)

**5. Selected-Text Mode Citations**
- passage_id: `"user-selection"` (vs book passage IDs)
- chapter/section: `"User Selection" / "Selected Text"`
- snippet: Excerpt from user-provided context
- No deep link (no fixed book location)

## Consequences

### Positive

- **Constitutional compliance**: Full traceability (Principle III, SC-001, SC-010)
- **User verification**: Clickable citations enable instant fact-checking
- **Machine-readable**: JSON format supports programmatic analysis (e.g., citation frequency by chapter)
- **Transparency**: Users see exact passages used to generate answer
- **Academic credibility**: Proper citations similar to academic papers
- **Debugging**: Developers can trace incorrect answers to specific chunks
- **SEO benefit**: Deep links improve Docusaurus book discoverability

### Negative

- **Frontend complexity**: Citation rendering requires React state management and link generation
- **Deep link maintenance**: Docusaurus URL structure changes require citation link updates
- **Snippet truncation**: 200-char snippets may not capture full context
- **Response size**: Citation metadata adds ~200-500 bytes per source (5 sources = ~1-2.5 KB)
- **Rendering inconsistency**: Inline citations may break on long answers or complex formatting
- **Mobile UX**: Hover tooltips don't work on touch devices (require tap or long-press)

## Alternatives Considered

**Alternative 1: Plain Text Citations**
- Approach: Return citations as plain text strings (e.g., "Source: Chapter 3, Section 2, Page 45")
- Why rejected:
  - Not machine-readable (hard to parse programmatically)
  - No structured metadata for analytics (citation frequency, chapter coverage)
  - Harder to render as clickable links (requires text parsing)
  - Less professional than structured JSON format

**Alternative 2: No Citations (answer only)**
- Approach: Return answer text without source references
- Why rejected:
  - Violates constitutional traceability requirement (Principle III, SC-001)
  - Users cannot verify claims (SC-010)
  - No transparency (violates Principle III)
  - Unacceptable for academic/professional book

**Alternative 3: Full Chunk Text in Response**
- Approach: Include entire chunk text (500-1000 tokens) instead of snippet
- Why rejected:
  - Bloats response size (5 chunks = 2500-5000 tokens = ~10-20 KB)
  - Poor UX (users overwhelmed with raw chunks)
  - Slower transmission over network
  - Snippet (50-200 chars) sufficient for preview

**Alternative 4: Hyperlinked Inline Citations (not clickable footnotes)**
- Approach: Embed hyperlinks directly in answer text (e.g., "According to [this passage](link)")
- Why rejected:
  - Disrupts answer readability (links mid-sentence)
  - Harder to parse which sources were used (vs numbered footnotes)
  - LLM must generate markdown links (complex prompt engineering)
  - Footnote format more familiar to users (academic convention)

**Alternative 5: Passage Highlighting in Book**
- Approach: Highlight source passages in Docusaurus book when viewing chatbot response
- Why rejected:
  - Requires bi-directional integration (chatbot → book highlighting)
  - Complex frontend state management (highlight persistence)
  - User may navigate away from highlighted passage
  - Over-engineering for MVP (defer to future enhancement)

## References

- Feature Spec: specs/001-rag-chatbot/spec.md (not yet created)
- Implementation Plan: specs/001-rag-chatbot/plan.md (lines 44-48: Transparency and Traceability)
- Constitution: .specify/memory/constitution.md (Principle III: Transparency and Traceability; SC-001, SC-010)
- Research: specs/001-rag-chatbot/research.md (Section 6: Citation and Source Traceability)
- Data Model: specs/001-rag-chatbot/data-model.md (Source sub-entity, Response entity)
- API Contract: specs/001-rag-chatbot/contracts/chatbot-api.yaml (Source schema, ChatResponse schema)
- Qdrant Schema: specs/001-rag-chatbot/contracts/qdrant-schema.json (payload schema: chapter, section, page, passage_id)
- Related ADRs: ADR-001 (RAG Architecture), ADR-002 (Dual-Mode Interaction)
- Evaluator Evidence: history/prompts/001-rag-chatbot/002-implementation-plan-rag-chatbot.plan.prompt.md
