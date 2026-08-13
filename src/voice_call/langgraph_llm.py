"""
LiveKit LLM adapter for the existing LangGraph hospital agent.

Flow:

    LiveKit STT
        |
        | user text
        v
    LangGraphLLM
        |
        v
    _run_agent_turn()
        |
        v
    LangGraph
        |
        +--> Qwen / OpenRouter
        |
        +--> Hospital tools
        |
        v
    final response text
        |
        v
    LiveKit TTS
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from livekit.agents import llm
from livekit.agents.llm import ChatChunk, ChoiceDelta
from livekit.agents.types import (
    APIConnectOptions,
    DEFAULT_API_CONNECT_OPTIONS,
    NOT_GIVEN,
    NotGivenOr,
)

from src.utils.logger_exceptions import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# LangGraph currently returns one complete response.
# It is NOT token streaming.
_CHUNK_DELAY_SECONDS = 0.0


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

RunAgentTurn = Callable[[str, str], Awaitable[str]]


# ---------------------------------------------------------------------------
# LangGraph LLM
# ---------------------------------------------------------------------------


class LangGraphLLM(llm.LLM):
    """
    Makes the existing LangGraph hospital agent look like a LiveKit LLM.

    LiveKit calls:
        chat()

    This adapter calls:
        _run_agent_turn(thread_id, user_text)
    """

    def __init__(
        self,
        *,
        run_agent_turn: RunAgentTurn,
        thread_id: str,
    ) -> None:
        super().__init__()

        self._run_agent_turn = run_agent_turn
        self._thread_id = thread_id

        logger.info(
            "LangGraphLLM initialized | thread_id=%s",
            thread_id,
        )

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        tools: list[llm.Tool] | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice: NotGivenOr[llm.ToolChoice] = NOT_GIVEN,
        extra_kwargs: NotGivenOr[dict[str, Any]] = NOT_GIVEN,
    ) -> "LangGraphLLMStream":

        return LangGraphLLMStream(
            self,
            chat_ctx=chat_ctx,
            tools=tools or [],
            conn_options=conn_options,
            run_agent_turn=self._run_agent_turn,
            thread_id=self._thread_id,
        )

    def label(self) -> str:
        return "langgraph-hospital-agent"


# ---------------------------------------------------------------------------
# LangGraph LLM Stream
# ---------------------------------------------------------------------------


class LangGraphLLMStream(llm.LLMStream):
    """
    Connects one LiveKit LLM turn to one LangGraph turn.

    Flow:

        ChatContext
            |
            v
        latest user text
            |
            v
        _run_agent_turn()
            |
            v
        final LangGraph response
            |
            v
        ChatChunk
    """

    def __init__(
        self,
        llm_instance: LangGraphLLM,
        *,
        chat_ctx: llm.ChatContext,
        tools: list[llm.Tool],
        conn_options: APIConnectOptions,
        run_agent_turn: RunAgentTurn,
        thread_id: str,
    ) -> None:

        super().__init__(
            llm_instance,
            chat_ctx=chat_ctx,
            tools=tools,
            conn_options=conn_options,
        )

        self._run_agent_turn = run_agent_turn
        self._thread_id = thread_id

    # -----------------------------------------------------------------------
    # Main LiveKit execution
    # -----------------------------------------------------------------------

    async def _run(self) -> None:

        user_text = self._latest_user_text()

        if not user_text:
            logger.warning(
                "LangGraphLLMStream: no user message found | "
                "thread_id=%s",
                self._thread_id,
            )

            self._emit_response(
                "Sorry, I didn't hear anything. "
                "Could you please repeat that?"
            )
            return

        logger.info(
            "LangGraphLLMStream: processing user text | "
            "thread_id=%s | text=%r",
            self._thread_id,
            user_text,
        )

        try:
            # ---------------------------------------------------------------
            # Call existing LangGraph hospital agent
            # ---------------------------------------------------------------

            reply_text = await self._run_agent_turn(
                self._thread_id,
                user_text,
            )

            logger.info(
                "LangGraph response received | "
                "thread_id=%s | response=%r",
                self._thread_id,
                reply_text,
            )

        except Exception as exc:

            logger.exception(
                "LangGraph agent FAILED | "
                "thread_id=%s | error=%s",
                self._thread_id,
                exc,
            )

            # IMPORTANT:
            # Re-raise during debugging so we can see the real error.
            raise

        # -------------------------------------------------------------------
        # Empty response protection
        # -------------------------------------------------------------------

        if not reply_text:

            logger.warning(
                "LangGraph returned empty response | "
                "thread_id=%s",
                self._thread_id,
            )

            self._emit_response(
                "I'm sorry, I couldn't generate a response. "
                "Could you please try again?"
            )
            return

        # -------------------------------------------------------------------
        # Send response to LiveKit
        # -------------------------------------------------------------------

        self._emit_response(reply_text)

    # -----------------------------------------------------------------------
    # Emit response
    # -----------------------------------------------------------------------

    def _emit_response(self, text: str) -> None:
        """
        Send LangGraph response to LiveKit.

        LangGraph currently returns a complete response rather than
        streaming tokens, so we split the response into chunks.
        """

        chunks = self._chunk(text)

        for chunk_text in chunks:

            self._event_ch.send_nowait(
                ChatChunk(
                    id=self._thread_id,
                    delta=ChoiceDelta(
                        role="assistant",
                        content=chunk_text,
                    ),
                )
            )

            if _CHUNK_DELAY_SECONDS:
                # Currently unused.
                pass

    # -----------------------------------------------------------------------
    # Extract latest user message
    # -----------------------------------------------------------------------

    def _latest_user_text(self) -> str:
        """
        Extract the latest user message from LiveKit ChatContext.
        """

        for message in reversed(self._chat_ctx.items):

            role = getattr(message, "role", None)

            if role != "user":
                continue

            # Newer LiveKit message objects
            text_content = getattr(
                message,
                "text_content",
                None,
            )

            if text_content:
                return text_content.strip()

            # Fallback for content stored as parts
            content = getattr(
                message,
                "content",
                None,
            )

            if isinstance(content, list):

                parts = [
                    str(part).strip()
                    for part in content
                    if isinstance(part, str)
                    and part.strip()
                ]

                if parts:
                    return " ".join(parts)

            if content:
                return str(content).strip()

        return ""

    # -----------------------------------------------------------------------
    # Chunk response
    # -----------------------------------------------------------------------

    @staticmethod
    def _chunk(text: str) -> list[str]:
        """
        Split final response into word-sized chunks.

        Example:

            "What date would you prefer?"

        becomes approximately:

            "What "
            "date "
            "would "
            "you "
            "prefer?"
        """

        text = text.strip()

        if not text:
            return []

        words = text.split()

        return [
            f"{word} "
            for word in words[:-1]
        ] + [words[-1]]