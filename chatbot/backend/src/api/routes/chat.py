"""Chat API routes for RAG chatbot question answering."""

import logging
import time
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ...models import QueryMode, Source
from ...services import AnswerGenerationService, RetrievalService
from ...utils.validation import sanitize_text, validate_context_text, validate_query_text

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User question",
        examples=["What is the optimal chunk size for RAG systems?"],
    )
    mode: QueryMode = Field(
        ...,
        description="Query mode: book-wide (semantic search) or selected-text (user-provided context only)",
    )
    context: Optional[str] = Field(
        None,
        max_length=10000,
        description="User-selected text (required for selected-text mode, must be None for book-wide mode)",
    )
    session_id: Optional[UUID] = Field(
        None,
        description="Session ID for multi-turn conversations (optional)",
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    query_id: UUID = Field(..., description="Unique identifier for this query")
    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(
        default_factory=list,
        description="Source citations for the answer",
    )
    refused: bool = Field(
        False,
        description="True if chatbot refused to answer due to insufficient context",
    )
    refusal_reason: Optional[str] = Field(
        None,
        description="Explanation for refusal (if refused=true)",
    )
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)",
    )
    latency_ms: int = Field(..., ge=0, description="Response latency in milliseconds")
    mode: QueryMode = Field(..., description="Mode used for this query")


# Refusal message template
REFUSAL_MESSAGE = (
    "I cannot answer this question based on the provided book content. "
    "The available context does not contain sufficient information about the requested topic. "
    "Please try:\n"
    "- Rephrasing your question\n"
    "- Selecting specific text from the book (selected-text mode)\n"
    "- Asking about topics covered in the book"
)


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask a question",
    description="""
Ask a question about the AI-Native Software Development Book.

**Modes:**
- **book-wide**: Semantic search over entire book using Qdrant vector database
- **selected-text**: Answer only from user-provided text (no retrieval)

**Constitutional Principles:**
1. **Grounded Accuracy**: All answers derived only from book content
2. **Faithful Retrieval**: Strict mode isolation (no cross-mode information leakage)
3. **Transparency**: Full source citations for every answer
4. **Academic Rigor**: CS-appropriate explanations
5. **Deterministic Refusal**: Explicit refusal when context insufficient

**Example Request (book-wide):**
```json
{
  "query": "What is the optimal chunk size for RAG systems?",
  "mode": "book-wide"
}
```

**Example Request (selected-text):**
```json
{
  "query": "Explain the main concept in this text",
  "mode": "selected-text",
  "context": "The optimal chunk size for technical documentation is 500-1000 tokens..."
}
```
    """,
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Answer a user question using RAG.

    Returns grounded answer with source citations or deterministic refusal.
    """
    start_time = time.time()
    query_id = uuid4()

    logger.info(f"[{query_id}] Chat request: mode={request.mode}, query_len={len(request.query)}")

    try:
        # Validate and sanitize input
        query = sanitize_text(request.query)
        is_valid, error_msg = validate_query_text(query)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg,
            )

        # Validate context based on mode
        is_valid, error_msg = validate_context_text(request.context, request.mode)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg,
            )

        # Initialize services
        retrieval_service = RetrievalService()
        answer_service = AnswerGenerationService()

        # Process based on mode
        if request.mode == QueryMode.BOOK_WIDE:
            # Book-wide mode: retrieve from Qdrant
            logger.info(f"[{query_id}] Book-wide mode: retrieving chunks")
            chunks, sources = retrieval_service.retrieve_and_rerank(query)

            if not chunks:
                # No chunks retrieved - refuse
                latency_ms = int((time.time() - start_time) * 1000)
                logger.warning(f"[{query_id}] No chunks retrieved, refusing")
                return ChatResponse(
                    query_id=query_id,
                    answer=REFUSAL_MESSAGE,
                    sources=[],
                    refused=True,
                    refusal_reason="No relevant content found in book",
                    confidence=0.0,
                    latency_ms=latency_ms,
                    mode=request.mode,
                )

            # Generate context from chunks
            context = retrieval_service.get_context_text(chunks)

        else:
            # Selected-text mode: use user-provided context only
            logger.info(f"[{query_id}] Selected-text mode: using user context ({len(request.context)} chars)")
            context = request.context
            sources = [
                Source(
                    passage_id="selected-text",
                    chapter="User-Selected Text",
                    section="User Selection",
                    page=None,
                    snippet=context[:200] + "..." if len(context) > 200 else context,
                )
            ]

        # Generate answer
        logger.info(f"[{query_id}] Generating answer")
        answer, confidence, refused, refusal_reason = answer_service.generate_answer(
            query=query,
            context=context,
            mode=request.mode,
            user_context=request.context if request.mode == QueryMode.SELECTED_TEXT else None,
        )

        # Override with standard refusal message if refused
        if refused:
            answer = REFUSAL_MESSAGE
            sources = []

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"[{query_id}] Response complete: refused={refused}, "
            f"confidence={confidence:.2f}, latency={latency_ms}ms"
        )

        return ChatResponse(
            query_id=query_id,
            answer=answer,
            sources=sources,
            refused=refused,
            refusal_reason=refusal_reason,
            confidence=confidence,
            latency_ms=latency_ms,
            mode=request.mode,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{query_id}] Chat request failed: {e}")
        latency_ms = int((time.time() - start_time) * 1000)

        # Return graceful error response
        return ChatResponse(
            query_id=query_id,
            answer="An error occurred while processing your question. Please try again.",
            sources=[],
            refused=True,
            refusal_reason=f"Internal error: {str(e)}",
            confidence=0.0,
            latency_ms=latency_ms,
            mode=request.mode,
        )
