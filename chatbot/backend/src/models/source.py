"""Source model representing a citation to a book passage."""

from pydantic import BaseModel, Field


class Source(BaseModel):
    """
    Represents a citation to a specific book passage.

    Used to provide traceability from chatbot answers to source content.
    """

    passage_id: str = Field(
        ...,
        pattern=r"^(ch\d+-sec\d+-p\d+|selected-text)$",
        description="Human-readable identifier (e.g., ch3-sec2-p45 or selected-text)",
    )
    chapter: str = Field(..., min_length=1, description="Chapter title or number")
    section: str = Field(..., min_length=1, description="Section title")
    page: int | None = Field(None, ge=1, description="Page number (optional)")
    snippet: str = Field(
        ..., min_length=1, max_length=200, description="Excerpt from the source passage"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "passage_id": "ch3-sec2-p45",
                "chapter": "Chapter 3: RAG Systems",
                "section": "3.2 Retrieval Strategies",
                "page": 45,
                "snippet": "The optimal chunk size for technical documentation is 500-1000 tokens with 100-token overlap.",
            }
        }

    def to_dict(self) -> dict:
        """Convert Source to dictionary for JSONB storage."""
        return {
            "passage_id": self.passage_id,
            "chapter": self.chapter,
            "section": self.section,
            "page": self.page,
            "snippet": self.snippet,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Source":
        """Create Source from dictionary."""
        return cls(
            passage_id=data["passage_id"],
            chapter=data["chapter"],
            section=data["section"],
            page=data.get("page"),
            snippet=data["snippet"],
        )
