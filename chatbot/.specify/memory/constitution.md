<!--
Sync Impact Report:
Version Change: Initial → 1.0.0
Modified Principles: Initial creation
Added Sections: Core Principles, Architecture Constraints, Success Criteria, Governance
Removed Sections: None
Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md (constitution check references this document)
  ✅ .specify/templates/spec-template.md (aligned with requirements structure)
  ✅ .specify/templates/tasks-template.md (aligned with testing and validation)
Follow-up TODOs: None
-->

# Integrated RAG Chatbot for AI-Native Software Development Book Constitution

## Core Principles

### I. Grounded Accuracy

All answers MUST be derived strictly from book content or user-selected text. The chatbot operates as a retrieval-augmented system with zero tolerance for extrapolation beyond retrieved or provided context.

**Rationale**: This chatbot serves as an authoritative reference tool for the AI-Native Software Development Book. Users depend on factual accuracy and traceability to source material. Any deviation from book content undermines trust and academic integrity.

**Non-negotiable rules**:
- Every factual statement must be supported by retrieved book passages or selected text
- No use of external knowledge, training data, or general world facts
- When an answer cannot be grounded in available context, the system MUST respond with: "This information cannot be verified from the book content."

### II. Faithful Retrieval

The chatbot operates in two distinct modes, each with strict retrieval boundaries:

**Selected-text mode**:
- Reasoning restricted exclusively to user-selected text
- Vector retrieval disabled completely
- No access to broader book context

**Book-wide mode**:
- Retrieval limited to indexed book content in Qdrant
- Semantic vector search over indexed chunks only
- Fixed upper bound on retrieved context to prevent dilution

**Rationale**: Mode enforcement prevents contamination between localized text analysis and book-wide search. This separation ensures users receive answers from the exact scope they intend.

### III. Transparency and Traceability

Every chatbot response MUST be traceable to explicit book sections or selected passages.

**Non-negotiable rules**:
- Answers include source references (section, page, or passage identifiers)
- Retrieved context is presented or summarized for user verification
- No opaque reasoning chains that obscure source material

**Rationale**: Academic and professional users require the ability to verify claims and explore source material independently. Traceability enables critical evaluation and deeper learning.

### IV. Academic Rigor

Answer tone and content quality must meet computer science academic standards.

**Non-negotiable rules**:
- Clear, precise explanations suitable for technical audiences
- Neutral tone, free from speculation or editorializing
- Terminology consistent with book definitions and industry standards
- Complex concepts explained with appropriate technical depth

**Rationale**: The book targets software engineering professionals and students. Responses must match the intellectual rigor and precision expected in academic and professional contexts.

### V. Deterministic Refusal

When evidence is insufficient, the system MUST refuse to answer rather than speculate or approximate.

**Non-negotiable rules**:
- Explicit refusal with the standard message: "This information cannot be verified from the book content."
- No hedging, guessing, or probabilistic statements when grounding fails
- No fallback to general knowledge or training data

**Rationale**: False or ungrounded answers are worse than no answer. Deterministic refusal maintains system integrity and user trust.

## Architecture Constraints

### Technology Stack

**Interaction and Orchestration**:
- OpenAI Agents SDK or ChatKit SDK for multi-turn conversations and tool orchestration

**Inference and Retrieval**:
- FastAPI for serving inference endpoints and retrieval orchestration
- Python-based backend

**Vector Storage**:
- Qdrant Cloud Free Tier for vector storage and semantic search
- Must operate within Free Tier limits (1 GB storage, 1 million vectors)

**Metadata and Logs**:
- Neon Serverless Postgres for metadata, interaction logs, and user preferences
- User queries and logs stored only if explicitly enabled

### Retrieval Constraints

**Semantic Search**:
- Semantic vector search only over indexed book chunks
- No keyword search, regex, or full-text search fallbacks
- Fixed upper bound on retrieved context (e.g., top-5 chunks) to prevent dilution

**Context Management**:
- Retrieved chunks must maintain sufficient surrounding context for comprehension
- Chunk boundaries must not split critical explanations mid-sentence

### Data Handling

**Book Content Integrity**:
- No modification of book content at inference time
- Indexed chunks are read-only
- Updates to book content require re-indexing

**User Data**:
- User queries and interaction logs stored only if explicitly enabled
- No personally identifiable information (PII) stored without consent
- Compliance with data retention and privacy policies

### Performance and Reliability

**Qdrant Free Tier Compliance**:
- Must operate within 1 GB storage limit
- Must operate within 1 million vector limit
- Monitor usage to prevent exceeding limits

**Graceful Degradation**:
- On retrieval failure: return error message, do not hallucinate
- On API failure: log error, return user-friendly message
- System remains usable even if one component (e.g., Qdrant) is temporarily unavailable

## Success Criteria

The chatbot is considered successful when it meets ALL of the following measurable outcomes:

### Grounding Validation

- **SC-001**: Every chatbot response is traceable to explicit book passages or selected text
- **SC-002**: Zero hallucinated facts detected during evaluation (manual or automated grading)
- **SC-003**: Chatbot consistently refuses unanswerable questions with the standard refusal message

### Mode Enforcement

- **SC-004**: Selected-text-only questions never include information outside the selection
- **SC-005**: Book-wide mode questions never use external knowledge or training data
- **SC-006**: Mode switching (selected-text ↔ book-wide) is deterministic and user-controlled

### Accuracy and Precision

- **SC-007**: Factual correctness verified against book content (>95% accuracy on evaluation set)
- **SC-008**: Technical terminology usage consistent with book definitions
- **SC-009**: No conflicting or contradictory statements across multiple answers

### User Experience

- **SC-010**: Users can verify all factual claims by following provided source references
- **SC-011**: Answers are explanatory, neutral, and suitable for a computer science audience
- **SC-012**: System responds within acceptable latency bounds (e.g., <3 seconds for retrieval + generation)

### Operational Reliability

- **SC-013**: System operates within Qdrant Free Tier limits without degradation
- **SC-014**: Graceful error handling on retrieval or API failures
- **SC-015**: Logs capture sufficient detail for debugging and performance monitoring

## Governance

### Amendment Procedure

This constitution supersedes all other development practices and guidelines. Amendments require:

1. **Documentation**: Proposed changes documented with rationale and impact analysis
2. **Approval**: Consensus from project stakeholders (maintainers, users, reviewers)
3. **Migration Plan**: Explicit plan for updating dependent artifacts (specs, plans, tasks, code)
4. **Version Bump**: Semantic versioning applied according to impact:
   - **MAJOR**: Backward-incompatible governance or principle removals/redefinitions
   - **MINOR**: New principles or sections added, materially expanded guidance
   - **PATCH**: Clarifications, wording fixes, non-semantic refinements

### Compliance Review

All pull requests, code reviews, and design artifacts MUST verify compliance with this constitution.

**Verification checklist**:
- [ ] No hallucinated facts beyond retrieved or selected context
- [ ] Mode enforcement respected (selected-text vs. book-wide)
- [ ] Refusal behavior deterministic and correct
- [ ] Source traceability maintained
- [ ] Architecture constraints respected (Qdrant limits, no runtime content modification)

### Complexity Justification

Any deviation from these principles MUST be justified in writing with:
- Specific problem the deviation addresses
- Why a compliant alternative is insufficient
- Mitigation plan to minimize risk

Unjustified complexity or violations are grounds for rejection.

### Runtime Guidance

For detailed development workflows, agent-specific execution patterns, and runtime implementation guidance, see `CLAUDE.md` and other agent-specific guidance files.

**Version**: 1.0.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2025-12-15
