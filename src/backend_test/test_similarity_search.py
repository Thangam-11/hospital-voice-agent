import asyncio

from src.database.base_engine import AsyncSessionLocal
from src.rag_tools.embedding_layer.bge_embedding import (
    BGEEmbeddingService,
)
from src.rag_tools.vector_store.pgvector_store import (
    PGVectorStore,
)


async def test_similarity_search() -> None:

    # ==================================================
    # 1. User question
    # ==================================================

    question = (
        "What are the visitor rules for ICU?"
    )

    print("\n" + "=" * 70)
    print("QUESTION")
    print("=" * 70)
    print(question)

    # ==================================================
    # 2. Convert question → BGE embedding
    # ==================================================

    embedding_service = BGEEmbeddingService(
        device="cpu",
        batch_size=32,
    )

    query_embedding = (
        embedding_service.embed_query(
            question
        )
    )

    print(
        f"\nQuery embedding dimension: "
        f"{len(query_embedding)}"
    )

    # ==================================================
    # 3. Search PostgreSQL + pgvector
    # ==================================================

    async with AsyncSessionLocal() as session:

        vector_store = PGVectorStore(
            session=session
        )

        results = (
            await vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=5,
            )
        )

    # ==================================================
    # 4. Display retrieved chunks
    # ==================================================

    print("\n" + "=" * 70)
    print("TOP RETRIEVED CHUNKS")
    print("=" * 70)

    for index, (chunk, distance) in enumerate(
        results,
        start=1,
    ):

        print(
            f"\n--- Result #{index} ---"
        )

        print(
            f"Distance : {distance:.4f}"
        )

        print(
            f"Source   : {chunk.source}"
        )

        print(
            f"Section  : {chunk.section}"
        )

        print(
            f"Chunk ID : {chunk.chunk_id}"
        )

        print(
            "\nContent:"
        )

        print(chunk.content)


if __name__ == "__main__":

    asyncio.run(
        test_similarity_search()
    )