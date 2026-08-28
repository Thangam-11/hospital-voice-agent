from src.rag_tools.retrieval.retrieval_models import (
    RetrievedChunk,
)


def build_context(
    results: list[RetrievedChunk],
) -> str:

    if not results:
        return ""

    context_parts: list[str] = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        chunk = result.chunk

        context_parts.append(
            f"""
SOURCE {index}
Document: {chunk.source}
Section: {chunk.section or "Unknown"}
Chunk ID: {chunk.chunk_id}
Similarity: {result.score:.4f}

Content:
{chunk.content}
""".strip()
        )

    return "\n\n".join(
        context_parts
    )