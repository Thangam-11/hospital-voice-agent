# src/agent/agent_graph.py

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.agent.context.context_builder import build_task_context
from src.agent.context.context_models import AgentContext
from src.agent.llm_connection import create_llm
from src.agent.prompts import SYSTEM_PROMPT
from src.agent.state import AgentState
from src.utils.logger_exceptions import get_logger

logger = get_logger(__name__)


def _normalize_tool_call_args(tool_calls: list[dict]) -> list[dict]:
    """
    Some OpenRouter providers serving this model occasionally wrap scalar
    argument values in a {'type': ..., 'value': ...} envelope instead of
    passing them directly. Unwrap that shape defensively.
    """
    for call in tool_calls:
        args = call.get("args", {})
        for key, value in list(args.items()):
            if isinstance(value, dict) and set(value.keys()) == {"type", "value"}:
                args[key] = value["value"]
    return tool_calls


def _latest_user_message(messages: list) -> str:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return ""


def _build_agent_context(state: AgentState) -> AgentContext:
    """
    Assembles the AgentContext used for this turn's prompt.

    NOTE: current_task is read from state["intent"] -- this must match
    whatever key your intent-classification step actually writes.
    (The previous version of this file had two divergent copies of this
    logic: one reading state["current_task"], the other state["intent"].
    "intent" is kept here since that's what the compiled graph used.)
    """

    messages = state["messages"]

    return AgentContext(
        user_message=_latest_user_message(messages),
        current_task=state.get("intent"),
        conversation_history=messages[-6:],
        retrieved_context=state.get("retrieved_context") or "",
        patient_verified=bool(state.get("patient_id")),
        verification_attempts=state.get("verification_attempts", 0),
        specialization=state.get("specialization"),
        date_from=state.get("date_from"),
        selected_slot_id=(
            str(state["selected_slot_id"])
            if state.get("selected_slot_id")
            else None
        ),
        slot_confirmed=state.get("slot_confirmed", False),
    )


def build_agent_graph(
    tools: list[BaseTool],
    checkpointer: BaseCheckpointSaver | None = None,
):
    """
    Build and compile the voice agent graph.

    Context building is its own graph node (context_node) rather than
    inline code inside agent_node, matching the Agent Graph -> Context
    Engine -> Qwen3 pipeline in the architecture diagram, and giving
    Langfuse a distinct span to trace for context assembly.
    """

    llm = create_llm()

    # tool_choice="required" forces a tool call every turn. This model
    # unreliably calls tools under "auto" -- it narrates actions in plain
    # text instead of invoking them. respond_to_patient (included in
    # `tools` by the caller) exists so "required" doesn't break ordinary
    # conversational replies.
    llm_with_tools = llm.bind_tools(tools, tool_choice="required")

    async def context_node(state: AgentState) -> dict:

        context = _build_agent_context(state)
        dynamic_context = build_task_context(context)

        logger.info(
            "Context built | task=%s | length=%d",
            context.current_task,
            len(dynamic_context),
        )

        return {"dynamic_context": dynamic_context}

    async def agent_node(state: AgentState) -> dict:

        messages = state["messages"]
        dynamic_context = state.get("dynamic_context", "")

        response = await llm_with_tools.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                SystemMessage(
                    content=f"CURRENT AGENT CONTEXT:\n\n{dynamic_context}"
                ),
                *messages,
            ]
        )

        if response.tool_calls:
            response.tool_calls = _normalize_tool_call_args(response.tool_calls)

        logger.info(
            "agent_node: tool_calls=%s content_preview=%r",
            response.tool_calls,
            (response.content or "")[:150],
        )

        return {"messages": [response]}

    def route_after_agent(state: AgentState):
        last_message = state["messages"][-1]
        tool_calls = getattr(last_message, "tool_calls", None) or []
        if tool_calls:
            return "tools"
        return END  # shouldn't happen with tool_choice="required", but safe fallback

    def route_after_tools(state: AgentState):
        """
        - Hard cutoff once verify_patient's attempt cap is hit.
        - If the tool that just ran was respond_to_patient, end the turn
          immediately instead of forcing another tool call.
        - Otherwise loop back to context_node so the next agent call sees
          freshly rebuilt context (e.g. a newly retrieved_context, or an
          updated selected_slot_id from the tool that just ran).
        """
        if state.get("verification_attempts", 0) >= 2:
            return "escalate"

        for msg in reversed(state["messages"]):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                called_names = {c["name"] for c in msg.tool_calls}
                if called_names == {"respond_to_patient"}:
                    return END
                break

        return "context"

    def escalate_node(state: AgentState):
        return {
            "messages": [
                AIMessage(
                    content=(
                        "I'm having trouble verifying your identity. Let me "
                        "connect you with a staff member who can help."
                    )
                )
            ]
        }

    graph = StateGraph(AgentState)
    graph.add_node("context", context_node)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("escalate", escalate_node)

    graph.add_edge(START, "context")
    graph.add_edge("context", "agent")
    graph.add_conditional_edges(
        "agent", route_after_agent, {"tools": "tools", END: END}
    )
    graph.add_conditional_edges(
        "tools",
        route_after_tools,
        {"context": "context", "escalate": "escalate", END: END},
    )
    graph.add_edge("escalate", END)

    compiled = graph.compile(checkpointer=checkpointer)

    logger.info(
        "Agent graph compiled with %d tools: %s",
        len(tools),
        [t.name for t in tools],
    )

    return compiled