# src/agent/state.py

from typing import Annotated, Optional
from uuid import UUID

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state for the voice agent graph.

    total=False -> every key is optional, since state builds up
    incrementally as tools run across turns of the call.
    """

    # ----------------------------------------------------------------
    # Conversation
    # ----------------------------------------------------------------
    messages: Annotated[list[AnyMessage], add_messages]

    # ----------------------------------------------------------------
    # Call / session metadata
    # ----------------------------------------------------------------
    call_sid: str
    caller_phone_number: Optional[str]

    # ----------------------------------------------------------------
    # Patient verification
    # ----------------------------------------------------------------
    patient_id: Optional[UUID]
    verification_attempts: int

    # ----------------------------------------------------------------
    # Appointment flow
    # ----------------------------------------------------------------
    intent: Optional[str]
    specialization: Optional[str]
    date_from: Optional[str]

    selected_slot_id: Optional[UUID]
    slot_confirmed: bool

    appointment_id: Optional[UUID]

    # Cancellation confirmation is tracked separately from appointment_id,
    # which book_appointment also writes to (the ID of a just-booked
    # appointment). Reusing the same key for "pending cancellation target"
    # would let one silently overwrite the other mid-conversation.
    confirmed_cancellation_id: Optional[UUID]
    cancellation_confirmed: bool  # was Optional[UUID] — this is a flag, not an ID


def initial_state(call_sid: str, caller_phone_number: Optional[str] = None) -> AgentState:
    """
    Build a fresh state dict at the start of a call.
    Use this rather than hand-rolling the dict at the FastAPI layer,
    so new keys added here don't get missed at the call site.
    """

    return AgentState(
        messages=[],
        call_sid=call_sid,
        caller_phone_number=caller_phone_number,
        patient_id=None,
        verification_attempts=0,
        intent=None,
        specialization=None,
        date_from=None,
        selected_slot_id=None,
        slot_confirmed=False,
        appointment_id=None,
        confirmed_cancellation_id=None,
        cancellation_confirmed=False,
    )