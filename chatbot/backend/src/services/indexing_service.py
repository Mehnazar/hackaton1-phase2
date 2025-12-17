"""Indexing service for processing and indexing book content into Qdrant."""

import logging
from typing import Dict, List
from uuid import uuid4

from qdrant_client.models import PointStruct

from ..models import Chunk
from ..utils.chunking import generate_embeddings_batch
from ..utils.qdrant_client import get_qdrant_client
from .chunking_service import ChunkingService
from .content_extractor import ContentExtractor

logger = logging.getLogger(__name__)


class IndexingService:
    """
    Service for indexing book content into Qdrant.

    Coordinates content extraction, chunking, embedding, and vector storage.
    """

    def __init__(self, content_dir: str = "content"):
        """
        Initialize IndexingService.

        Args:
            content_dir: Directory containing Markdown book files
        """
        self.content_extractor = ContentExtractor(content_dir=content_dir)
        self.chunking_service = ChunkingService()
        self.qdrant_client = get_qdrant_client()
        logger.info(f"Initialized IndexingService with content_dir: {content_dir}")

    def generate_embeddings_for_chunks(
        self, chunk_dicts: List[Dict], batch_size: int = 100
    ) -> List[Chunk]:
        """
        Generate embeddings for chunks and create Chunk models.

        Args:
            chunk_dicts: List of chunk dicts (without embeddings)
            batch_size: Batch size for embedding generation

        Returns:
            List of Chunk models with embeddings
        """
        chunks_with_embeddings = []
        total_chunks = len(chunk_dicts)

        logger.info(f"Generating embeddings for {total_chunks} chunks...")

        # Process in batches
        for i in range(0, total_chunks, batch_size):
            batch = chunk_dicts[i : i + batch_size]
            texts = [chunk["text"] for chunk in batch]

            try:
                # Generate embeddings batch
                embeddings = generate_embeddings_batch(texts)

                # Create Chunk models
                for chunk_dict, embedding in zip(batch, embeddings):
                    chunk = Chunk(
                        id=uuid4(),
                        text=chunk_dict["text"],
                        embedding=embedding,
                        chapter=chunk_dict["chapter"],
                        section=chunk_dict["section"],
                        page=chunk_dict.get("page"),
                        passage_id=chunk_dict["passage_id"],
                        source_file=chunk_dict["source_file"],
                    )
                    chunks_with_embeddings.append(chunk)

                logger.info(f"Processed batch {i // batch_size + 1}: {len(batch)} chunks")

            except Exception as e:
                logger.error(f"Failed to generate embeddings for batch {i // batch_size + 1}: {e}")
                continue

        logger.info(
            f"Successfully generated embeddings for {len(chunks_with_embeddings)}/{total_chunks} chunks"
        )
        return chunks_with_embeddings

    def index_chunks(self, chunks: List[Chunk], batch_size: int = 100) -> int:
        """
        Index chunks into Qdrant.

        Args:
            chunks: List of Chunk models with embeddings
            batch_size: Batch size for Qdrant upsert

        Returns:
            Number of successfully indexed chunks
        """
        total_chunks = len(chunks)
        indexed_count = 0

        logger.info(f"Indexing {total_chunks} chunks into Qdrant...")

        # Process in batches
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]

            # Convert chunks to PointStruct
            points = [
                PointStruct(
                    id=str(chunk.id),
                    vector=chunk.embedding,
                    payload=chunk.to_qdrant_payload(),
                )
                for chunk in batch
            ]

            try:
                success = self.qdrant_client.upsert_points(points)
                if success:
                    indexed_count += len(batch)
                    logger.info(f"Indexed batch {i // batch_size + 1}: {len(batch)} chunks")
                else:
                    logger.error(f"Failed to index batch {i // batch_size + 1}")

            except Exception as e:
                logger.error(f"Error indexing batch {i // batch_size + 1}: {e}")
                continue

        logger.info(f"Successfully indexed {indexed_count}/{total_chunks} chunks")
        return indexed_count

    def index_all_content(self, batch_size: int = 100) -> Dict:
        """
        Process and index all book content.

        Full pipeline: extract -> chunk -> embed -> index

        Args:
            batch_size: Batch size for embedding and indexing

        Returns:
            Dict with indexing statistics
        """
        logger.info("Starting full content indexing pipeline...")

        stats = {
            "files_processed": 0,
            "chunks_created": 0,
            "chunks_embedded": 0,
            "chunks_indexed": 0,
            "errors": [],
        }

        try:
            # Step 1: Extract content from files
            logger.info("Step 1: Extracting content from Markdown files...")
            processed_files = self.content_extractor.process_all_files()
            stats["files_processed"] = len(processed_files)

            if not processed_files:
                logger.warning("No files to process")
                return stats

            # Step 2: Chunk content
            logger.info("Step 2: Chunking content...")
            chunk_dicts = self.chunking_service.chunk_all_files(processed_files)
            stats["chunks_created"] = len(chunk_dicts)

            if not chunk_dicts:
                logger.warning("No chunks created")
                return stats

            # Step 3: Generate embeddings
            logger.info("Step 3: Generating embeddings...")
            chunks = self.generate_embeddings_for_chunks(chunk_dicts, batch_size=batch_size)
            stats["chunks_embedded"] = len(chunks)

            if not chunks:
                logger.warning("No embeddings generated")
                return stats

            # Step 4: Index into Qdrant
            logger.info("Step 4: Indexing into Qdrant...")
            indexed_count = self.index_chunks(chunks, batch_size=batch_size)
            stats["chunks_indexed"] = indexed_count

            logger.info(f"Indexing pipeline complete: {stats}")

        except Exception as e:
            logger.error(f"Indexing pipeline failed: {e}")
            stats["errors"].append(str(e))

        return stats

    def get_indexing_stats(self) -> Dict:
        """
        Get current indexing statistics from Qdrant.

        Returns:
            Dict with collection statistics
        """
        collection_info = self.qdrant_client.get_collection_info()

        if not collection_info:
            return {"error": "Failed to get collection info"}

        return {
            "collection_name": collection_info["name"],
            "total_chunks": collection_info["points_count"],
            "vectors_count": collection_info["vectors_count"],
            "status": collection_info["status"],
            "optimizer_status": collection_info["optimizer_status"],
        }

    def clear_collection(self) -> bool:
        """
        Clear all indexed content from Qdrant.

        CAUTION: This permanently deletes all indexed chunks.

        Returns:
            True if successful, False otherwise
        """
        logger.warning("Clearing collection - all indexed content will be deleted")
        return self.qdrant_client.delete_collection()
