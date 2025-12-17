"""Response model representing a chatbot answer with sources and metadata."""

from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

from .source import Source


class Response(BaseModel):
    """
    Represents a chatbot-generated answer with sources and metadata.

    Stored in Neon Postgres for analytics and traceability.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the response")
    query_id: UUID = Field(..., description="ID of the associated query")
    answer: str = Field(..., description="Chatbot-generated answer text")
    sources: List[Source] = Field(
        default_factory=list, description="List of source citations for the answer"
    )
    confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="Confidence score (0.0-1.0) for the answer"
    )
    refused: bool = Field(False, description="True if chatbot refused to answer")
    refusal_reason: str | None = Field(
        None, description="Explanation for refusal (e.g., insufficient context)"
    )
    latency_ms: int | None = Field(
        None, ge=0, description="Response generation latency in milliseconds"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when response was generated"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "query_id": "650e8400-e29b-41d4-a716-446655440001",
                "answer": "The optimal chunk size for RAG systems is 500-1000 tokens with 100-token overlap.",
                "sources": [
                    {
                        "passage_id": "ch3-sec2-p45",
                        "chapter": "Chapter 3: RAG Systems",
                        "section": "3.2 Retrieval Strategies",
                        "page": 45,
                        "snippet": "The optimal chunk size for technical documentation is 500-1000 tokens...",
                    }
                ],
                "confidence": 0.92,
                "refused": False,
                "refusal_reason": None,
                "latency_ms": 1250,
                "timestamp": "2025-12-15T10:30:05Z",
            }
        }

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, v: str, info) -> str:
        """Validate that answer is non-empty if not refused."""
        refused = info.data.get("refused", False)
        if not refused and not v.strip():
            raise ValueError("answer must be non-empty when refused is False")
        return v

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, v: List[Source], info) -> List[Source]:
        """Validate that sources are provided if not refused."""
        refused = info.data.get("refused", False)
        if not refused and len(v) == 0:
            raise ValueError("sources must be non-empty when refused is False")
        return v

    @field_validator("refusal_reason")
    @classmethod
    def validate_refusal_reason(cls, v: str | None, info) -> str | None:
        """Validate that refusal_reason is provided if refused."""
        refused = info.data.get("refused", False)
        if refused and not v:
            raise ValueError("refusal_reason is required when refused is True")
        if not refused and v:
            raise ValueError("refusal_reason must be None when refused is False")
        return v

    def to_db_dict(self) -> dict:
        """Convert Response to database format."""
        return {
            "id": str(self.id),
            "query_id": str(self.query_id),
            "answer_text": self.answer,
            "sources": [source.to_dict() for source in self.sources],
            "confidence": self.confidence,
            "refused": self.refused,
            "refusal_reason": self.refusal_reason,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_db_row(cls, row: dict) -> "Response":
        """Create Response from database row."""
        return cls(
            id=UUID(row["id"]),
            query_id=UUID(row["query_id"]),
            answer=row["answer_text"],
            sources=[Source.from_dict(s) for s in row.get("sources", [])],
            confidence=row.get("confidence"),
            refused=row.get("refused", False),
            refusal_reason=row.get("refusal_reason"),
            latency_ms=row.get("latency_ms"),
            timestamp=row["timestamp"],
        )
