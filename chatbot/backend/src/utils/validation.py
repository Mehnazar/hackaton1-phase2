"""Input validation utilities for query processing."""

import re
from typing import Tuple

from ..models import QueryMode


def sanitize_text(text: str) -> str:
    """
    Sanitize text input by removing control characters and normalizing whitespace.

    Args:
        text: Raw text input

    Returns:
        Sanitized text with normalized whitespace
    """
    # Remove control characters except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize whitespace (multiple spaces/newlines to single)
    text = re.sub(r"\s+", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def validate_query_text(text: str, min_length: int = 1, max_length: int = 2000) -> Tuple[bool, str]:
    """
    Validate query text length and content.

    Args:
        text: Query text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return False, "Query text cannot be empty"

    if len(text) < min_length:
        return False, f"Query text must be at least {min_length} characters"

    if len(text) > max_length:
        return False, f"Query text must not exceed {max_length} characters"

    return True, ""


def validate_context_text(
    context: str | None, mode: QueryMode, min_length: int = 1, max_length: int = 10000
) -> Tuple[bool, str]:
    """
    Validate context text based on query mode.

    Args:
        context: Context text (user-selected text)
        mode: Query mode (book-wide or selected-text)
        min_length: Minimum allowed length for context
        max_length: Maximum allowed length for context

    Returns:
        Tuple of (is_valid, error_message)
    """
    if mode == QueryMode.SELECTED_TEXT:
        if not context:
            return False, "Context is required for selected-text mode"

        if len(context) < min_length:
            return False, f"Context must be at least {min_length} characters"

        if len(context) > max_length:
            return False, f"Context must not exceed {max_length} characters"

    elif mode == QueryMode.BOOK_WIDE:
        if context:
            return False, "Context must not be provided for book-wide mode"

    return True, ""


def validate_similarity_score(score: float) -> bool:
    """
    Validate similarity score is in valid range [0.0, 1.0].

    Args:
        score: Similarity score to validate

    Returns:
        True if valid, False otherwise
    """
    return 0.0 <= score <= 1.0


def validate_confidence_score(score: float) -> bool:
    """
    Validate confidence score is in valid range [0.0, 1.0].

    Args:
        score: Confidence score to validate

    Returns:
        True if valid, False otherwise
    """
    return 0.0 <= score <= 1.0


def extract_passage_id_components(passage_id: str) -> Tuple[int, int, int] | None:
    """
    Extract chapter, section, and page numbers from passage_id.

    Args:
        passage_id: Passage identifier (e.g., "ch3-sec2-p45")

    Returns:
        Tuple of (chapter, section, page) or None if invalid format
    """
    pattern = r"^ch(\d+)-sec(\d+)-p(\d+)$"
    match = re.match(pattern, passage_id)

    if not match:
        return None

    chapter = int(match.group(1))
    section = int(match.group(2))
    page = int(match.group(3))

    return (chapter, section, page)


def is_valid_passage_id(passage_id: str) -> bool:
    """
    Check if passage_id matches expected format.

    Args:
        passage_id: Passage identifier to validate

    Returns:
        True if valid format, False otherwise
    """
    return extract_passage_id_components(passage_id) is not None
