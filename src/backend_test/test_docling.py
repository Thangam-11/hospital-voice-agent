from pathlib import Path

from src.rag_tools.data_ingestion.docling_parser import DoclingParser


POLICY_DIR = (
    Path(__file__).resolve().parents[1]
    / "knowledge_base"
    / "policies"
)


def main() -> None:

    parser = DoclingParser()

    print(f"Policy directory: {POLICY_DIR}")

    files = sorted(POLICY_DIR.glob("*.md"))

    print(f"Found {len(files)} policy files")

    for file_path in files:

        document = parser.parse_file(file_path)

        print("\n" + "=" * 60)
        print(f"File: {file_path.name}")
        print(f"Type: {type(document).__name__}")
        print("=" * 60)

        markdown = document.export_to_markdown()

        print(markdown[:500])


if __name__ == "__main__":
    main()