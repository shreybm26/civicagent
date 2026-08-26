"""Workflow event/result types and state helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from ..contracts import SessionState, State

Event = Literal[
    "citizen_message",
    "service_identified",
    "unrecognized_intent",
    "location_requested",
    "location_resolved",
    "location_failed",
    "image_uploaded",
    "media_analyzed",
    "all_required_present",
    "validation_failed",
    "validation_passed",
    "citizen_edits",
    "citizen_confirms",
    "backend_error",
    "receipt",
    "retry_review",
]


@dataclass(frozen=True)
class WorkflowResult:
    state: SessionState
    message: str
    event: Event
    changed_fields: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class WorkflowError(RuntimeError):
    """Base workflow exception safe to map at the HTTP boundary."""


class TransitionError(WorkflowError):
    """Raised when a caller attempts an illegal state transition."""


class WorkflowInputError(WorkflowError):
    """Raised for deterministic input/schema violations."""


StateName = State
