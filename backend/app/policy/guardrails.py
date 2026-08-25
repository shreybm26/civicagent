"""Deterministic safety checks; these never delegate decisions to an LLM."""

from __future__ import annotations

import re
from collections.abc import Iterable

from ..contracts import SessionState
from ..workflow.schema import ServiceSchema

PROMPT_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all instructions",
    "bypass confirmation",
    "submit the form now",
    "auto-submit",
)
UNSUPPORTED_POLICY_PATTERNS = (
    "am i eligible",
    "is this legal",
    "what are my rights",
    "guarantee a response",
    "when will the government",
)
PII_PATTERNS = (
    re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b"),
    re.compile(r"\b(?:\+?\d[\d .()-]{7,}\d)\b"),
)


def is_prompt_injection(text: str) -> bool:
    lowered = text.casefold()
    return any(pattern in lowered for pattern in PROMPT_INJECTION_PATTERNS)


def is_unsupported_policy_request(text: str) -> bool:
    lowered = text.casefold()
    return any(pattern in lowered for pattern in UNSUPPORTED_POLICY_PATTERNS)


def contains_pii(text: str) -> bool:
    return any(pattern.search(text) for pattern in PII_PATTERNS)


def safe_citizen_message(text: str) -> str:
    """Return a user-facing boundary message for unsafe/unsupported requests."""

    if is_prompt_injection(text):
        return "I can collect and submit a civic report only after the required review and your explicit confirmation."
    if is_unsupported_policy_request(text):
        return "I can help collect a civic issue report, but I cannot provide legal, eligibility, or guaranteed-response advice."
    return "I can help collect a civic issue report using the supported service types."


def validate_schema_authority(schema: ServiceSchema, known_departments: Iterable[str] | None = None) -> None:
    """Reject a schema that could fabricate a department or required field."""

    if known_departments is not None and schema.department not in set(known_departments):
        raise ValueError("Schema department is not in the approved registry")
    field_ids = [field.id for field in schema.fields]
    if len(field_ids) != len(set(field_ids)):
        raise ValueError("Schema contains duplicate field IDs")
    if not any(field.required for field in schema.fields):
        raise ValueError("Schema must declare at least one required field")


def redacted_event(session: SessionState, event: str) -> dict[str, str]:
    """Structured log payload containing no citizen content or media."""

    return {
        "session_id": str(session.session_id),
        "state": session.state,
        "event": event,
    }
