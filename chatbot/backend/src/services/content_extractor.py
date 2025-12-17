"""Content extraction service for processing Markdown book files."""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ContentExtractor:
    """
    Extracts and parses content from Markdown book files.

    Handles chapter/section detection, metadata extraction, and content organization.
    """

    def __init__(self, content_dir: str = "content"):
        """
        Initialize ContentExtractor.

        Args:
            content_dir: Directory containing Markdown book files
        """
        self.content_dir = Path(content_dir)
        logger.info(f"Initialized ContentExtractor with content_dir: {self.content_dir}")

    def list_markdown_files(self) -> List[Path]:
        """
        List all Markdown files in the content directory.

        Returns:
            List of Path objects for .md files
        """
        if not self.content_dir.exists():
            logger.warning(f"Content directory does not exist: {self.content_dir}")
            return []

        md_files = sorted(self.content_dir.glob("**/*.md"))
        logger.info(f"Found {len(md_files)} Markdown files")
        return md_files

    def read_file(self, file_path: Path) -> str:
        """
        Read content from a Markdown file.

        Args:
            file_path: Path to Markdown file

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            logger.debug(f"Read {len(content)} characters from {file_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise

    def extract_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """
        Extract YAML frontmatter from Markdown content.

        Args:
            content: Raw Markdown content

        Returns:
            Tuple of (frontmatter_dict, content_without_frontmatter)
        """
        frontmatter = {}
        body = content

        # Check for YAML frontmatter (---\n...\n---)
        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, content, re.DOTALL)

        if match:
            yaml_str = match.group(1)
            body = match.group(2)

            # Simple YAML parsing (key: value pairs)
            for line in yaml_str.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()

            logger.debug(f"Extracted frontmatter: {frontmatter}")

        return frontmatter, body

    def extract_chapter_info(self, content: str, file_path: Path) -> Optional[Dict]:
        """
        Extract chapter information from content.

        Looks for patterns like:
        - # Chapter 3: RAG Systems
        - # 3. RAG Systems

        Args:
            content: Markdown content
            file_path: Source file path (fallback for chapter detection)

        Returns:
            Dict with chapter_num, chapter_title, or None
        """
        # Pattern 1: "# Chapter N: Title"
        pattern1 = r"^#\s+Chapter\s+(\d+)[:\-\s]+(.+)$"
        match = re.search(pattern1, content, re.MULTILINE | re.IGNORECASE)
        if match:
            return {
                "chapter_num": int(match.group(1)),
                "chapter_title": match.group(2).strip(),
                "chapter_full": f"Chapter {match.group(1)}: {match.group(2).strip()}",
            }

        # Pattern 2: "# N. Title"
        pattern2 = r"^#\s+(\d+)\.\s+(.+)$"
        match = re.search(pattern2, content, re.MULTILINE)
        if match:
            return {
                "chapter_num": int(match.group(1)),
                "chapter_title": match.group(2).strip(),
                "chapter_full": f"Chapter {match.group(1)}: {match.group(2).strip()}",
            }

        # Fallback: extract from filename (e.g., chapter-3-rag-systems.md)
        filename = file_path.stem
        pattern3 = r"chapter[-_](\d+)"
        match = re.search(pattern3, filename, re.IGNORECASE)
        if match:
            chapter_num = int(match.group(1))
            return {
                "chapter_num": chapter_num,
                "chapter_title": filename.replace(f"chapter-{chapter_num}", "").strip("-_"),
                "chapter_full": f"Chapter {chapter_num}",
            }

        logger.warning(f"Could not extract chapter info from {file_path}")
        return None

    def extract_sections(self, content: str) -> List[Dict]:
        """
        Extract section information from content.

        Looks for patterns like:
        - ## 3.2 Retrieval Strategies
        - ## Retrieval Strategies

        Args:
            content: Markdown content

        Returns:
            List of dicts with section_num, section_title, section_content
        """
        sections = []

        # Split by ## headers
        section_pattern = r"^##\s+(.+)$"
        lines = content.split("\n")

        current_section = None
        current_content = []

        for line in lines:
            match = re.match(section_pattern, line)
            if match:
                # Save previous section
                if current_section:
                    sections.append(
                        {
                            "section_title": current_section,
                            "section_content": "\n".join(current_content).strip(),
                        }
                    )

                # Start new section
                current_section = match.group(1).strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            sections.append(
                {
                    "section_title": current_section,
                    "section_content": "\n".join(current_content).strip(),
                }
            )

        logger.debug(f"Extracted {len(sections)} sections")
        return sections

    def process_file(self, file_path: Path) -> Dict:
        """
        Process a Markdown file and extract all metadata and content.

        Args:
            file_path: Path to Markdown file

        Returns:
            Dict with frontmatter, chapter_info, sections, raw_content
        """
        logger.info(f"Processing file: {file_path}")

        # Read file
        raw_content = self.read_file(file_path)

        # Extract frontmatter
        frontmatter, body = self.extract_frontmatter(raw_content)

        # Extract chapter info
        chapter_info = self.extract_chapter_info(body, file_path)

        # Extract sections
        sections = self.extract_sections(body)

        return {
            "file_path": str(file_path),
            "frontmatter": frontmatter,
            "chapter_info": chapter_info,
            "sections": sections,
            "raw_content": body,
        }

    def process_all_files(self) -> List[Dict]:
        """
        Process all Markdown files in content directory.

        Returns:
            List of processed file dicts
        """
        md_files = self.list_markdown_files()
        processed_files = []

        for file_path in md_files:
            try:
                processed = self.process_file(file_path)
                processed_files.append(processed)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                continue

        logger.info(f"Successfully processed {len(processed_files)}/{len(md_files)} files")
        return processed_files
