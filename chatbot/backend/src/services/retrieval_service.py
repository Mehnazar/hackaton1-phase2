"""Retrieval service for semantic search and reranking."""

import logging
from typing import Dict, List

from ..config import settings
from ..models import Chunk, Source
from ..utils.chunking import generate_embedding, truncate_snippet
from ..utils.qdrant_client import get_qdrant_client
from ..utils.validation import extract_passage_id_components

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Service for retrieving relevant chunks using semantic search.

    Handles query embedding, Qdrant search, and section proximity reranking.
    """

    def __init__(self):
        """Initialize RetrievalService."""
        self.qdrant_client = get_qdrant_client()
        self.top_k_retrieval = settings.top_k_retrieval
        self.top_k_rerank = settings.top_k_rerank
        self.similarity_threshold = settings.similarity_threshold
        logger.info(
            f"Initialized RetrievalService (top_k={self.top_k_retrieval}, "
            f"rerank={self.top_k_rerank}, threshold={self.similarity_threshold})"
        )

    def retrieve_chunks(self, query: str) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User question text

        Returns:
            List of retrieved chunk dicts with scores and payloads
        """
        logger.info(f"Retrieving chunks for query: {query[:100]}...")

        # Generate query embedding
        try:
            query_embedding = generate_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return []

        # Search Qdrant
        results = self.qdrant_client.search(
            query_vector=query_embedding,
            limit=self.top_k_retrieval,
            score_threshold=self.similarity_threshold,
        )

        logger.info(f"Retrieved {len(results)} chunks above threshold {self.similarity_threshold}")
        return results

    def rerank_by_section_proximity(self, chunks: List[Dict]) -> List[Dict]:
        """
        Rerank chunks by section proximity (boost same-chapter chunks).

        Strategy:
        1. Group chunks by chapter
        2. Boost scores for chunks in the most-represented chapter
        3. Sort by boosted score
        4. Return top-K reranked

        Args:
            chunks: List of chunk dicts from retrieve_chunks()

        Returns:
            Reranked list of chunks (top_k_rerank)
        """
        if not chunks:
            return []

        logger.info(f"Reranking {len(chunks)} chunks by section proximity...")

        # Count chapter frequencies
        chapter_counts = {}
        for chunk in chunks:
            chapter = chunk["payload"].get("chapter", "Unknown")
            chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1

        # Find most common chapter
        most_common_chapter = max(chapter_counts, key=chapter_counts.get) if chapter_counts else None
        logger.debug(f"Most common chapter: {most_common_chapter} ({chapter_counts.get(most_common_chapter, 0)} chunks)")

        # Boost scores for chunks in most common chapter
        boosted_chunks = []
        for chunk in chunks:
            chunk_copy = chunk.copy()
            chapter = chunk["payload"].get("chapter", "Unknown")

            # Boost score by 10% if in most common chapter
            if chapter == most_common_chapter:
                chunk_copy["boosted_score"] = chunk["score"] * 1.1
                logger.debug(f"Boosted chunk {chunk['payload'].get('passage_id')} from {chunk['score']:.3f} to {chunk_copy['boosted_score']:.3f}")
            else:
                chunk_copy["boosted_score"] = chunk["score"]

            boosted_chunks.append(chunk_copy)

        # Sort by boosted score (descending)
        reranked = sorted(boosted_chunks, key=lambda x: x["boosted_score"], reverse=True)

        # Return top-K reranked
        top_reranked = reranked[: self.top_k_rerank]
        logger.info(f"Reranked to top {len(top_reranked)} chunks")

        return top_reranked

    def sort_by_document_order(self, chunks: List[Dict]) -> List[Dict]:
        """
        Sort chunks by document order (chapter, section, page).

        Args:
            chunks: List of chunk dicts

        Returns:
            Sorted list of chunks
        """
        def get_sort_key(chunk: Dict) -> tuple:
            """Extract (chapter_num, section_num, page_num) for sorting."""
            passage_id = chunk["payload"].get("passage_id", "ch0-sec0-p0")
            components = extract_passage_id_components(passage_id)

            if components:
                chapter_num, section_num, page_num = components
                return (chapter_num, section_num, page_num)
            else:
                # Fallback: put at end
                return (999, 999, 999)

        sorted_chunks = sorted(chunks, key=get_sort_key)
        logger.debug(f"Sorted {len(sorted_chunks)} chunks by document order")
        return sorted_chunks

    def chunks_to_sources(self, chunks: List[Dict]) -> List[Source]:
        """
        Convert retrieved chunks to Source citations.

        Args:
            chunks: List of chunk dicts

        Returns:
            List of Source models
        """
        sources = []

        for chunk in chunks:
            payload = chunk["payload"]

            try:
                source = Source(
                    passage_id=payload.get("passage_id", "unknown"),
                    chapter=payload.get("chapter", "Unknown Chapter"),
                    section=payload.get("section", "Unknown Section"),
                    page=payload.get("page"),
                    snippet=truncate_snippet(payload.get("text", ""), max_length=200),
                )
                sources.append(source)
            except Exception as e:
                logger.error(f"Failed to create Source from chunk: {e}")
                continue

        logger.debug(f"Created {len(sources)} Source citations")
        return sources

    def retrieve_and_rerank(self, query: str) -> tuple[List[Dict], List[Source]]:
        """
        Full retrieval pipeline: retrieve -> rerank -> sort -> convert to sources.

        Args:
            query: User question text

        Returns:
            Tuple of (reranked_chunks, sources)
        """
        # Step 1: Retrieve chunks
        retrieved_chunks = self.retrieve_chunks(query)

        if not retrieved_chunks:
            logger.warning("No chunks retrieved")
            return [], []

        # Step 2: Rerank by section proximity
        reranked_chunks = self.rerank_by_section_proximity(retrieved_chunks)

        # Step 3: Sort by document order
        sorted_chunks = self.sort_by_document_order(reranked_chunks)

        # Step 4: Convert to sources
        sources = self.chunks_to_sources(sorted_chunks)

        logger.info(
            f"Retrieval pipeline complete: {len(retrieved_chunks)} retrieved, "
            f"{len(reranked_chunks)} reranked, {len(sources)} sources"
        )

        return sorted_chunks, sources

    def get_context_text(self, chunks: List[Dict]) -> str:
        """
        Concatenate chunk texts to form context for answer generation.

        Args:
            chunks: List of chunk dicts

        Returns:
            Concatenated context text
        """
        if not chunks:
            return ""

        context_parts = []
        for idx, chunk in enumerate(chunks, start=1):
            payload = chunk["payload"]
            passage_id = payload.get("passage_id", "unknown")
            text = payload.get("text", "")

            context_parts.append(f"[{passage_id}] {text}")

        context = "\n\n".join(context_parts)
        logger.debug(f"Generated context with {len(chunks)} chunks ({len(context)} chars)")
        return context
