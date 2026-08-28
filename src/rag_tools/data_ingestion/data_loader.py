from pathlib import Path

from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)

POLICY_DIR = (
    Path(__file__).resolve().parents[2]
    / "knowledge_base"
    / "policies"
)


def load_markdown_files() -> list[dict]:
    """
    Load all Markdown policy documents from the policies directory.

    Returns:
        list[dict]: Documents containing content and metadata.
    """

    documents: list[dict] = []

    logger.info("Starting policy document loading")
    logger.info("Policy directory: %s", POLICY_DIR)

    if not POLICY_DIR.exists():
        logger.error(
            "Policy directory does not exist: %s",
            POLICY_DIR,
        )
        return documents

    markdown_files = sorted(POLICY_DIR.glob("*.md"))

    logger.info(
        "Found %d Markdown policy files",
        len(markdown_files),
    )

    for file_path in markdown_files:

        try:
            content = file_path.read_text(
                encoding="utf-8"
            ).strip()

            if not content:
                logger.warning(
                    "Skipping empty policy file: %s",
                    file_path.name,
                )
                continue

            documents.append(
                {
                    "content": content,
                    "metadata": {
                        "source": file_path.name,
                        "file_path": str(file_path),
                        "file_type": "markdown",
                    },
                }
            )

            logger.info(
                "Loaded policy: %s | characters=%d",
                file_path.name,
                len(content),
            )

        except OSError:
            logger.exception(
                "Failed to read policy file: %s",
                file_path,
            )

    logger.info(
        "Policy loading completed | documents_loaded=%d",
        len(documents),
    )

    return documents

if __name__ == "__main__":
    documents = load_markdown_files()

    print(f"Loaded documents: {len(documents)}")