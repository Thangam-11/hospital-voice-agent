# src/agent/agent_core.py
#
# Thin compatibility wrapper. The graph itself lives in graph.py, the
# LLM client in llm_connection.py. This file exists so existing call
# sites (main.py, runner.py) importing `build_agent` don't need to
# change their call shape.

from langgraph.checkpoint.base import BaseCheckpointSaver

from src.agent.agent_graph import build_agent_graph
from src.agent.agent_tools import create_appointment_tools
from src.service.appointment_service import AppointmentService
from src.service.patient_service import PatientService


def build_agent(
    appointment_service: AppointmentService,
    patient_service: PatientService,
    checkpointer: BaseCheckpointSaver,
):
    """
    Builds a compiled agent graph bound to specific service instances.

    checkpointer MUST be a single shared instance held for the app's
    lifetime (or per-call in the Twilio path) — NOT created fresh here.
    Rebuilding the graph itself per request/turn is fine (services are
    session-scoped and can't be reused across requests), but state
    persistence depends entirely on reusing the same checkpointer
    instance across calls to this function for the same thread_id.
    """
    tools = create_appointment_tools(appointment_service, patient_service)
    return build_agent_graph(tools=tools, checkpointer=checkpointer)