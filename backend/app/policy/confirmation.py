"""Explicit confirmation gate for the only irreversible workflow action."""

from __future__ import annotations

from datetime import datetime, timezone

from ..contracts import SessionState


def can_confirm(state: SessionState, confirmed: bool) -> tuple[bool, str | None]:
    if not confirmed:
        return False, "Submission requires explicit confirmation."
    if state.state != "REVIEWING":
        return False, "Complete the review before submitting."
    if not state.validation.valid:
        return False, "Complete all required fields before submitting."
    return True, None


def apply_confirmation(state: SessionState) -> SessionState:
    next_state = state.model_copy(deep=True)
    next_state.confirmation.confirmed = True
    next_state.confirmation.confirmed_at = datetime.now(timezone.utc)
    return next_state
