"""Book content API routes for serving markdown chapters to frontend."""

import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/book", tags=["Book"])


class BookChapter(BaseModel):
    """Model for a book chapter."""

    id: str
    number: int
    title: str
    content: str


@router.get("/chapters", response_model=List[BookChapter])
async def get_chapters():
    """
    Get all book chapters with their content.

    Returns:
        List of chapters with full markdown content

    Note:
        This endpoint will always return successfully, even if some files
        fail to load. Individual file errors are logged but don't fail the request.
    """
    content_dir = Path("content")

    if not content_dir.exists():
        logger.warning(f"Content directory not found: {content_dir}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content directory not found. Please ensure the 'content' directory exists with markdown files."
        )

    chapters = []
    md_files = sorted(content_dir.glob("*.md"))

    if not md_files:
        logger.warning(f"No markdown files found in {content_dir}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No markdown files found in content directory"
        )

    for idx, md_file in enumerate(md_files, start=1):
        try:
            # Read file with explicit encoding
            content = md_file.read_text(encoding="utf-8")

            # Validate content is not empty
            if not content.strip():
                logger.warning(f"Empty content in {md_file.name}, skipping")
                continue

            # Extract title from filename or first heading
            title = _extract_title(content, md_file.stem)

            chapters.append(BookChapter(
                id=f"chapter-{idx}",
                number=idx,
                title=title,
                content=content
            ))
            logger.info(f"Successfully loaded chapter: {title}")

        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {md_file.name}: {e}")
            # Add a placeholder chapter for failed files
            chapters.append(BookChapter(
                id=f"chapter-{idx}",
                number=idx,
                title=f"Error loading {md_file.stem}",
                content=f"# Error\n\nFailed to load content from {md_file.name} due to encoding issues."
            ))
        except Exception as e:
            logger.error(f"Unexpected error reading {md_file.name}: {e}", exc_info=True)
            # Add a placeholder chapter for failed files
            chapters.append(BookChapter(
                id=f"chapter-{idx}",
                number=idx,
                title=f"Error loading {md_file.stem}",
                content=f"# Error\n\nFailed to load content from {md_file.name}: {str(e)}"
            ))

    if not chapters:
        logger.error("All chapter files failed to load")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load any chapters. Check server logs for details."
        )

    logger.info(f"Successfully loaded {len(chapters)} chapters")
    return chapters


def _extract_title(content: str, fallback: str) -> str:
    """
    Extract title from markdown content.

    Args:
        content: Markdown content
        fallback: Fallback title if extraction fails

    Returns:
        Extracted title or fallback
    """
    lines = content.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("title:"):
            return line[6:].strip()

    # Fallback: use filename and clean it up
    return fallback.replace("-", " ").replace("_", " ").title()
