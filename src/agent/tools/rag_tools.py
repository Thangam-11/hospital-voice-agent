from __future__ import annotations

from langchain_core.tools import tool

from src.database.base_engine import AsyncSessionLocal
from src.rag_tools.embedding_layer.bge_embedding import (
    BGEEmbeddingService,
)
from src.rag_tools.retrieval.context_builder import (
    build_context,
)
from src.rag_tools.retrieval.retriever import (
    RetrieverService,
)
from src.rag_tools.vector_store.pgvector_store import (
    PGVectorStore,
)
from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)


@tool
async def search_hospital_policy(
    query: str,
) -> str:
    """
    Search the hospital policy knowledge base.

    Use this tool when the patient asks about hospital policies,
    rules, procedures, visiting hours, registration, billing,
    insurance, privacy, emergencies, or other information that
    should be answered from the hospital policy documents.

    Returns relevant hospital policy context for the agent.
    """

    query = query.strip()

    if not query:
        return (
            "No policy search was performed because "
            "the query was empty."
        )

    logger.info(
        "Hospital policy RAG search started | query=%s",
        query,
    )

    try:
        # --------------------------------------------------
        # 1. Create embedding service
        # --------------------------------------------------

        embedding_service = BGEEmbeddingService(
            device="cpu",
            batch_size=32,
        )

        # --------------------------------------------------
        # 2. Open database session
        # --------------------------------------------------

        async with AsyncSessionLocal() as session:

            # --------------------------------------------------
            # 3. Create pgvector store
            # --------------------------------------------------

            vector_store = PGVectorStore(
                session=session
            )

            # --------------------------------------------------
            # 4. Create custom retriever
            # --------------------------------------------------

            retriever = RetrieverService(
                vector_store=vector_store,
                embedding_service=embedding_service,
                top_k=5,
                similarity_threshold=0.50,
            )

            # --------------------------------------------------
            # 5. Retrieve relevant chunks
            # --------------------------------------------------

            results = await retriever.search(
                query=query
            )

        # --------------------------------------------------
        # 6. Build LLM-ready context
        # --------------------------------------------------

        context = build_context(
            results
        )

        # --------------------------------------------------
        # 7. Handle no relevant policy
        # --------------------------------------------------

        if not context:

            logger.warning(
                "No relevant hospital policy found | query=%s",
                query,
            )

            return (
                "No sufficiently relevant hospital policy "
                "was found for this question. "
                "Do not invent an answer. "
                "Follow the appropriate hospital escalation "
                "procedure if necessary."
            )

        logger.info(
            "Hospital policy RAG search completed | "
            "results=%d | context_length=%d",
            len(results),
            len(context),
        )

        # --------------------------------------------------
        # 8. Return context to Qwen3 agent
        # --------------------------------------------------

        return (
            "Relevant hospital policy context:\n\n"
            + context
        )

    except Exception:

        logger.exception(
            "Hospital policy RAG search failed"
        )

        return (
            "The hospital policy knowledge base is "
            "temporarily unavailable. "
            "Do not invent or guess the policy answer."
        )