from __future__ import annotations

from src.agent.context.context_models import AgentContext


# ==============================================================
# Shared helpers
# ==============================================================

def _format_conversation_history(context: AgentContext) -> str:
    """
    Renders recent turns as clean "role: content" lines instead of raw
    message reprs. str(HumanMessage(...)) includes additional_kwargs,
    response_metadata, and an id -- none of which should be spent as
    tokens in every single turn's context.
    """

    if not context.conversation_history:
        return ""

    lines = []

    for message in context.conversation_history:

        role = getattr(message, "type", None) or message.__class__.__name__
        content = getattr(message, "content", str(message))

        lines.append(f"{role}: {content}")

    return "RECENT CONVERSATION:\n" + "\n".join(lines)


def _format_current_task(context: AgentContext) -> str:
    """
    Consistent None-guarding: omit the block entirely rather than ever
    render "CURRENT TASK:\nNone" into the prompt.
    """

    if not context.current_task:
        return ""

    return f"CURRENT TASK:\n{context.current_task}"


def _format_user_message(context: AgentContext) -> str:
    return f"CURRENT USER MESSAGE:\n{context.user_message}"


def _join(*parts: str) -> str:
    return "\n\n".join(part for part in parts if part)


# ==============================================================
# Task-specific builders
# ==============================================================

def build_hospital_policy_context(context: AgentContext) -> str:

    retrieved_block = (
        f"RELEVANT HOSPITAL POLICY:\n{context.retrieved_context}"
        if context.retrieved_context
        else ""
    )

    return _join(
        _format_current_task(context),
        _format_conversation_history(context),
        retrieved_block,
        _format_user_message(context),
    )


def build_appointment_context(context: AgentContext) -> str:

    parts = [
        _format_current_task(context),
        _format_conversation_history(context),
    ]

    if context.specialization:
        parts.append(f"SPECIALIZATION:\n{context.specialization}")

    if context.date_from:
        parts.append(f"PREFERRED DATE:\n{context.date_from}")

    if context.selected_slot_id:
        parts.append(f"SELECTED SLOT:\n{context.selected_slot_id}")

    if context.slot_confirmed:
        parts.append("SLOT STATUS:\nThe patient confirmed the selected slot.")

    parts.append(_format_user_message(context))

    return _join(*parts)


def build_cancellation_context(context: AgentContext) -> str:

    parts = [
        _format_current_task(context),
        _format_conversation_history(context),
        f"PATIENT VERIFIED:\n{context.patient_verified}",
        f"VERIFICATION ATTEMPTS:\n{context.verification_attempts}",
    ]

    if context.selected_slot_id:
        parts.append(f"SELECTED APPOINTMENT:\n{context.selected_slot_id}")

    parts.append(_format_user_message(context))

    return _join(*parts)


def build_general_context(context: AgentContext) -> str:

    return _join(
        _format_current_task(context),
        _format_conversation_history(context),
        _format_user_message(context),
    )


# ==============================================================
# Dispatcher
#
# This is the function agent_graph.py actually imports. It was missing
# entirely before, which would raise ImportError at startup.
# ==============================================================

_TASK_BUILDERS = {
    "hospital_policy": build_hospital_policy_context,
    "appointment": build_appointment_context,
    "cancellation": build_cancellation_context,
}


def build_task_context(context: AgentContext) -> str:
    """
    Routes to the correct task-specific builder based on
    context.current_task. Falls back to build_general_context for an
    unrecognized or missing task, so an unknown intent value never
    raises a KeyError.
    """

    builder = _TASK_BUILDERS.get(context.current_task, build_general_context)

    return builder(context)