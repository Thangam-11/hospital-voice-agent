from typing import Sequence

from sentence_transformers import SentenceTransformer

from src.configure.settings import get_settings
from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)

settings = get_settings()


class BGEEmbeddingService:
    """
    Local embedding service using BAAI/bge-base-en-v1.5.
    """

    MODEL_NAME = settings.embedding_model
    EMBEDDING_DIMENSION = settings.embedding_dim

    def __init__(
        self,
        device: str = "cpu",
        batch_size: int = 32,
    ) -> None:

        self.device = device
        self.batch_size = batch_size

        logger.info(
            "Loading embedding model | model=%s | device=%s",
            self.MODEL_NAME,
            self.device,
        )

        self.model = SentenceTransformer(
            self.MODEL_NAME,
            device=self.device,
            local_files_only=True,
        )

        actual_dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        if actual_dimension != self.EMBEDDING_DIMENSION:
            raise ValueError(
                f"Embedding dimension mismatch | "
                f"configured={self.EMBEDDING_DIMENSION} | "
                f"actual={actual_dimension}"
            )

        logger.info(
            "Embedding model loaded | dimension=%d",
            actual_dimension,
        )

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        """
        Convert document chunks into embeddings.
        """

        if not texts:
            logger.warning(
                "No documents provided for embedding"
            )
            return []

        logger.info(
            "Creating document embeddings | count=%d",
            len(texts),
        )

        embeddings = self.model.encode(
            list(texts),
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        result = embeddings.tolist()

        logger.info(
            "Document embeddings created | "
            "count=%d | dimension=%d",
            len(result),
            len(result[0]) if result else 0,
        )

        return result

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Convert a user query into an embedding.
        """

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        logger.info(
            "Creating query embedding"
        )

        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        result = embedding.tolist()

        logger.info(
            "Query embedding created | dimension=%d",
            len(result),
        )

        return result