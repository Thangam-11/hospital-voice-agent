"""
Per-process runtime resources for the LiveKit worker.

Resources created here:

1. SQLAlchemy async session factory
   - Used by PatientService / AppointmentService.

2. LangGraph PostgresSaver (sync, wrapped for async use)
   - Used to persist AgentState by thread_id.
   - Deliberately SYNC, not AsyncPostgresSaver: async psycopg
     requires SelectorEventLoop, but LiveKit uses ProactorEventLoop
     on Windows for subprocess support, which causes
     `psycopg.InterfaceError: Psycopg cannot use the
     'ProactorEventLoop' to run in async mode`. Sync psycopg has no
     event-loop restriction, and LangGraph's base checkpointer class
     already runs sync checkpointers in a thread executor when
     called from async graph code (graph.ainvoke()), so this is
     safe to use as-is.

Both resources are created lazily inside the LiveKit job's
running event loop and reused by jobs handled by the same
worker process.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
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
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None

_checkpointer: Optional[PostgresSaver] = None
_checkpointer_cm = None

_init_lock = asyncio.Lock()


# ---------------------------------------------------------------------------
# SQLAlchemy session factory getter
# ---------------------------------------------------------------------------

async def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Return the shared SQLAlchemy session factory for this worker process.

    The factory itself is shared. Each call/turn creates its own
    AsyncSession through:

        async with session_factory() as session:
            ...
    """

    global _engine
    global _session_factory

    if _session_factory is not None:
        return _session_factory

    async with _init_lock:

        if _session_factory is None:

            settings = get_settings()

            logger.info("runtime: creating SQLAlchemy async engine")

            _engine = create_async_engine(
                settings.database_url,
                echo=(settings.environment.lower() == "development"),
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )

            _session_factory = async_sessionmaker(
                bind=_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            logger.info("runtime: SQLAlchemy session factory created")

    return _session_factory


# ---------------------------------------------------------------------------
# LangGraph checkpointer getter
# ---------------------------------------------------------------------------

async def get_checkpointer() -> PostgresSaver:
    """
    Return the shared LangGraph PostgreSQL checkpointer for this
    worker process, creating it on first call.

    Stores LangGraph state keyed by the thread_id supplied by
    runner.handle_turn().
    """

    global _checkpointer
    global _checkpointer_cm

    if _checkpointer is not None:
        return _checkpointer

    async with _init_lock:

        if _checkpointer is None:

            settings = get_settings()

            logger.info("runtime: creating LangGraph PostgreSQL checkpointer (sync)")

            # IMPORTANT: this URL must be compatible with psycopg 3, e.g.
            #   postgresql://user:password@localhost:5432/hospital
            #
            # settings.database_url is SQLAlchemy-style
            # (postgresql+asyncpg://...) for the async engine above.
            # psycopg (used by PostgresSaver) doesn't understand the
            # "+asyncpg" driver suffix, so it's stripped here.
            checkpointer_url = settings.database_url.replace(
                "postgresql+asyncpg://", "postgresql://", 1
            )

            def _create():
                cm = PostgresSaver.from_conn_string(checkpointer_url)
                saver = cm.__enter__()
                saver.setup()
                return cm, saver

            # Runs psycopg's sync connect() in a worker thread so it
            # never touches the ProactorEventLoop directly.
            _checkpointer_cm, _checkpointer = await asyncio.to_thread(_create)

            logger.info("runtime: LangGraph checkpointer ready")

    return _checkpointer


# ---------------------------------------------------------------------------
# Shutdown
# ---------------------------------------------------------------------------

async def shutdown_runtime() -> None:
    """
    Close worker-level resources during shutdown.
    """

    global _engine
    global _session_factory
    global _checkpointer
    global _checkpointer_cm

    logger.info("runtime: shutting down resources")

    # Close LangGraph checkpointer context.
    # NOTE: PostgresSaver's context manager is sync (__exit__, not
    # __aexit__) — run it in a thread to match how it was opened.
    if _checkpointer_cm is not None:

        try:
            await asyncio.to_thread(_checkpointer_cm.__exit__, None, None, None)

        except Exception:
            logger.exception("runtime: failed to close LangGraph checkpointer")

        finally:
            _checkpointer = None
            _checkpointer_cm = None

    # Dispose SQLAlchemy engine
    if _engine is not None:

        try:
            await _engine.dispose()

        except Exception:
            logger.exception("runtime: failed to dispose SQLAlchemy engine")

        finally:
            _engine = None
            _session_factory = None

    logger.info("runtime: shutdown complete")