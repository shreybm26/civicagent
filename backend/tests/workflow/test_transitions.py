import pytest

from app.workflow.states import TransitionError
from app.workflow.transitions import transition


def test_primary_and_failure_transitions_are_explicit() -> None:
    assert transition("IDLE", "citizen_message") == "IDENTIFYING"
    assert transition("IDENTIFYING", "service_identified") == "COLLECTING"
    assert transition("COLLECTING", "all_required_present") == "VALIDATING"
    assert transition("VALIDATING", "validation_passed") == "REVIEWING"
    assert transition("REVIEWING", "citizen_confirms") == "SUBMITTING"
    assert transition("SUBMITTING", "backend_error") == "SUBMISSION_FAILED"
    assert transition("SUBMISSION_FAILED", "retry_review") == "REVIEWING"
    assert transition("SUBMITTING", "receipt") == "COMPLETED"


def test_illegal_transition_is_rejected() -> None:
    with pytest.raises(TransitionError):
        transition("IDLE", "receipt")
