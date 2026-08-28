import asyncio

from src.database.base_engine import AsyncSessionLocal
from src.rag_tools.embedding_layer.bge_embedding import (
    BGEEmbeddingService,
)
from src.rag_tools.vector_store.pgvector_store import (
    PGVectorStore,
)
from src.rag_tools.retrieval.retriever import (
    RetrieverService,
)
from src.rag_tools.retrieval.context_builder import (
    build_context,
)


async def main() -> None:

    query = (
        "What are the visitor rules for ICU?"
    )

    embedding_service = BGEEmbeddingService(
        device="cpu",
        batch_size=32,
    )

    async with AsyncSessionLocal() as session:

        vector_store = PGVectorStore(
            session=session
        )

        retriever = RetrieverService(
            vector_store=vector_store,
            embedding_service=embedding_service,
            top_k=5,
            similarity_threshold=0.50,
        )

        results = await retriever.search(
            query=query
        )

    print("\n" + "=" * 70)
    print("QUERY")
    print("=" * 70)

    print(query)

    print("\n" + "=" * 70)
    print("RETRIEVED RESULTS")
    print("=" * 70)

    for index, result in enumerate(
        results,
        start=1,
    ):

        chunk = result.chunk

        print(
            f"\n--- Result {index} ---"
        )

        print(
            f"Similarity: {result.score:.4f}"
        )

        print(
            f"Source: {chunk.source}"
        )

        print(
            f"Section: {chunk.section}"
        )

        print(
            f"Chunk ID: {chunk.chunk_id}"
        )

        print(
            f"\n{chunk.content}"
        )

    context = build_context(
        results
    )

    print("\n" + "=" * 70)
    print("LLM CONTEXT")
    print("=" * 70)

    print(context)


if __name__ == "__main__":

    asyncio.run(main())