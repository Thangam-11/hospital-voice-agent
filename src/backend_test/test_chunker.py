from pathlib import Path

from src.rag_tools.data_ingestion.docling_parser import (
    DoclingParser,
)
from src.rag_tools.data_ingestion.chunker import (
    PolicyChunker,
)


POLICY_DIR = (
    Path(__file__).resolve().parents[1]
    / "knowledge_base"
    / "policies"
)


def main() -> None:

    parser = DoclingParser()

    chunker = PolicyChunker(
        target_words=450,
        max_words=600,
        overlap_words=60,
    )

    files = sorted(
        POLICY_DIR.glob("*.md")
    )

    print(f"Found {len(files)} policy files")

    total_chunks = 0

    for file_path in files:

        # ---------------------------------------------
        # Markdown → DoclingDocument
        # ---------------------------------------------

        document = parser.parse_file(
            file_path
        )

        # ---------------------------------------------
        # DoclingDocument → normalized Markdown
        # ---------------------------------------------

        markdown = document.export_to_markdown()

        # ---------------------------------------------
        # Markdown → structured chunks
        # ---------------------------------------------

        chunks = chunker.chunk_document(
            document_markdown=markdown,
            source=file_path.name,
        )

        total_chunks += len(chunks)

        print("\n" + "=" * 70)
        print(f"Source: {file_path.name}")
        print(f"Chunks: {len(chunks)}")
        print("=" * 70)

        for chunk in chunks:

            print(
                f"\nChunk ID: "
                f"{chunk['metadata']['chunk_id']}"
            )

            print(
                f"Section: "
                f"{chunk['metadata']['section']}"
            )

            print(
                f"Words: "
                f"{len(chunk['content'].split())}"
            )

            print(
                chunk["content"][:300]
            )

    print("\n" + "=" * 70)
    print(f"TOTAL CHUNKS: {total_chunks}")
    print("=" * 70)


if __name__ == "__main__":
    main()