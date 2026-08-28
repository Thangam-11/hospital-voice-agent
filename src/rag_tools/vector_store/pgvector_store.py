from __future__ import annotations

from typing import Sequence
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configure.settings import get_settings
from src.database.policy_chunk import PolicyChunk
from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)

settings = get_settings()


class PGVectorStore:
    """
    PostgreSQL + pgvector storage for hospital RAG documents.

    Responsibilities:
        1. Store document chunks and embeddings.
        2. Perform vector similarity search.
        3. Delete chunks belonging to a source document.
        4. Preserve metadata for traceability.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        self.session = session

        logger.info(
            "PGVectorStore initialized"
        )

    # ==========================================================
    # ADD CHUNKS
    # ==========================================================

    async def add_chunks(
        self,
        chunks: Sequence[dict],
        embeddings: Sequence[Sequence[float]],
    ) -> int:
        """
        Store document chunks and their embeddings.

        Args:
            chunks:
                Chunk dictionaries produced by PolicyChunker.

            embeddings:
                Embeddings produced by BGEEmbeddingService.

        Returns:
            Number of chunks stored.
        """

        if not chunks:

            logger.warning(
                "No chunks provided for vector storage"
            )

            return 0

        # ------------------------------------------------------
        # Validate chunk / embedding count
        # ------------------------------------------------------

        if len(chunks) != len(embeddings):

            raise ValueError(
                "Number of chunks must match "
                "number of embeddings."
            )

        # ------------------------------------------------------
        # Validate embedding dimension
        # ------------------------------------------------------

        expected_dimension = settings.embedding_dim

        for index, embedding in enumerate(embeddings):

            if len(embedding) != expected_dimension:

                raise ValueError(
                    f"Invalid embedding dimension at index "
                    f"{index}. Expected "
                    f"{expected_dimension}, got "
                    f"{len(embedding)}."
                )

        # ------------------------------------------------------
        # Create database records
        # ------------------------------------------------------

        records: list[PolicyChunk] = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
            strict=True,
        ):

            content = chunk.get("content")

            if not content:

                raise ValueError(
                    "Chunk content cannot be empty."
                )

            metadata = chunk.get(
                "metadata",
                {},
            )

            record = PolicyChunk(
                id=uuid4(),

                content=content,

                embedding=list(embedding),

                source=metadata.get(
                    "source",
                    "unknown",
                ),

                document_type=metadata.get(
                    "document_type",
                    "hospital_policy",
                ),

                section=metadata.get(
                    "section"
                ),

                chunk_id=metadata.get(
                    "chunk_id",
                    str(uuid4()),
                ),

                chunk_number=metadata.get(
                    "chunk_number",
                    1,
                ),

                # IMPORTANT:
                # Your SQLAlchemy model should call
                # this field `chunk_metadata`,
                # not `metadata`.
                chunk_metadata=metadata,
            )

            records.append(record)

        # ------------------------------------------------------
        # Insert into PostgreSQL
        # ------------------------------------------------------

        try:

            self.session.add_all(records)

            await self.session.commit()

            logger.info(
                "Chunks stored successfully | count=%d",
                len(records),
            )

            return len(records)

        except Exception:

            await self.session.rollback()

            logger.exception(
                "Failed to store chunks in pgvector"
            )

            raise

    # ==========================================================
    # SIMILARITY SEARCH
    # ==========================================================

    async def similarity_search(
        self,
        query_embedding: Sequence[float],
        top_k: int = 5,
    ) -> list[tuple[PolicyChunk, float]]:
        """
        Perform cosine-similarity search using pgvector.

        Args:
            query_embedding:
                768-dimensional BGE query embedding.

            top_k:
                Number of results to return.

        Returns:
            List of:

                (
                    PolicyChunk,
                    cosine_distance
                )

        Smaller cosine distance means greater similarity.
        """

        # ------------------------------------------------------
        # Validate query
        # ------------------------------------------------------

        if not query_embedding:

            raise ValueError(
                "Query embedding cannot be empty."
            )

        # ------------------------------------------------------
        # Validate dimension
        # ------------------------------------------------------

        expected_dimension = settings.embedding_dim

        if len(query_embedding) != expected_dimension:

            raise ValueError(
                f"Expected {expected_dimension} dimensions, "
                f"got {len(query_embedding)}."
            )

        # ------------------------------------------------------
        # Validate top_k
        # ------------------------------------------------------

        if top_k <= 0:

            raise ValueError(
                "top_k must be greater than 0."
            )

        logger.info(
            "Running pgvector similarity search | "
            "top_k=%d",
            top_k,
        )

        # ------------------------------------------------------
        # Cosine distance
        #
        # pgvector translates this to:
        #
        # embedding <=> query_vector
        #
        # Smaller distance = more similar
        # ------------------------------------------------------

        distance = (
            PolicyChunk.embedding.cosine_distance(
                list(query_embedding)
            )
        )

        # ------------------------------------------------------
        # SQL query
        # ------------------------------------------------------

        statement = (
            select(
                PolicyChunk,
                distance.label("distance"),
            )
            .order_by(distance)
            .limit(top_k)
        )

        try:

            result = await self.session.execute(
                statement
            )

            rows = result.all()

        except Exception as e:
            import traceback
            print("=== PGVECTOR ERROR ===")
            print(traceback.format_exc())
            logger.exception(
                "pgvector similarity search failed"
            )

            raise

        logger.info(
            "Similarity search completed | results=%d",
            len(rows),
        )

        # ------------------------------------------------------
        # Convert SQLAlchemy result
        # ------------------------------------------------------

        return [
            (
                chunk,
                float(distance_value),
            )
            for chunk, distance_value in rows
        ]

    # ==========================================================
    # DELETE BY SOURCE
    # ==========================================================

    async def delete_by_source(
        self,
        source: str,
    ) -> int:
        """
        Delete all chunks belonging to a source document.

        Useful when a hospital policy is updated and needs
        to be re-ingested.

        Example:

            privacy_policy.md
                    ↓
            delete old chunks
                    ↓
            parse updated document
                    ↓
            chunk
                    ↓
            embed
                    ↓
            insert new chunks
        """

        if not source.strip():

            raise ValueError(
                "Source cannot be empty."
            )

        logger.info(
            "Deleting chunks | source=%s",
            source,
        )

        statement = delete(
            PolicyChunk
        ).where(
            PolicyChunk.source == source
        )

        try:

            result = await self.session.execute(
                statement
            )

            await self.session.commit()

            deleted_count = result.rowcount or 0

            logger.info(
                "Chunks deleted | source=%s | count=%d",
                source,
                deleted_count,
            )

            return deleted_count

        except Exception:

            await self.session.rollback()

            logger.exception(
                "Failed to delete chunks | source=%s",
                source,
            )

            raise