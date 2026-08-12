"""
LangGraph LLM Adapter for LiveKit.

This module plugs the existing LangGraph hospital agent (see
`voice_agent._run_agent_turn`) into LiveKit's voice pipeline as a
custom `llm.LLM` implementation.

Pipeline position (per your architecture diagram):

    Deepgram STT --text--> LangGraphLLMAdapter --text--> ElevenLabs TTS
                                   |
                                   v
                          _run_agent_turn()
                                   |
                                   v
                       LangGraph + Qwen 3 (+ tools)

IMPORTANT:
LiveKit's `llm.LLM` interface is a *streaming* interface: it expects
a `chat()` call to return an `LLMStream` that yields `ChatChunk`
objects incrementally. Your underlying LangGraph agent is NOT
streaming today — `_run_agent_turn()` returns one complete string
after `ainvoke()` finishes.

To bridge this without changing your agent internals, this adapter:
    1. Extracts the latest user message from LiveKit's ChatContext
    2. Calls `_run_agent_turn(thread_id, user_text)`
    3. Emits the full response as a single ChatChunk

This keeps your LangGraph/Qwen reasoning layer completely untouched.
If you later make `_run_agent_turn` a true async generator (streaming
tokens), swap the single "yield full text" call below for a loop that
yields as tokens arrive — the rest of this adapter stays the same.
"""

from __future__ import annotations

from typing import Any

from livekit.agents import llm
from livekit.agents.llm import ChatChunk, ChatContext, ChoiceDelta
from livekit.agents.types import APIConnectOptions, DEFAULT_API_CONNECT_OPTIONS

from src.utils.logger_exceptions import get_logger
from src.voice_agent import _run_agent_turn  # your existing shared function

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_latest_user_text(chat_ctx: ChatContext) -> str:
    """
    Pull the most recent user message out of LiveKit's ChatContext.

    LiveKit appends the new user turn (from STT) to chat_ctx before
    calling chat(), so the last "user" role message is what we need
    to send into the LangGraph agent.
    """

    for item in reversed(chat_ctx.items):
        role = getattr(item, "role", None)

        if role == "user":
            content = getattr(item, "text_content", None)

            if content:
                return content.strip()

            # Fallback for content stored as a list of parts
            content_list = getattr(item, "content", None)

            if isinstance(content_list, list):
                parts = [
                    str(part) for part in content_list if isinstance(part, str)
                ]

                if parts:
                    return " ".join(parts).strip()

    return ""


# ---------------------------------------------------------------------------
# LLMStream implementation
# ---------------------------------------------------------------------------

class LangGraphLLMStream(llm.LLMStream):
    """
    Single-shot LLMStream that wraps one call to _run_agent_turn().

    LiveKit expects streamed ChatChunks; since the LangGraph agent
    currently returns one final string, we emit exactly one chunk
    containing the full response.
    """

    def __init__(
        self,
        adapter: "LangGraphLLMAdapter",
        *,
        chat_ctx: ChatContext,
        thread_id: str,
        conn_options: APIConnectOptions,
    ) -> None:
        super().__init__(
            adapter,
            chat_ctx=chat_ctx,
            tools=[],
            conn_options=conn_options,
        )
        self._thread_id = thread_id

    async def _run(self) -> None:
        user_text = _extract_latest_user_text(self._chat_ctx)

        if not user_text:
            logger.warning(
                "LangGraphLLMStream: no user text found in chat_ctx | thread_id=%s",
                self._thread_id,
            )
            response_text = "Sorry, I didn't hear anything. Could you please repeat that?"
        else:
            response_text = await _run_agent_turn(
                thread_id=self._thread_id,
                user_text=user_text,
            )

        chunk = ChatChunk(
            id=self._thread_id,
            delta=ChoiceDelta(role="assistant", content=response_text),
        )

        self._event_ch.send_nowait(chunk)


# ---------------------------------------------------------------------------
# LLM implementation
# ---------------------------------------------------------------------------

class LangGraphLLMAdapter(llm.LLM):
    """
    Custom LiveKit `llm.LLM` implementation backed by the existing
    LangGraph + Qwen 3 hospital agent.

    Usage in your LiveKit AgentSession setup:

        from langgraph_llm_adapter import LangGraphLLMAdapter

        session = AgentSession(
            vad=silero.VAD.load(),
            stt=deepgram.STT(),
            llm=LangGraphLLMAdapter(),      # <-- this adapter
            tts=elevenlabs.TTS(),
        )

    `thread_id` is derived per-session from the LiveKit room name so
    that LangGraph's checkpointer keeps separate conversation state
    per call.
    """

    def __init__(self, *, default_thread_id: str | None = None) -> None:
        super().__init__()
        self._default_thread_id = default_thread_id

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools: list[Any] | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        thread_id: str | None = None,
        **kwargs: Any,
    ) -> LangGraphLLMStream:
        """
        Returns an LLMStream for this turn.

        `thread_id` should be passed by the caller (e.g. the LiveKit
        room name / call SID) so conversation state is scoped per
        call. Falls back to `default_thread_id` if not provided —
        set that explicitly if you construct one adapter instance
        per session.
        """

        resolved_thread_id = (
            thread_id or self._default_thread_id or "default-thread"
        )

        return LangGraphLLMStream(
            self,
            chat_ctx=chat_ctx,
            thread_id=resolved_thread_id,
            conn_options=conn_options,
        )

    def label(self) -> str:
        return "langgraph-qwen3-hospital-agent"