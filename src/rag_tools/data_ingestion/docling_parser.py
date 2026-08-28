from pathlib import Path

from docling.document_converter import DocumentConverter

from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)


class DoclingParser:
    """Parse hospital policy documents using Docling."""

    def __init__(self) -> None:
        self.converter = DocumentConverter()
        logger.info("Docling parser initialized")

    def parse_file(self, file_path: str | Path):
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(
                "Policy file not found: %s",
                file_path,
            )
            raise FileNotFoundError(file_path)

        try:
            logger.info(
                "Parsing policy with Docling: %s",
                file_path.name,
            )

            result = self.converter.convert(
                str(file_path)
            )

            document = result.document

            logger.info(
                "Docling parsing completed: %s",
                file_path.name,
            )

            return document

        except Exception:
            logger.exception(
                "Docling parsing failed: %s",
                file_path.name,
            )
            raise