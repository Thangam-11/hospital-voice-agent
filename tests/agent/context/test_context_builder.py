from src.agent.context.context_models import AgentContext
from src.agent.context.context_builder import build_task_context


def test_hospital_policy_context():

    context = AgentContext(
        user_message="What are the visiting hours?",

        current_task="hospital_policy",

        conversation_history=[],

        retrieved_context=(
            "General visiting hours are from 9 AM to 6 PM."
        ),
    )


    result = build_task_context(context)

    assert "hospital_policy" in result

    assert "visiting hours" in result

    assert "9 AM to 6 PM" in result

    assert "CURRENT USER MESSAGE" in result

def test_appointment_context():

    context = AgentContext(
        user_message=(
            "I want a cardiology appointment tomorrow."
        ),

        current_task="appointment",

        specialization="Cardiology",

        date_from="2026-09-01",

        conversation_history=[],
    )

    result = build_task_context(context)

    assert "appointment" in result

    assert "Cardiology" in result

    assert "2026-09-01" in result

    assert "CURRENT USER MESSAGE" in result

def test_cancellation_context():

    context = AgentContext(
        user_message="I want to cancel my appointment.",

        current_task="cancellation",

        patient_verified=False,

        verification_attempts=0,

        conversation_history=[],
    )

    result = build_task_context(context)

    assert "cancellation" in result

    assert "False" in result

    assert "VERIFICATION ATTEMPTS" in result

    assert "CURRENT USER MESSAGE" in result