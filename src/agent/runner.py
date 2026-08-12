# src/agent/runner.py

from langgraph.errors import GraphRecursionError
from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_core.messages import HumanMessage

from src.agent.agent_core import build_agent
from src.agent.state import initial_state
from src.service.appointment_service import AppointmentService
from src.service.patient_service import PatientService
from src.utils.logger_exceptions import get_logger

logger = get_logger(__name__)


async def handle_turn(
    session_factory,
    checkpointer: BaseCheckpointSaver,
    call_sid: str,
    patient_utterance: str,
    caller_phone_number: str | None = None,
) -> str:
    """
    Called once per patient utterance (after STT produces text).

    checkpointer: the SAME instance for every turn of every call —
    create this once when the app/Twilio handler starts up (e.g. on
    app.state), not per turn. This is what makes conversation memory
    persist across turns; call_sid as thread_id only works if the
    checkpointer instance backing it is consistent across calls.

    session_factory: opens a fresh AsyncSession per turn — AsyncSession
    isn't safe for concurrent/reused access across calls or turns.
    """

    async with session_factory() as session:
        appointment_service = AppointmentService(session)
        patient_service = PatientService(session)
        graph = build_agent(appointment_service, patient_service, checkpointer)

        config = {
            "configurable": {"thread_id": call_sid},
            "recursion_limit": 15,
        }

        existing_state = await graph.aget_state(config)
        if not existing_state.values:
            await graph.aupdate_state(
                config, initial_state(call_sid, caller_phone_number)
            )

        try:
            result = await graph.ainvoke(
                {"messages": [HumanMessage(content=patient_utterance)]},
                config=config,
            )
        except GraphRecursionError:
            logger.warning("handle_turn: recursion limit hit for call_sid=%s", call_sid)
            return "I'm having trouble processing that — let me connect you with a staff member."

        last_message = result["messages"][-1]
        return last_message.content