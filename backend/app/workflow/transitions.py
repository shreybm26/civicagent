"""Legal transitions for the CivicAgent deterministic state machine."""

from __future__ import annotations

from collections.abc import Mapping

from ..contracts import State
from .states import Event, TransitionError

TRANSITIONS: Mapping[State, Mapping[Event, State]] = {
    "IDLE": {"citizen_message": "IDENTIFYING"},
    "IDENTIFYING": {
        "service_identified": "COLLECTING",
        "unrecognized_intent": "IDLE",
    },
    "COLLECTING": {
        "location_requested": "LOCATION_REQUIRED",
        "image_uploaded": "MEDIA_ANALYSIS",
        "all_required_present": "VALIDATING",
        "citizen_edits": "COLLECTING",
    },
    "LOCATION_REQUIRED": {
        "location_resolved": "COLLECTING",
        "location_failed": "LOCATION_REQUIRED",
        "image_uploaded": "MEDIA_ANALYSIS",
    },
    "MEDIA_ANALYSIS": {
        "media_analyzed": "COLLECTING",
    },
    "VALIDATING": {
        "validation_failed": "COLLECTING",
        "validation_passed": "REVIEWING",
    },
    "REVIEWING": {
        "citizen_edits": "COLLECTING",
        "citizen_confirms": "SUBMITTING",
    },
    "SUBMITTING": {
        "backend_error": "SUBMISSION_FAILED",
        "receipt": "COMPLETED",
    },
    "SUBMISSION_FAILED": {"retry_review": "REVIEWING"},
    "COMPLETED": {"citizen_message": "IDENTIFYING"},
}


def transition(current: State, event: Event) -> State:
    try:
        return TRANSITIONS[current][event]
    except KeyError as exc:
        raise TransitionError(f"Illegal workflow transition: {current} + {event}") from exc
