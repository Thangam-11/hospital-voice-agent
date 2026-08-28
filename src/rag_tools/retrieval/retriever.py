from __future__ import annotations

from typing import Optional

from src.rag_tools.embedding_layer.bge_embedding import (
    BGEEmbeddingService,
)
from src.rag_tools.vector_store.pgvector_store import (
    PGVectorStore,
)
from src.rag_tools.retrieval.retrieval_models import (
    RetrievedChunk,
)
from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)


class RetrieverService:
    """
    Custom retrieval pipeline for hospital policy RAG.

    Pipeline:

        question
            ↓
        BGE embedding
            ↓
        pgvector search
            ↓
        similarity filtering
            ↓
        ranked chunks
    """

    def __init__(
        self,
        vector_store: PGVectorStore,
        embedding_service: BGEEmbeddingService,
        top_k: int = 5,
        similarity_threshold: float = 0.50,
    ) -> None:

        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

        logger.info(
            "RetrieverService initialized | top_k=%d | threshold=%.2f",
            top_k,
            similarity_threshold,
        )

    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> list[RetrievedChunk]:
        """
        Retrieve relevant hospital policy chunks.

        Args:
            query:
                User's natural-language question.

            top_k:
                Number of candidates to retrieve.

        Returns:
            Ranked list of RetrievedChunk objects.
        """

        # --------------------------------------------------
        # 1. Validate query
        # --------------------------------------------------

        query = query.strip()

        if not query:
            raise ValueError(
                "Retrieval query cannot be empty."
            )

        k = top_k or self.top_k

        logger.info(
            "Starting retrieval | query=%s | top_k=%d",
            query,
            k,
        )

        # --------------------------------------------------
        # 2. Convert query → BGE embedding
        # --------------------------------------------------

        query_embedding = (
            self.embedding_service.embed_query(
                query
            )
        )

        logger.info(
            "Query embedding generated | dimension=%d",
            len(query_embedding),
        )

        # --------------------------------------------------
        # 3. Search pgvector
        # --------------------------------------------------

        results = await self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=k,
        )

        logger.info(
            "Vector search returned | candidates=%d",
            len(results),
        )

        # --------------------------------------------------
        # 4. Convert distance → similarity score
        # --------------------------------------------------

        retrieved_chunks: list[RetrievedChunk] = []

        for chunk, distance in results:

            similarity = 1.0 - distance

            logger.debug(
                "Candidate | source=%s | chunk_id=%s | "
                "distance=%.4f | similarity=%.4f",
                chunk.source,
                chunk.chunk_id,
                distance,
                similarity,
            )

            # --------------------------------------------------
            # 5. Similarity threshold
            # --------------------------------------------------

            if similarity < self.similarity_threshold:

                logger.debug(
                    "Chunk rejected by similarity threshold | "
                    "chunk_id=%s | similarity=%.4f",
                    chunk.chunk_id,
                    similarity,
                )

                continue

            retrieved_chunks.append(
                RetrievedChunk(
                    chunk=chunk,
                    distance=distance,
                )
            )

        logger.info(
            "Retrieval completed | returned=%d",
            len(retrieved_chunks),
        )

        return retrieved_chunks