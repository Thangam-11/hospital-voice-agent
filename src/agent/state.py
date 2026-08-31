# src/agent/state.py

from __future__ import annotations

from typing import Annotated, Optional
from uuid import UUID

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared runtime state for the hospital voice agent.

    The state is shared across LangGraph nodes and contains:

    1. Conversation state
    2. Call/session state
    3. Patient verification state
    4. Appointment workflow state
    5. Cancellation workflow state
    6. Context engineering state
    7. Harness execution state
    8. Guardrail state
    """

    # ==============================================================
    # CONVERSATION
    # ==============================================================

    messages: Annotated[
        list[AnyMessage],
        add_messages,
    ]

    # ==============================================================
    # CALL / SESSION
    # ==============================================================

    call_sid: str

    caller_phone_number: Optional[str]

    # ==============================================================
    # PATIENT VERIFICATION
    # ==============================================================

    patient_id: Optional[UUID]

    verification_attempts: int

    # ==============================================================
    # APPOINTMENT FLOW
    # ==============================================================

    intent: Optional[str]

    specialization: Optional[str]

    date_from: Optional[str]

    selected_slot_id: Optional[UUID]

    slot_confirmed: bool

    appointment_id: Optional[UUID]

    # ==============================================================
    # CANCELLATION FLOW
    # ==============================================================

    confirmed_cancellation_id: Optional[UUID]

    cancellation_confirmed: bool

    # ==============================================================
    # CONTEXT ENGINEERING
    # ==============================================================

    # What task is currently being performed?
    #
    # Examples:
    #   appointment
    #   cancellation
    #   status
    #   hospital_policy
    #   general
    current_task: Optional[str]

    # Context retrieved from the RAG pipeline.
    retrieved_context: Optional[str]

    # Retrieved chunks used to construct the context.
    #
    # Keep this for traceability / observability.
    retrieved_chunks: list[dict]

    # ==============================================================
    # HARNESS / EXECUTION CONTROL
    # ==============================================================

    # Number of tools executed during the current turn.
    tool_call_count: int

    # Name of the most recently executed tool.
    last_tool: Optional[str]

    # ==============================================================
    # GUARDRAILS
    # ==============================================================

    # Examples:
    #
    #   passed
    #   blocked
    #   emergency
    #   medical_advice
    #   prompt_injection
    guardrail_status: Optional[str]


def initial_state(
    call_sid: str,
    caller_phone_number: Optional[str] = None,
) -> AgentState:
    """
    Create the initial runtime state for a new conversation.
    """

    return AgentState(
        # ----------------------------------------------------------
        # Conversation
        # ----------------------------------------------------------

        messages=[],

        # ----------------------------------------------------------
        # Session
        # ----------------------------------------------------------

        call_sid=call_sid,

        caller_phone_number=caller_phone_number,

        # ----------------------------------------------------------
        # Patient
        # ----------------------------------------------------------

        patient_id=None,

        verification_attempts=0,

        # ----------------------------------------------------------
        # Appointment
        # ----------------------------------------------------------

        intent=None,

        specialization=None,

        date_from=None,

        selected_slot_id=None,

        slot_confirmed=False,

        appointment_id=None,

        # ----------------------------------------------------------
        # Cancellation
        # ----------------------------------------------------------

        confirmed_cancellation_id=None,

        cancellation_confirmed=False,

        # ----------------------------------------------------------
        # Context Engineering
        # ----------------------------------------------------------

        current_task=None,

        retrieved_context=None,

        retrieved_chunks=[],

        # ----------------------------------------------------------
        # Harness
        # ----------------------------------------------------------

        tool_call_count=0,

        last_tool=None,

        # ----------------------------------------------------------
        # Guardrails
        # ----------------------------------------------------------

        guardrail_status=None,
    )