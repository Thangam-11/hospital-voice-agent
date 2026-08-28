from src.database.base_engine import AsyncSessionLocal

from src.rag_tools.data_ingestion.data_loader import (
    load_markdown_files,
)
from src.rag_tools.data_ingestion.docling_parser import (
    DoclingParser,
)
from src.rag_tools.data_ingestion.chunker import (
    PolicyChunker,
)
from src.rag_tools.embedding_layer.bge_embedding import (
    BGEEmbeddingService,
)
from src.rag_tools.vector_store.pgvector_store import (
    PGVectorStore,
)
from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)


async def ingest_policies() -> None:

    logger.info(
        "Starting hospital policy ingestion"
    )

    # ==================================================
    # 1. LOAD
    # ==================================================

    documents = load_markdown_files()

    logger.info(
        "Documents loaded | count=%d",
        len(documents),
    )

    if not documents:
        logger.warning(
            "No policy documents found"
        )
        return

    # ==================================================
    # 2. PARSE + 3. CHUNK
    # ==================================================

    parser = DoclingParser()
    chunker = PolicyChunker()

    all_chunks: list[dict] = []

    for document in documents:

        source = document["metadata"]["source"]

        file_path = document["metadata"]["file_path"]

        logger.info(
            "Processing policy | source=%s",
            source,
        )

        # ----------------------------------------------
        # Docling parsing
        # ----------------------------------------------

        docling_document = parser.parse_file(
            file_path
        )

        # ----------------------------------------------
        # Convert DoclingDocument → Markdown
        # ----------------------------------------------

        markdown = (
            docling_document.export_to_markdown()
        )

        # ----------------------------------------------
        # Chunk
        # ----------------------------------------------

        chunks = chunker.chunk_document(
            document_markdown=markdown,
            source=source,
        )

        all_chunks.extend(chunks)

        logger.info(
            "Policy processed | source=%s | chunks=%d",
            source,
            len(chunks),
        )

    logger.info(
        "Chunking completed | total_chunks=%d",
        len(all_chunks),
    )

    if not all_chunks:
        logger.warning(
            "No chunks generated"
        )
        return

    # ==================================================
    # 4. EMBEDDING
    # ==================================================

    embedding_service = BGEEmbeddingService(
        device="cpu",
        batch_size=32,
    )

    texts = [
        chunk["content"]
        for chunk in all_chunks
    ]

    logger.info(
        "Creating embeddings | count=%d",
        len(texts),
    )

    embeddings = (
        embedding_service.embed_documents(
            texts
        )
    )

    logger.info(
        "Embeddings generated | count=%d | dimension=%d",
        len(embeddings),
        len(embeddings[0]) if embeddings else 0,
    )

    # ==================================================
    # 5. STORE IN POSTGRESQL + PGVECTOR
    # ==================================================

    async with AsyncSessionLocal() as session:

        vector_store = PGVectorStore(
            session=session
        )

        # ----------------------------------------------
        # Remove old chunks before re-ingestion
        # ----------------------------------------------

        sources = {
            chunk["metadata"]["source"]
            for chunk in all_chunks
        }

        logger.info(
            "Preparing policy re-ingestion | sources=%d",
            len(sources),
        )

        for source in sources:

            deleted_count = (
                await vector_store.delete_by_source(
                    source
                )
            )

            logger.info(
                "Old chunks removed | source=%s | count=%d",
                source,
                deleted_count,
            )

        # ----------------------------------------------
        # Insert new chunks + embeddings
        # ----------------------------------------------

        stored_count = (
            await vector_store.add_chunks(
                chunks=all_chunks,
                embeddings=embeddings,
            )
        )

    logger.info(
        "Policy ingestion completed | stored=%d",
        stored_count,
    )


if __name__ == "__main__":

    import asyncio

    asyncio.run(
        ingest_policies()
    )