import re
from pathlib import Path

from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)


class PolicyChunker:
    """
    Structure-aware chunker for hospital policy documents.

    Strategy:
        1. Split by Markdown headings.
        2. Preserve heading context.
        3. Keep small sections intact.
        4. Split large sections by paragraphs.
        5. Apply token/word-size fallback.
        6. Add small overlap between large chunks.
    """

    def __init__(
        self,
        target_words: int = 450,
        max_words: int = 600,
        overlap_words: int = 60,
    ) -> None:

        self.target_words = target_words
        self.max_words = max_words
        self.overlap_words = overlap_words

        logger.info(
            "PolicyChunker initialized | "
            "target=%d words | max=%d words | overlap=%d words",
            target_words,
            max_words,
            overlap_words,
        )

    def chunk_document(
        self,
        document_markdown: str,
        source: str,
    ) -> list[dict]:

        sections = self._split_sections(
            document_markdown
        )

        chunks: list[dict] = []

        for section_index, section in enumerate(sections):

            section_chunks = self._process_section(
                section=section,
                source=source,
                section_index=section_index,
            )

            chunks.extend(section_chunks)

        logger.info(
            "Chunking completed | source=%s | chunks=%d",
            source,
            len(chunks),
        )

        return chunks

    # ---------------------------------------------------------
    # Split document by headings
    # ---------------------------------------------------------

    def _split_sections(
        self,
        markdown: str,
    ) -> list[dict]:

        lines = markdown.splitlines()

        sections: list[dict] = []

        current_heading = "General"
        current_level = 0
        current_content: list[str] = []

        for line in lines:

            heading_match = re.match(
                r"^(#{1,6})\s+(.+)$",
                line.strip(),
            )

            if heading_match:

                if current_content:
                    sections.append(
                        {
                            "heading": current_heading,
                            "level": current_level,
                            "content": "\n".join(
                                current_content
                            ).strip(),
                        }
                    )

                current_level = len(
                    heading_match.group(1)
                )

                current_heading = (
                    heading_match.group(2).strip()
                )

                current_content = []

            else:
                current_content.append(line)

        # Add final section
        if current_content:
            sections.append(
                {
                    "heading": current_heading,
                    "level": current_level,
                    "content": "\n".join(
                        current_content
                    ).strip(),
                }
            )

        return [
            section
            for section in sections
            if section["content"]
        ]

    # ---------------------------------------------------------
    # Process one section
    # ---------------------------------------------------------

    def _process_section(
        self,
        section: dict,
        source: str,
        section_index: int,
    ) -> list[dict]:

        heading = section["heading"]
        content = section["content"]

        words = content.split()

        # Small section → keep intact
        if len(words) <= self.max_words:

            return [
                self._create_chunk(
                    source=source,
                    section=heading,
                    content=content,
                    chunk_number=1,
                    section_index=section_index,
                )
            ]

        # Large section → split
        paragraphs = self._split_paragraphs(
            content
        )

        return self._build_chunks_from_paragraphs(
            paragraphs=paragraphs,
            source=source,
            section=heading,
            section_index=section_index,
        )

    # ---------------------------------------------------------
    # Paragraph splitting
    # ---------------------------------------------------------

    def _split_paragraphs(
        self,
        content: str,
    ) -> list[str]:

        paragraphs = re.split(
            r"\n\s*\n",
            content,
        )

        return [
            paragraph.strip()
            for paragraph in paragraphs
            if paragraph.strip()
        ]

    # ---------------------------------------------------------
    # Build chunks from paragraphs
    # ---------------------------------------------------------

    def _build_chunks_from_paragraphs(
        self,
        paragraphs: list[str],
        source: str,
        section: str,
        section_index: int,
    ) -> list[dict]:

        chunks: list[dict] = []

        current_words: list[str] = []
        chunk_number = 1

        for paragraph in paragraphs:

            paragraph_words = paragraph.split()

            # If adding paragraph exceeds max,
            # finalize current chunk.
            if (
                current_words
                and len(current_words)
                + len(paragraph_words)
                > self.max_words
            ):

                content = " ".join(current_words)

                chunks.append(
                    self._create_chunk(
                        source=source,
                        section=section,
                        content=content,
                        chunk_number=chunk_number,
                        section_index=section_index,
                    )
                )

                chunk_number += 1

                # Keep overlap
                current_words = current_words[
                    -self.overlap_words:
                ]

            current_words.extend(
                paragraph_words
            )

            # Target reached
            if len(current_words) >= self.target_words:

                content = " ".join(current_words)

                chunks.append(
                    self._create_chunk(
                        source=source,
                        section=section,
                        content=content,
                        chunk_number=chunk_number,
                        section_index=section_index,
                    )
                )

                chunk_number += 1

                current_words = current_words[
                    -self.overlap_words:
                ]

        # Remaining content
        if current_words:

            content = " ".join(current_words)

            chunks.append(
                self._create_chunk(
                    source=source,
                    section=section,
                    content=content,
                    chunk_number=chunk_number,
                    section_index=section_index,
                )
            )

        return chunks

    # ---------------------------------------------------------
    # Create chunk
    # ---------------------------------------------------------

    def _create_chunk(
        self,
        source: str,
        section: str,
        content: str,
        chunk_number: int,
        section_index: int,
    ) -> dict:

        chunk_id = (
            f"{Path(source).stem}"
            f"_{section_index:03d}"
            f"_{chunk_number:03d}"
        )

        return {
            "content": (
                f"Document: {source}\n"
                f"Section: {section}\n\n"
                f"{content}"
            ),
            "metadata": {
                "source": source,
                "document_type": "hospital_policy",
                "section": section,
                "chunk_id": chunk_id,
                "chunk_number": chunk_number,
            },
        }