from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    """
    LLM-facing context.

    This is NOT the complete AgentState.

    It contains only information that is useful
    for the current reasoning task.
    """

    user_message: str

    current_task: str | None = None

    conversation_history: list[Any] = field(
        default_factory=list
    )

    retrieved_context: str = ""

    patient_verified: bool = False

    verification_attempts: int = 0

    specialization: str | None = None

    date_from: str | None = None

    selected_slot_id: str | None = None

    slot_confirmed: bool = False