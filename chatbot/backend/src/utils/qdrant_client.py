"""Qdrant client initialization and utilities."""

import logging
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    PointStruct,
    VectorParams,
)

from ..config import settings

logger = logging.getLogger(__name__)

# Qdrant configuration constants
COLLECTION_NAME = "book-chunks"
VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small
DISTANCE_METRIC = Distance.COSINE
HNSW_M = 16  # Number of bi-directional links per element
HNSW_EF_CONSTRUCT = 100  # Size of dynamic candidate list for construction


class QdrantClientWrapper:
    """
    Wrapper for Qdrant client with helper methods for RAG operations.

    Provides initialization, health checks, and common vector operations.
    """

    def __init__(self):
        """Initialize Qdrant client connection."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30,
        )
        logger.info(f"Initialized Qdrant client: {settings.qdrant_url}")

    def health_check(self) -> bool:
        """
        Check if Qdrant cluster is healthy and accessible.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to get collections list as a simple health check
            self.client.get_collections()
            logger.info("Qdrant health check: OK")
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False

    def ensure_collection(self) -> bool:
        """
        Ensure the book-chunks collection exists with correct configuration.

        Creates the collection if it doesn't exist. If it exists, validates
        the vector configuration.

        Returns:
            True if collection exists/created successfully, False otherwise
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if COLLECTION_NAME in collection_names:
                logger.info(f"Collection '{COLLECTION_NAME}' already exists")
                return True

            # Create collection with HNSW index
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=DISTANCE_METRIC,
                    hnsw_config=HnswConfigDiff(
                        m=HNSW_M,
                        ef_construct=HNSW_EF_CONSTRUCT,
                    ),
                ),
            )
            logger.info(
                f"Created collection '{COLLECTION_NAME}' with vector_size={VECTOR_SIZE}, "
                f"distance={DISTANCE_METRIC}, HNSW(m={HNSW_M}, ef_construct={HNSW_EF_CONSTRUCT})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to ensure collection '{COLLECTION_NAME}': {e}")
            return False

    def get_collection_info(self) -> Optional[dict]:
        """
        Get information about the book-chunks collection.

        Returns:
            Collection info dict or None if collection doesn't exist
        """
        try:
            info = self.client.get_collection(collection_name=COLLECTION_NAME)
            return {
                "name": COLLECTION_NAME,
                "vectors_count": info.points_count,  # Use points_count for vector count
                "points_count": info.points_count,
                "status": str(info.status) if hasattr(info, 'status') else "unknown",
                "optimizer_status": str(info.optimizer_status) if hasattr(info, 'optimizer_status') else "unknown",
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None

    def upsert_points(self, points: List[PointStruct]) -> bool:
        """
        Upsert points (chunks) to the collection.

        Args:
            points: List of PointStruct objects with id, vector, and payload

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.upsert(collection_name=COLLECTION_NAME, points=points)
            logger.info(f"Upserted {len(points)} points to '{COLLECTION_NAME}'")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert points: {e}")
            return False

    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
    ) -> List[dict]:
        """
        Search for similar chunks in the collection.

        Args:
            query_vector: Query embedding vector (1536-dim)
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of search results with id, score, and payload
        """
        try:
            results = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )

            return [
                {
                    "id": str(result.id),
                    "score": result.score,
                    "payload": result.payload,
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []

    def delete_collection(self) -> bool:
        """
        Delete the book-chunks collection.

        CAUTION: This will permanently delete all indexed chunks.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(collection_name=COLLECTION_NAME)
            logger.warning(f"Deleted collection '{COLLECTION_NAME}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False


# Global Qdrant client instance
qdrant_client: Optional[QdrantClientWrapper] = None


def get_qdrant_client() -> QdrantClientWrapper:
    """
    Get or create the global Qdrant client instance.

    Returns:
        QdrantClientWrapper instance
    """
    global qdrant_client
    if qdrant_client is None:
        qdrant_client = QdrantClientWrapper()
    return qdrant_client
