"""Answer generation service using OpenAI for grounded responses."""

import logging
from typing import List, Optional, Tuple

from openai import OpenAI

from ..config import settings
from ..models import QueryMode, Response, Source

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key)

# System prompt for grounded answer generation
GROUNDED_ANSWER_SYSTEM_PROMPT = """You are an expert AI assistant for the AI-Native Software Development Book.

**CRITICAL RULES (Constitutional Principles):**
1. **Grounded Accuracy**: ALL answers MUST be derived ONLY from the provided context. NEVER use external knowledge.
2. **Faithful Retrieval**: Answer ONLY from the context provided. If the context doesn't contain the answer, say so explicitly.
3. **Transparency**: Cite specific passages using [passage_id] format when referencing information.
4. **Academic Rigor**: Provide computer-science-appropriate explanations with technical depth.
5. **Deterministic Refusal**: If the context is insufficient to answer the question, respond with EXACTLY:
   "I cannot answer this question based on the provided book content. The available context does not contain sufficient information about [topic]."

**Response Format:**
- Answer the question clearly and concisely
- Cite passages using [passage_id] notation (e.g., [ch3-sec2-p45])
- Use multiple citations when drawing from different sections
- If uncertain, explicitly state limitations

**Example Good Answer:**
"The optimal chunk size for RAG systems is 500-1000 tokens with 100-token overlap [ch3-sec2-p45]. This balances semantic coherence with retrieval precision [ch3-sec2-p46]."

**Example Refusal:**
"I cannot answer this question based on the provided book content. The available context does not contain sufficient information about deployment strategies for production RAG systems."
"""


class AnswerGenerationService:
    """
    Service for generating grounded answers using OpenAI.

    Ensures all answers are derived from retrieved context with proper citations.
    """

    def __init__(self):
        """Initialize AnswerGenerationService."""
        self.chat_model = settings.openai_chat_model
        self.confidence_threshold = settings.confidence_threshold
        logger.info(
            f"Initialized AnswerGenerationService (model={self.chat_model}, "
            f"confidence_threshold={self.confidence_threshold})"
        )

    def build_prompt(
        self,
        query: str,
        context: str,
        mode: QueryMode,
        user_context: Optional[str] = None,
    ) -> str:
        """
        Build the user prompt for answer generation.

        Args:
            query: User question
            context: Retrieved context (book-wide) or user-provided (selected-text)
            mode: Query mode (book-wide or selected-text)
            user_context: User-selected text (for selected-text mode)

        Returns:
            Formatted user prompt
        """
        if mode == QueryMode.SELECTED_TEXT:
            # Selected-text mode: use only user-provided context
            prompt = f"""**SELECTED TEXT MODE**: Answer using ONLY the user-selected text below. DO NOT use any other knowledge.

**User-Selected Text:**
{user_context}

**User Question:**
{query}

**Instructions:**
- Answer ONLY from the selected text above
- If the selected text doesn't contain the answer, say: "The selected text does not contain information about [topic]."
- Cite the selected text as [selected-text]
"""
        else:
            # Book-wide mode: use retrieved context
            prompt = f"""**BOOK-WIDE MODE**: Answer using ONLY the retrieved book passages below. DO NOT use any other knowledge.

**Retrieved Context:**
{context}

**User Question:**
{query}

**Instructions:**
- Answer ONLY from the retrieved passages above
- Cite specific passages using [passage_id] notation
- If the retrieved context doesn't contain the answer, say: "I cannot answer this question based on the provided book content. The available context does not contain sufficient information about [topic]."
"""

        return prompt

    def generate_answer(
        self,
        query: str,
        context: str,
        mode: QueryMode,
        user_context: Optional[str] = None,
    ) -> Tuple[str, float, bool, Optional[str]]:
        """
        Generate an answer using OpenAI.

        Args:
            query: User question
            context: Retrieved context or user-selected text
            mode: Query mode
            user_context: User-selected text (for selected-text mode)

        Returns:
            Tuple of (answer, confidence, refused, refusal_reason)
        """
        logger.info(f"Generating answer for query in {mode} mode")

        # Build prompt
        user_prompt = self.build_prompt(query, context, mode, user_context)

        try:
            # Call OpenAI
            response = openai_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": GROUNDED_ANSWER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,  # Deterministic for consistency
                max_tokens=1000,
            )

            answer = response.choices[0].message.content.strip()
            finish_reason = response.choices[0].finish_reason

            logger.info(f"Generated answer ({len(answer)} chars, finish_reason={finish_reason})")

            # Check for refusal patterns
            refusal_patterns = [
                "I cannot answer this question",
                "The selected text does not contain",
                "The available context does not contain",
                "insufficient information",
            ]

            refused = any(pattern.lower() in answer.lower() for pattern in refusal_patterns)

            if refused:
                refusal_reason = "Insufficient context to answer question"
                confidence = 0.0
                logger.warning(f"Answer refused: {refusal_reason}")
            else:
                # Estimate confidence based on answer length and finish reason
                confidence = self._estimate_confidence(answer, finish_reason, context)

            return answer, confidence, refused, refusal_reason if refused else None

        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return (
                "An error occurred while generating the answer. Please try again.",
                0.0,
                True,
                f"Error: {str(e)}",
            )

    def _estimate_confidence(self, answer: str, finish_reason: str, context: str) -> float:
        """
        Estimate confidence score based on answer characteristics.

        Heuristics:
        - Length: Longer answers (with citations) = higher confidence
        - Citations: Presence of [passage_id] citations = higher confidence
        - Finish reason: 'stop' = higher confidence than 'length'

        Args:
            answer: Generated answer text
            finish_reason: OpenAI finish reason
            context: Retrieved context

        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.5  # Base confidence

        # Check for citations
        if "[ch" in answer or "[sec" in answer or "[selected-text]" in answer:
            confidence += 0.2
            logger.debug("Confidence +0.2 for citations")

        # Check answer length (reasonable answers are 50-500 chars)
        if 50 <= len(answer) <= 500:
            confidence += 0.2
            logger.debug("Confidence +0.2 for reasonable length")
        elif len(answer) > 500:
            confidence += 0.1

        # Check finish reason
        if finish_reason == "stop":
            confidence += 0.1
            logger.debug("Confidence +0.1 for clean finish")

        # Cap at 1.0
        confidence = min(confidence, 1.0)

        logger.debug(f"Estimated confidence: {confidence:.2f}")
        return confidence

    def should_refuse(self, confidence: float, context: str, query: str) -> Tuple[bool, Optional[str]]:
        """
        Determine if the answer should be refused based on confidence and context.

        Args:
            confidence: Estimated confidence score
            context: Retrieved context
            query: User question

        Returns:
            Tuple of (should_refuse, refusal_reason)
        """
        # Check confidence threshold
        if confidence < self.confidence_threshold:
            reason = f"Confidence ({confidence:.2f}) below threshold ({self.confidence_threshold})"
            logger.warning(f"Refusing answer: {reason}")
            return True, reason

        # Check context sufficiency
        if not context or len(context.strip()) < 100:
            reason = "Insufficient context (too short)"
            logger.warning(f"Refusing answer: {reason}")
            return True, reason

        return False, None
