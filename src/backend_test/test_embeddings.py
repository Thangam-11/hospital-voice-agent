from src.rag_tools.embedding_layer.bge_embedding import (
    BGEEmbeddingService,
)


def main() -> None:

    print("\n=== BGE Embedding Test ===\n")

    # ---------------------------------------------------------
    # 1. Initialize embedding service
    # ---------------------------------------------------------

    embedding_service = BGEEmbeddingService(
        device="cpu",
        batch_size=32,
    )

    # ---------------------------------------------------------
    # 2. Test document embeddings
    # ---------------------------------------------------------

    documents = [
        "Patients can request an appointment with an available doctor.",
        "Patient identity should be verified before providing patient-specific information.",
        "Visitors must follow hospital visitor rules and instructions.",
    ]

    print(
        f"Creating embeddings for {len(documents)} documents..."
    )

    embeddings = embedding_service.embed_documents(
        documents
    )

    # ---------------------------------------------------------
    # 3. Validate document embeddings
    # ---------------------------------------------------------

    print("\n=== Document Embedding Result ===")

    print(
        f"Number of embeddings: {len(embeddings)}"
    )

    if embeddings:
        print(
            f"Embedding dimension: {len(embeddings[0])}"
        )

        print(
            f"First 5 values: {embeddings[0][:5]}"
        )

    # ---------------------------------------------------------
    # 4. Test query embedding
    # ---------------------------------------------------------

    query = "How can I book an appointment?"

    print("\n=== Query Embedding ===")

    print(f"Query: {query}")

    query_embedding = (
        embedding_service.embed_query(query)
    )

    print(
        f"Query embedding dimension: "
        f"{len(query_embedding)}"
    )

    print(
        f"First 5 values: "
        f"{query_embedding[:5]}"
    )

    # ---------------------------------------------------------
    # 5. Validate dimensions
    # ---------------------------------------------------------

    assert len(embeddings) == len(documents)

    assert all(
        len(vector) == 768
        for vector in embeddings
    )

    assert len(query_embedding) == 768

    print("\n=== Validation ===")

    print("Document count: PASS")
    print("Document dimension: PASS")
    print("Query dimension: PASS")

    print("\n✅ BGE embedding test completed successfully.")


if __name__ == "__main__":
    main()