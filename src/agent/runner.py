from langgraph.errors import GraphRecursionError
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.agent_core import build_agent
from src.service.appointment_service import AppointmentService
from src.service.patient_service import PatientService
from src.utils.logger_exceptions import get_logger

logger = get_logger(__name__)


async def run_agent(
    session: AsyncSession,
    checkpointer: BaseCheckpointSaver,
    call_sid: str,
    patient_utterance: str,
    caller_phone_number: str | None = None,
) -> str:

    appointment_service = AppointmentService(session)
    patient_service = PatientService(session)

    graph = build_agent(
        appointment_service,
        patient_service,
        checkpointer,
    )

    config = {
        "configurable": {
            "thread_id": call_sid,
        },
        "recursion_limit": 15,
    }

    try:
        result = await graph.ainvoke(
            {
                "messages": [
                    HumanMessage(content=patient_utterance)
                ],
                "call_sid": call_sid,
                "caller_phone_number": caller_phone_number,
            },
            config=config,
        )

    except GraphRecursionError:
        logger.warning(
            "Recursion limit reached | call_sid=%s",
            call_sid,
        )
        return (
            "I'm having trouble processing that. "
            "Let me connect you with a staff member."
        )

    messages = result.get("messages", [])

    if not messages:
        return "I'm sorry, I couldn't generate a response."

    return str(messages[-1].content)


async def handle_turn(
    session_factory,
    checkpointer: BaseCheckpointSaver,
    call_sid: str,
    patient_utterance: str,
    caller_phone_number: str | None = None,
) -> str:

    async with session_factory() as session:

        return await run_agent(
            session=session,
            checkpointer=checkpointer,
            call_sid=call_sid,
            patient_utterance=patient_utterance,
            caller_phone_number=caller_phone_number,
        )