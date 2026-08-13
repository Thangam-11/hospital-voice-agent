"""
Per-process runtime resources for the LiveKit worker.

Resources:

1. SQLAlchemy async session factory
   - Used by PatientService / AppointmentService.

2. LangGraph AsyncPostgresSaver
   - Used to persist AgentState by thread_id.
   - Required because the LangGraph graph uses async execution
     via graph.ainvoke() and async nodes.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.configure.settings import get_settings
from src.utils.logger_exceptions import get_logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Process-level resources
# ---------------------------------------------------------------------------

_engine: Optional[AsyncEngine] = None

_session_factory: Optional[
    async_sessionmaker[AsyncSession]
] = None

_checkpointer: Optional[AsyncPostgresSaver] = None

_checkpointer_cm = None

_init_lock = asyncio.Lock()


# ---------------------------------------------------------------------------
# SQLAlchemy session factory
# ---------------------------------------------------------------------------

async def get_session_factory() -> async_sessionmaker[AsyncSession]:

    global _engine
    global _session_factory

    if _session_factory is not None:
        return _session_factory

    async with _init_lock:

        if _session_factory is None:

            settings = get_settings()

            logger.info(
                "runtime: creating SQLAlchemy async engine"
            )

            _engine = create_async_engine(
                settings.database_url,
                echo=(
                    settings.environment.lower()
                    == "development"
                ),
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )

            _session_factory = async_sessionmaker(
                bind=_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            logger.info(
                "runtime: SQLAlchemy async session factory ready"
            )

    return _session_factory


# ---------------------------------------------------------------------------
# LangGraph Async PostgreSQL checkpointer
# ---------------------------------------------------------------------------

async def get_checkpointer() -> AsyncPostgresSaver:

    global _checkpointer
    global _checkpointer_cm

    if _checkpointer is not None:
        return _checkpointer

    async with _init_lock:

        if _checkpointer is None:

            settings = get_settings()

            logger.info(
                "runtime: creating LangGraph "
                "PostgreSQL ASYNC checkpointer"
            )

            # Your SQLAlchemy URL is:
            #
            # postgresql+asyncpg://...
            #
            # Psycopg expects:
            #
            # postgresql://...
            #
            checkpointer_url = settings.database_url.replace(
                "postgresql+asyncpg://",
                "postgresql://",
                1,
            )

            logger.info(
                "runtime: initializing AsyncPostgresSaver"
            )

            _checkpointer_cm = (
                AsyncPostgresSaver.from_conn_string(
                    checkpointer_url
                )
            )

            _checkpointer = (
                await _checkpointer_cm.__aenter__()
            )

            await _checkpointer.setup()

            logger.info(
                "runtime: LangGraph AsyncPostgresSaver ready"
            )

    return _checkpointer


# ---------------------------------------------------------------------------
# Shutdown
# ---------------------------------------------------------------------------

async def shutdown_runtime() -> None:

    global _engine
    global _session_factory
    global _checkpointer
    global _checkpointer_cm

    logger.info(
        "runtime: shutting down resources"
    )

    # ---------------------------------------------------------
    # Close LangGraph async checkpointer
    # ---------------------------------------------------------

    if _checkpointer_cm is not None:

        try:

            await _checkpointer_cm.__aexit__(
                None,
                None,
                None,
            )

        except Exception:

            logger.exception(
                "runtime: failed to close "
                "LangGraph async checkpointer"
            )

        finally:

            _checkpointer = None
            _checkpointer_cm = None

    # ---------------------------------------------------------
    # Dispose SQLAlchemy engine
    # ---------------------------------------------------------

    if _engine is not None:

        try:

            await _engine.dispose()

        except Exception:

            logger.exception(
                "runtime: failed to dispose "
                "SQLAlchemy async engine"
            )

        finally:

            _engine = None
            _session_factory = None

    logger.info(
        "runtime: shutdown complete"
    )