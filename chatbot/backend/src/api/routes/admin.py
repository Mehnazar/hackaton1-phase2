"""Admin API routes for indexing and management operations."""

import logging
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from ...services import IndexingService
from ...utils.chunking import generate_embedding
from ...utils.qdrant_client import get_qdrant_client
from ..dependencies import AdminAPIKey

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# Request/Response models
class IndexingRequest(BaseModel):
    """Request model for indexing operations."""

    content_dir: str = Field(
        default="content",
        description="Directory containing Markdown book files",
    )
    batch_size: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Batch size for embedding and indexing",
    )


class IndexingResponse(BaseModel):
    """Response model for indexing operations."""

    success: bool
    message: str
    stats: Dict


class StatsResponse(BaseModel):
    """Response model for stats endpoint."""

    collection_name: str
    total_chunks: int
    vectors_count: int
    status: str
    optimizer_status: str


class SearchTestRequest(BaseModel):
    """Request model for search test."""

    query: str = Field(..., min_length=1, max_length=500, description="Test query")
    limit: int = Field(default=5, ge=1, le=20, description="Number of results")


class SearchTestResponse(BaseModel):
    """Response model for search test."""

    query: str
    results: list
    count: int


@router.post(
    "/index",
    response_model=IndexingResponse,
    summary="Index all book content",
    description="Process and index all Markdown files in the content directory. "
    "This will extract content, chunk it, generate embeddings, and store in Qdrant.",
)
async def index_content(
    request: IndexingRequest,
    api_key: AdminAPIKey,
) -> IndexingResponse:
    """
    Index all book content into Qdrant.

    Requires admin API key (X-API-Key header).
    """
    logger.info(f"Starting indexing from {request.content_dir}")

    try:
        indexing_service = IndexingService(content_dir=request.content_dir)
        stats = indexing_service.index_all_content(batch_size=request.batch_size)

        if stats["chunks_indexed"] == 0:
            return IndexingResponse(
                success=False,
                message="No chunks were indexed. Check logs for errors.",
                stats=stats,
            )

        return IndexingResponse(
            success=True,
            message=f"Successfully indexed {stats['chunks_indexed']} chunks from {stats['files_processed']} files",
            stats=stats,
        )

    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {str(e)}",
        )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get indexing statistics",
    description="Get current statistics about indexed content in Qdrant.",
)
async def get_stats(api_key: AdminAPIKey) -> StatsResponse:
    """
    Get indexing statistics.

    Requires admin API key (X-API-Key header).
    """
    try:
        indexing_service = IndexingService()
        stats = indexing_service.get_indexing_stats()

        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=stats["error"],
            )

        return StatsResponse(**stats)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}",
        )


@router.post(
    "/search-test",
    response_model=SearchTestResponse,
    summary="Test semantic search",
    description="Test semantic search functionality by searching for similar chunks. "
    "Useful for debugging and validation.",
)
async def search_test(
    request: SearchTestRequest,
    api_key: AdminAPIKey,
) -> SearchTestResponse:
    """
    Test semantic search.

    Requires admin API key (X-API-Key header).
    """
    try:
        # Generate embedding for query
        logger.info(f"Testing search for query: {request.query}")
        query_embedding = generate_embedding(request.query)

        # Search Qdrant
        qdrant_client = get_qdrant_client()
        results = qdrant_client.search(
            query_vector=query_embedding,
            limit=request.limit,
        )

        # Format results
        formatted_results = [
            {
                "score": result["score"],
                "passage_id": result["payload"].get("passage_id"),
                "chapter": result["payload"].get("chapter"),
                "section": result["payload"].get("section"),
                "text_snippet": result["payload"].get("text", "")[:200] + "...",
            }
            for result in results
        ]

        return SearchTestResponse(
            query=request.query,
            results=formatted_results,
            count=len(formatted_results),
        )

    except Exception as e:
        logger.error(f"Search test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search test failed: {str(e)}",
        )


@router.delete(
    "/collection",
    summary="Delete collection",
    description="Delete the entire book-chunks collection from Qdrant. "
    "⚠️ CAUTION: This permanently deletes all indexed content.",
)
async def delete_collection(
    api_key: AdminAPIKey,
    confirm: bool = Query(
        False,
        description="Must be set to true to confirm deletion",
    ),
) -> Dict:
    """
    Delete the book-chunks collection.

    Requires admin API key (X-API-Key header) and confirm=true query parameter.
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must set confirm=true to delete collection",
        )

    logger.warning("Deleting book-chunks collection")

    try:
        qdrant_client = get_qdrant_client()
        success = qdrant_client.delete_collection()

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete collection",
            )

        # Recreate empty collection
        qdrant_client.ensure_collection()

        return {
            "success": True,
            "message": "Collection deleted and recreated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete collection: {str(e)}",
        )
