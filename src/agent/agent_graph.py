# src/agent/agent_graph.py

from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

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


def build_agent_graph(
    tools: list[BaseTool],
    checkpointer: BaseCheckpointSaver | None = None,
):
    """
    Build and compile the voice agent graph.
    """

    llm = create_llm()

    # tool_choice="required" forces a tool call every turn. This model
    # unreliably calls tools under "auto" — it narrates actions in plain
    # text instead of invoking them. respond_to_patient (included in
    # `tools` by the caller) exists so "required" doesn't break ordinary
    # conversational replies.
    llm_with_tools = llm.bind_tools(tools, tool_choice="required")

    async def agent_node(state: AgentState) -> dict:
        messages = state["messages"]

        response = await llm_with_tools.ainvoke(
            [SystemMessage(content=SYSTEM_PROMPT), *messages]
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
        - Otherwise loop back to the agent as normal.
        """
        if state.get("verification_attempts", 0) >= 2:
            return "escalate"

        for msg in reversed(state["messages"]):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                called_names = {c["name"] for c in msg.tool_calls}
                if called_names == {"respond_to_patient"}:
                    return END
                break

        return "agent"

    def escalate_node(state: AgentState):
        return {
            "messages": [AIMessage(content=(
                "I'm having trouble verifying your identity. Let me connect "
                "you with a staff member who can help."
            ))]
        }

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("escalate", escalate_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent", route_after_agent, {"tools": "tools", END: END}
    )
    graph.add_conditional_edges(
        "tools", route_after_tools, {"agent": "agent", "escalate": "escalate", END: END}
    )
    graph.add_edge("escalate", END)

    compiled = graph.compile(checkpointer=checkpointer)

    logger.info(
        "Agent graph compiled with %d tools: %s",
        len(tools),
        [t.name for t in tools],
    )

    return compiled