"""Chunking service for splitting book content into semantic segments."""

import logging
from typing import Dict, List

from ..config import settings
from ..models import Chunk
from ..utils.chunking import (
    extract_chapter_from_text,
    extract_section_from_text,
    generate_passage_id,
    split_markdown_text,
)

logger = logging.getLogger(__name__)


class ChunkingService:
    """
    Service for chunking book content into semantic segments.

    Handles splitting content while preserving metadata (chapter, section, page).
    """

    def __init__(self):
        """Initialize ChunkingService."""
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        logger.info(
            f"Initialized ChunkingService (chunk_size={self.chunk_size}, overlap={self.chunk_overlap})"
        )

    def chunk_section(
        self,
        section_content: str,
        chapter_info: Dict,
        section_title: str,
        section_num: int,
        source_file: str,
    ) -> List[Dict]:
        """
        Chunk a section of content.

        Args:
            section_content: Section text to chunk
            chapter_info: Dict with chapter_num, chapter_title, chapter_full
            section_title: Section title
            section_num: Section number within chapter
            source_file: Source file path

        Returns:
            List of chunk dicts (without embeddings)
        """
        # Split content into chunks
        text_chunks = split_markdown_text(section_content)

        chunks = []
        for idx, text in enumerate(text_chunks):
            # Generate passage_id (ch{N}-sec{M}-p{P})
            passage_id = generate_passage_id(
                chapter_num=chapter_info.get("chapter_num", 0),
                section_num=section_num,
                page_num=idx + 1,
            )

            chunk_dict = {
                "text": text,
                "chapter": chapter_info.get("chapter_full", "Unknown Chapter"),
                "section": section_title,
                "page": idx + 1,  # Page within section
                "passage_id": passage_id,
                "source_file": source_file,
            }

            chunks.append(chunk_dict)

        logger.debug(
            f"Created {len(chunks)} chunks from section '{section_title}' (chapter {chapter_info.get('chapter_num')})"
        )
        return chunks

    def chunk_file(self, processed_file: Dict) -> List[Dict]:
        """
        Chunk all sections in a processed file.

        Args:
            processed_file: Dict from ContentExtractor.process_file()

        Returns:
            List of chunk dicts (without embeddings)
        """
        chapter_info = processed_file.get("chapter_info", {})
        if not chapter_info:
            logger.warning(
                f"No chapter info for {processed_file['file_path']}, using defaults"
            )
            chapter_info = {
                "chapter_num": 0,
                "chapter_title": "Unknown",
                "chapter_full": "Unknown Chapter",
            }

        sections = processed_file.get("sections", [])
        if not sections:
            # If no sections, treat entire content as one section
            logger.warning(
                f"No sections found in {processed_file['file_path']}, using full content"
            )
            sections = [
                {
                    "section_title": chapter_info.get("chapter_title", "Main Content"),
                    "section_content": processed_file.get("raw_content", ""),
                }
            ]

        all_chunks = []
        for section_num, section in enumerate(sections, start=1):
            section_chunks = self.chunk_section(
                section_content=section["section_content"],
                chapter_info=chapter_info,
                section_title=section["section_title"],
                section_num=section_num,
                source_file=processed_file["file_path"],
            )
            all_chunks.extend(section_chunks)

        logger.info(
            f"Created {len(all_chunks)} chunks from {processed_file['file_path']}"
        )
        return all_chunks

    def chunk_all_files(self, processed_files: List[Dict]) -> List[Dict]:
        """
        Chunk all processed files.

        Args:
            processed_files: List of dicts from ContentExtractor.process_all_files()

        Returns:
            List of chunk dicts (without embeddings)
        """
        all_chunks = []

        for processed_file in processed_files:
            try:
                file_chunks = self.chunk_file(processed_file)
                all_chunks.extend(file_chunks)
            except Exception as e:
                logger.error(
                    f"Failed to chunk file {processed_file.get('file_path')}: {e}"
                )
                continue

        logger.info(
            f"Created {len(all_chunks)} total chunks from {len(processed_files)} files"
        )
        return all_chunks

    def validate_chunk(self, chunk_dict: Dict) -> bool:
        """
        Validate that a chunk dict has all required fields.

        Args:
            chunk_dict: Chunk dict to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["text", "chapter", "section", "passage_id", "source_file"]
        for field in required_fields:
            if field not in chunk_dict or not chunk_dict[field]:
                logger.error(f"Chunk missing required field: {field}")
                return False

        # Check text length
        if len(chunk_dict["text"]) < 100:
            logger.warning(f"Chunk text too short ({len(chunk_dict['text'])} chars)")
            return False

        if len(chunk_dict["text"]) > 2000:
            logger.warning(f"Chunk text too long ({len(chunk_dict['text'])} chars)")
            return False

        return True
