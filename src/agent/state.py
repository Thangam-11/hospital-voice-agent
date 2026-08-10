from typing import Annotated, Optional
from uuid import UUID

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    # Conversation between patient and agent
    messages: Annotated[list[BaseMessage], add_messages]

    # Patient information
    patient_id: Optional[UUID]

    # What the patient wants
    intent: Optional[str]

    # Appointment information
    specialization: Optional[str]
    date_from: Optional[str]
    selected_slot_id: Optional[UUID]

    # Booking result
    appointment_id: Optional[UUID]