from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.contracts import (
    Candidate,
    CivicError,
    MessageIn,
    SessionState,
    State,
    idle_session,
)


def test_idle_session_matches_phase_one_contract() -> None:
    state = idle_session(uuid4())

    assert state.state == "IDLE"
    assert state.service_id is None
    assert state.schema_version == "1.0"
    assert state.fields == []
    assert state.receipt is None
    assert state.confirmation.confirmed is False


def test_contract_rejects_unknown_state_and_extra_fields() -> None:
    with pytest.raises(ValidationError):
        SessionState(session_id=uuid4(), state="idle")

    with pytest.raises(ValidationError):
        SessionState(session_id=uuid4(), unexpected="value")


def test_candidate_confidence_is_bounded() -> None:
    with pytest.raises(ValidationError):
        Candidate(field_id="severity", value="high", source="photo", confidence=1.1)


def test_message_input_strips_whitespace_and_rejects_blank() -> None:
    assert MessageIn(message="  pothole  ").message == "pothole"
    with pytest.raises(ValidationError):
        MessageIn(message="   ")


def test_error_text_is_single_line_and_redacted_by_shape() -> None:
    error = CivicError(code="UPSTREAM", message="  Try again.\nNo details.  ", retryable=True)

    assert error.message == "Try again. No details."
    assert "@" not in error.model_dump_json()
