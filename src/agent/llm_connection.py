# src/agent/llm.py

from langchain_openai import ChatOpenAI

from src.configure.settings import get_settings
from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)


def create_llm():
    settings = get_settings()

    logger.info("Creating LLM with model from settings: %s", settings.llm_model)

    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0,
        max_tokens=500,
    )