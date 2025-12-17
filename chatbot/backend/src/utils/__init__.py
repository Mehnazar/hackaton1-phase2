"""Utility functions for RAG Chatbot backend."""

from .chunking import (
    create_text_splitter,
    extract_chapter_from_text,
    extract_section_from_text,
    generate_embedding,
    generate_embeddings_batch,
    generate_passage_id,
    split_markdown_text,
    truncate_snippet,
)
from .qdrant_client import QdrantClientWrapper, get_qdrant_client
from .validation import (
    extract_passage_id_components,
    is_valid_passage_id,
    sanitize_text,
    validate_confidence_score,
    validate_context_text,
    validate_query_text,
    validate_similarity_score,
)

__all__ = [
    # Chunking utilities
    "create_text_splitter",
    "split_markdown_text",
    "generate_embedding",
    "generate_embeddings_batch",
    "extract_chapter_from_text",
    "extract_section_from_text",
    "generate_passage_id",
    "truncate_snippet",
    # Qdrant client
    "QdrantClientWrapper",
    "get_qdrant_client",
    # Validation utilities
    "sanitize_text",
    "validate_query_text",
    "validate_context_text",
    "validate_similarity_score",
    "validate_confidence_score",
    "extract_passage_id_components",
    "is_valid_passage_id",
]
