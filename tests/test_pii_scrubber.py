"""
Unit tests for PIIScrubber. These are pure regex tests — no LLM
calls, no network, should run in milliseconds. For the integrated
behavior (scrubbing wired into GuardrailService.generate), see
test_guardrails.py instead.

Run with:
    pytest tests/test_pii_scrubber.py -v
"""

from src.guardrails.pii_guardrail import PIIScrubber


def test_ssn_is_always_redacted():
    scrubber = PIIScrubber()
    result = scrubber.redact("The patient's SSN is 123-45-6789.")
    assert "[REDACTED_SSN]" in result.text
    assert "123-45-6789" not in result.text
    assert "SSN" in result.redacted_types


def test_credit_card_is_always_redacted():
    scrubber = PIIScrubber()
    result = scrubber.redact("Card number: 4111 1111 1111 1111")
    assert "[REDACTED_CARD]" in result.text
    assert "4111 1111 1111 1111" not in result.text
    assert "CREDIT_CARD" in result.redacted_types


def test_non_allowlisted_phone_is_redacted():
    scrubber = PIIScrubber(allowlisted_phones=["18005551234"])
    result = scrubber.redact("Contact them at 555-987-6543.")
    assert "[REDACTED_PHONE]" in result.text
    assert "555-987-6543" not in result.text
    assert "PHONE" in result.redacted_types


def test_allowlisted_hospital_phone_is_not_redacted():
    scrubber = PIIScrubber(allowlisted_phones=["18005551234"])
    result = scrubber.redact("Call our front desk at 1-800-555-1234.")
    assert "1-800-555-1234" in result.text
    assert "PHONE" not in result.redacted_types


def test_non_allowlisted_email_is_redacted():
    scrubber = PIIScrubber(allowlisted_emails=["info@hospital.com"])
    result = scrubber.redact("Reach them at someoneelse@example.com.")
    assert "[REDACTED_EMAIL]" in result.text
    assert "someoneelse@example.com" not in result.text


def test_allowlisted_hospital_email_is_not_redacted():
    scrubber = PIIScrubber(allowlisted_emails=["info@hospital.com"])
    result = scrubber.redact("Email us at info@hospital.com.")
    assert "info@hospital.com" in result.text
    assert "EMAIL" not in result.redacted_types


def test_appointment_dates_are_never_touched():
    """
    Regression test: dates must pass through untouched, since the bot's
    core job includes saying appointment dates. This is a deliberate
    design decision, not an oversight — see the module docstring in
    pii_scrubber.py for why dates aren't scrubbed.
    """
    scrubber = PIIScrubber()
    text = "Your appointment with Dr. Patel is on 2026-08-17 at 10:00 AM."
    result = scrubber.redact(text)
    assert result.text == text
    assert not result.had_redactions


def test_clean_response_has_no_redactions():
    scrubber = PIIScrubber()
    text = "I can help you book an appointment with a cardiologist."
    result = scrubber.redact(text)
    assert result.text == text
    assert not result.had_redactions


def test_multiple_pii_types_in_one_response():
    scrubber = PIIScrubber()
    text = "SSN 123-45-6789, card 4111111111111111, email test@example.com"
    result = scrubber.redact(text)
    assert "[REDACTED_SSN]" in result.text
    assert "[REDACTED_CARD]" in result.text
    assert "[REDACTED_EMAIL]" in result.text
    assert set(result.redacted_types) == {"SSN", "CREDIT_CARD", "EMAIL"}