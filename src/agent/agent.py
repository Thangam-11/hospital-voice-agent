# src/agent/agent.py

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from src.agent.tools.appointment_tools import (
    find_available_slots,
    book_appointment,
    cancel_appointment,
    check_appointment_status,
)
from src.utils.logger_exceptions import get_logger
from src.configure.settings import get_settings

settings = get_settings()
logger = get_logger()

# ---------------------------------------------------------
# 1. Agent state
# ---------------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ---------------------------------------------------------
# 2. LLM
# ---------------------------------------------------------

llm = ChatOpenAI(
    model=settings.llm_model,
    temperature=0,
)


# ---------------------------------------------------------
# 3. Tools
# ---------------------------------------------------------

tools = [
    find_available_slots,
    book_appointment,
    cancel_appointment,
    check_appointment_status,
]

llm_with_tools = llm.bind_tools(tools)


# ---------------------------------------------------------
# 4. Agent node
# ---------------------------------------------------------

async def agent_node(state: AgentState):

    response = await llm_with_tools.ainvoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


# ---------------------------------------------------------
# 5. Build LangGraph
# ---------------------------------------------------------

graph_builder = StateGraph(AgentState)

graph_builder.add_node(
    "agent",
    agent_node
)

graph_builder.add_node(
    "tools",
    ToolNode(tools)
)

graph_builder.add_edge(
    START,
    "agent"
)

graph_builder.add_conditional_edges(
    "agent",
    tools_condition
)

graph_builder.add_edge(
    "tools",
    "agent"
)

graph_builder.add_edge(
    "agent",
    END
)


# ---------------------------------------------------------
# 6. Compile
# ---------------------------------------------------------

agent = graph_builder.compile()