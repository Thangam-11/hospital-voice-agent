CONTEXT_POLICY = {

    "hospital_policy": [
        "conversation_history",
        "current_task",
        "retrieved_context",
    ],

    "appointment": [
        "conversation_history",
        "current_task",
        "specialization",
        "date_from",
        "selected_slot_id",
        "slot_confirmed",
    ],

    "cancellation": [
        "conversation_history",
        "current_task",
        "patient_verified",
        "verification_attempts",
        "selected_slot_id",
    ],

    "status": [
        "conversation_history",
        "current_task",
        "patient_verified",
    ],

    "general": [
        "conversation_history",
        "current_task",
    ],
}