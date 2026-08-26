from uuid import uuid4

from app.contracts import SessionState
from app.policy.guardrails import contains_pii, redacted_event


def test_pii_detection_and_redacted_event_shape() -> None:
    state = SessionState(session_id=uuid4())

    assert contains_pii("contact me at citizen@example.com") is True
    assert contains_pii("call +91 98765 43210") is True
    assert contains_pii("pothole near JNTU Metro") is False
    assert redacted_event(state, "receipt") == {
        "session_id": str(state.session_id),
        "state": "IDLE",
        "event": "receipt",
    }
