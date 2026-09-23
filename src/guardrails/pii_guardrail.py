"""
Deterministic PII scrubber for AI-generated output.

This runs on the BOT'S RESPONSE only, never on the user's input —
scrubbing input would break legitimate flows (a patient giving their
own phone number to look up a booking is normal and required).

Scope, by design:
- SSNs and credit card numbers: always redacted. A hospital assistant
  has no legitimate reason to ever say either, so this has virtually
  no false-positive risk.
- Phone numbers / emails: redacted UNLESS they match an allowlist of
  the hospital's own official contact info. This lets the bot say
  "call our front desk at 555-0100" while still catching some other
  number/email that leaked into its context (e.g. from a different
  patient's record).
- Dates are intentionally NOT scrubbed. There's no reliable way to
  distinguish "date of birth" from "appointment date" by pattern
  alone, and blocking all dates would break the bot's core job of
  confirming appointment times. This risk is instead mitigated by
  scoping the AI's data access correctly (it should never fetch
  another patient's DOB to begin with) and by the self_check_output
  guardrail's judgment-based review.
"""

import re
from dataclasses import dataclass, field


SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

# Simple 13-16 digit sequence, optionally grouped by spaces/dashes.
# Good enough to catch obviously-formatted card numbers; not a full
# Luhn-checksum validator, which would be the next upgrade.
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,16}\b")

PHONE_PATTERN = re.compile(
    r"(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)

EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


@dataclass
class ScrubResult:
    text: str
    redacted_types: list[str] = field(default_factory=list)

    @property
    def had_redactions(self) -> bool:
        return len(self.redacted_types) > 0


class PIIScrubber:
    def __init__(
        self,
        allowlisted_phones: list[str] | None = None,
        allowlisted_emails: list[str] | None = None,
    ):
        # Normalize allowlisted numbers to digits-only for comparison,
        # since phone formatting varies (dashes, spaces, parens).
        self.allowlisted_phones = {
            re.sub(r"\D", "", p) for p in (allowlisted_phones or [])
        }
        self.allowlisted_emails = {
            e.lower() for e in (allowlisted_emails or [])
        }

    def _is_allowlisted_phone(self, match_text: str) -> bool:
        digits = re.sub(r"\D", "", match_text)
        return digits in self.allowlisted_phones

    def _is_allowlisted_email(self, match_text: str) -> bool:
        return match_text.lower() in self.allowlisted_emails

    def redact(self, text: str) -> ScrubResult:
        redacted_types: list[str] = []
        result = text

        if SSN_PATTERN.search(result):
            redacted_types.append("SSN")
            result = SSN_PATTERN.sub("[REDACTED_SSN]", result)

        if CREDIT_CARD_PATTERN.search(result):
            redacted_types.append("CREDIT_CARD")
            result = CREDIT_CARD_PATTERN.sub("[REDACTED_CARD]", result)

        def _phone_sub(m: re.Match) -> str:
            if self._is_allowlisted_phone(m.group(0)):
                return m.group(0)
            if "PHONE" not in redacted_types:
                redacted_types.append("PHONE")
            return "[REDACTED_PHONE]"

        result = PHONE_PATTERN.sub(_phone_sub, result)

        def _email_sub(m: re.Match) -> str:
            if self._is_allowlisted_email(m.group(0)):
                return m.group(0)
            if "EMAIL" not in redacted_types:
                redacted_types.append("EMAIL")
            return "[REDACTED_EMAIL]"

        result = EMAIL_PATTERN.sub(_email_sub, result)

        return ScrubResult(text=result, redacted_types=redacted_types)