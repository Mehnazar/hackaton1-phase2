"""Chunking utilities for content processing and indexing."""

import logging
import re
from typing import List

from langchain_text_splitters import MarkdownTextSplitter
from openai import OpenAI

from ..config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key)


def create_text_splitter(
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> MarkdownTextSplitter:
    """
    Create a MarkdownTextSplitter configured for book content.

    Args:
        chunk_size: Target chunk size in tokens (defaults to settings.chunk_size)
        chunk_overlap: Overlap between chunks in tokens (defaults to settings.chunk_overlap)

    Returns:
        Configured MarkdownTextSplitter instance
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    return MarkdownTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def split_markdown_text(text: str) -> List[str]:
    """
    Split Markdown text into semantic chunks.

    Args:
        text: Markdown content to split

    Returns:
        List of text chunks
    """
    splitter = create_text_splitter()
    chunks = splitter.split_text(text)

    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks


def generate_embedding(text: str, model: str | None = None) -> List[float]:
    """
    Generate embedding vector for text using OpenAI.

    Args:
        text: Text to embed
        model: Embedding model to use (defaults to settings.openai_embedding_model)

    Returns:
        1536-dimensional embedding vector

    Raises:
        Exception: If embedding generation fails
    """
    model = model or settings.openai_embedding_model

    try:
        response = openai_client.embeddings.create(
            input=text,
            model=model,
        )
        embedding = response.data[0].embedding

        logger.debug(f"Generated embedding for text (length={len(text)})")
        return embedding

    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise


def generate_embeddings_batch(texts: List[str], model: str | None = None) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a batch.

    Args:
        texts: List of texts to embed
        model: Embedding model to use (defaults to settings.openai_embedding_model)

    Returns:
        List of 1536-dimensional embedding vectors

    Raises:
        Exception: If embedding generation fails
    """
    model = model or settings.openai_embedding_model

    try:
        response = openai_client.embeddings.create(
            input=texts,
            model=model,
        )
        embeddings = [data.embedding for data in response.data]

        logger.info(f"Generated {len(embeddings)} embeddings in batch")
        return embeddings

    except Exception as e:
        logger.error(f"Failed to generate embeddings batch: {e}")
        raise


def extract_chapter_from_text(text: str) -> str | None:
    """
    Extract chapter title/number from text.

    Looks for patterns like "# Chapter 3: RAG Systems" or "# 3. RAG Systems"

    Args:
        text: Text content to search

    Returns:
        Chapter title or None if not found
    """
    # Pattern 1: "# Chapter N: Title"
    pattern1 = r"^#\s+Chapter\s+(\d+)[:\-\s]+(.+)$"
    match = re.search(pattern1, text, re.MULTILINE | re.IGNORECASE)
    if match:
        chapter_num = match.group(1)
        title = match.group(2).strip()
        return f"Chapter {chapter_num}: {title}"

    # Pattern 2: "# N. Title"
    pattern2 = r"^#\s+(\d+)\.\s+(.+)$"
    match = re.search(pattern2, text, re.MULTILINE)
    if match:
        chapter_num = match.group(1)
        title = match.group(2).strip()
        return f"Chapter {chapter_num}: {title}"

    return None


def extract_section_from_text(text: str) -> str | None:
    """
    Extract section title from text.

    Looks for patterns like "## 3.2 Retrieval Strategies" or "## Retrieval Strategies"

    Args:
        text: Text content to search

    Returns:
        Section title or None if not found
    """
    # Pattern 1: "## N.M Title"
    pattern1 = r"^##\s+(\d+\.\d+)\s+(.+)$"
    match = re.search(pattern1, text, re.MULTILINE)
    if match:
        section_num = match.group(1)
        title = match.group(2).strip()
        return f"{section_num} {title}"

    # Pattern 2: "## Title"
    pattern2 = r"^##\s+(.+)$"
    match = re.search(pattern2, text, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        return title

    return None


def generate_passage_id(chapter_num: int, section_num: int, page_num: int) -> str:
    """
    Generate a passage identifier in the format "chN-secM-pP".

    Args:
        chapter_num: Chapter number
        section_num: Section number
        page_num: Page number

    Returns:
        Passage identifier (e.g., "ch3-sec2-p45")
    """
    return f"ch{chapter_num}-sec{section_num}-p{page_num}"


def truncate_snippet(text: str, max_length: int = 200) -> str:
    """
    Truncate text to maximum length for snippet display.

    Args:
        text: Full text to truncate
        max_length: Maximum length for snippet

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text

    # Truncate at word boundary
    truncated = text[: max_length - 3].rsplit(" ", 1)[0]
    return truncated + "..."
