"""Query model representing a user question submitted to the chatbot."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator


class QueryMode(str, Enum):
    """Retrieval modes for chatbot queries."""

    SELECTED_TEXT = "selected-text"
    BOOK_WIDE = "book-wide"


class Query(BaseModel):
    """
    Represents a user question submitted to the RAG chatbot.

    Stored in Neon Postgres for analytics and session tracking.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the query")
    session_id: UUID | None = Field(None, description="Session identifier for multi-turn conversations")
    text: str = Field(..., min_length=1, max_length=2000, description="User question text")
    mode: QueryMode = Field(..., description="Retrieval mode: selected-text or book-wide")
    context: str | None = Field(
        None, max_length=10000, description="User-selected text (required for selected-text mode)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when query was submitted"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "session_id": "650e8400-e29b-41d4-a716-446655440001",
                "text": "What is the optimal chunk size for RAG systems?",
                "mode": "book-wide",
                "context": None,
                "timestamp": "2025-12-15T10:30:00Z",
            }
        }

    @field_validator("context")
    @classmethod
    def validate_context(cls, v: str | None, info) -> str | None:
        """Validate that context is provided for selected-text mode."""
        mode = info.data.get("mode")
        if mode == QueryMode.SELECTED_TEXT and not v:
            raise ValueError("context is required when mode is 'selected-text'")
        if mode == QueryMode.BOOK_WIDE and v:
            raise ValueError("context must be None when mode is 'book-wide'")
        return v

    def to_db_dict(self) -> dict:
        """Convert Query to database format."""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id) if self.session_id else None,
            "query_text": self.text,
            "mode": self.mode.value,
            "context_text": self.context,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_db_row(cls, row: dict) -> "Query":
        """Create Query from database row."""
        return cls(
            id=UUID(row["id"]),
            session_id=UUID(row["session_id"]) if row.get("session_id") else None,
            text=row["query_text"],
            mode=QueryMode(row["mode"]),
            context=row.get("context_text"),
            timestamp=row["timestamp"],
        )
