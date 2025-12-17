"""Chunk model representing a segment of book content with embedding."""

from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """
    Represents a semantically coherent segment of book content.

    Stored in Qdrant with embedding and metadata for retrieval.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the chunk")
    text: str = Field(..., min_length=100, max_length=2000, description="Chunk text content")
    embedding: List[float] = Field(
        ..., min_length=1536, max_length=1536, description="1536-dim OpenAI embedding"
    )
    chapter: str = Field(..., min_length=1, description="Chapter title or number")
    section: str = Field(..., min_length=1, description="Section title")
    page: int | None = Field(None, ge=1, description="Page number (optional)")
    passage_id: str = Field(
        ...,
        pattern=r"^ch\d+-sec\d+-p\d+$",
        description="Human-readable identifier (e.g., ch3-sec2-p45)",
    )
    source_file: str = Field(..., min_length=1, description="Original Markdown file path")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when chunk was indexed"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "text": "The optimal chunk size for technical documentation is 500-1000 tokens with 100-token overlap.",
                "embedding": [0.023, -0.041, 0.015],  # Truncated for example
                "chapter": "Chapter 3: RAG Systems",
                "section": "3.2 Retrieval Strategies",
                "page": 45,
                "passage_id": "ch3-sec2-p45",
                "source_file": "content/chapter-3.md",
                "created_at": "2025-12-15T10:30:00Z",
            }
        }

    def to_qdrant_payload(self) -> dict:
        """Convert Chunk to Qdrant payload format (metadata only, no embedding)."""
        return {
            "text": self.text,
            "chapter": self.chapter,
            "section": self.section,
            "page": self.page,
            "passage_id": self.passage_id,
            "source_file": self.source_file,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_qdrant_point(cls, point_id: str, vector: List[float], payload: dict) -> "Chunk":
        """Create Chunk from Qdrant point."""
        return cls(
            id=UUID(point_id),
            text=payload["text"],
            embedding=vector,
            chapter=payload["chapter"],
            section=payload["section"],
            page=payload.get("page"),
            passage_id=payload["passage_id"],
            source_file=payload["source_file"],
            created_at=datetime.fromisoformat(payload["created_at"]),
        )
