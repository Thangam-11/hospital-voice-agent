from src.agent.context.context_policy import (
    CONTEXT_POLICY,
)


def test_hospital_policy_policy():

    fields = CONTEXT_POLICY["hospital_policy"]

    assert "conversation_history" in fields

    assert "current_task" in fields

    assert "retrieved_context" in fields


def test_appointment_policy():

    fields = CONTEXT_POLICY["appointment"]

    assert "specialization" in fields

    assert "date_from" in fields

    assert "selected_slot_id" in fields


def test_cancellation_policy():

    fields = CONTEXT_POLICY["cancellation"]

    assert "patient_verified" in fields

    assert "verification_attempts" in fields