from langgraph.checkpoint.base import BaseCheckpointSaver

from src.agent.agent_graph import build_agent_graph
from src.agent.tools.agent_tools import create_appointment_tools
from src.agent.tools.rag_tools import search_hospital_policy
from src.service.appointment_service import AppointmentService
from src.service.patient_service import PatientService


def build_agent(
    appointment_service: AppointmentService,
    patient_service: PatientService,
    checkpointer: BaseCheckpointSaver,
):
    """
    Builds a compiled agent graph bound to specific service instances.
    """

    # Existing appointment/patient tools
    tools = create_appointment_tools(
        appointment_service,
        patient_service,
    )

    # Add hospital policy RAG tool
    tools.append(search_hospital_policy)

    # Pass all tools to the agent graph
    return build_agent_graph(
        tools=tools,
        checkpointer=checkpointer,
    )