from langgraph.errors import GraphRecursionError
from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_core.messages import HumanMessage

from src.agent.agent_core import build_agent
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

    async with session_factory() as session:

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
                        HumanMessage(
                            content=patient_utterance
                        )
                    ]
                },
                config=config,
            )

        except GraphRecursionError:

            logger.warning(
                "handle_turn: recursion limit hit | call_sid=%s",
                call_sid,
            )

            return (
                "I'm having trouble processing that. "
                "Let me connect you with a staff member."
            )

        except Exception:

            logger.exception(
                "handle_turn: LangGraph execution failed | call_sid=%s",
                call_sid,
            )

            raise

        messages = result.get("messages", [])

        if not messages:
            logger.warning(
                "handle_turn: graph returned no messages | call_sid=%s",
                call_sid,
            )

            return (
                "I'm sorry, I couldn't generate a response. "
                "Could you please try again?"
            )

        last_message = messages[-1]

        return str(last_message.content)