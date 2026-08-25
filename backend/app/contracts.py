"""Typed contracts shared by the CivicAgent backend and frontend.

Phase 1 keeps these models independent of the schema registry and workflow
implementation so both feature branches can build against the same shapes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

State = Literal[
    "IDLE",
    "IDENTIFYING",
    "COLLECTING",
    "LOCATION_REQUIRED",
    "MEDIA_ANALYSIS",
    "VALIDATING",
    "REVIEWING",
    "SUBMITTING",
    "SUBMISSION_FAILED",
    "COMPLETED",
]

ServiceId = Literal[
    "road_issue",
    "garbage_issue",
    "streetlight_issue",
    "water_issue",
    "sanitation_issue",
]

MessageRole = Literal["citizen", "agent", "system"]
FieldSource = Literal["citizen", "correction", "conversation", "photo", "location", "schema"]
FieldStatus = Literal["missing", "candidate", "accepted", "rejected"]


class ContractModel(BaseModel):
    """Base model that rejects accidental contract drift."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Message(ContractModel):
    role: MessageRole
    text: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FieldValue(ContractModel):
    id: str = Field(min_length=1)
    value: Any = None
    required: bool = False
    source: FieldSource | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    status: FieldStatus = "missing"
    reason: str | None = None


class Candidate(ContractModel):
    field_id: str = Field(min_length=1)
    value: Any = None
    source: Literal["citizen", "correction", "conversation", "photo", "location"]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str | None = None


class RouterResult(ContractModel):
    service_id: ServiceId | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    needs_clarification: bool = True
    message: str = Field(min_length=1)


class ImageResult(ContractModel):
    relevant: bool
    reason: str = Field(min_length=1)
    candidates: list[Candidate] = Field(default_factory=list)


class LocationResult(ContractModel):
    query: str = Field(min_length=1)
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: Literal["curated_location", "citizen"] | None = None
    needs_clarification: bool = False
    message: str | None = None


class ValidationResult(ContractModel):
    valid: bool = False
    missing_fields: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class Confirmation(ContractModel):
    confirmed: bool = False
    confirmed_at: datetime | None = None


class Receipt(ContractModel):
    reference: str = Field(min_length=1)
    status: str = Field(min_length=1)
    department: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CivicError(ContractModel):
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    retryable: bool = False

    @field_validator("message")
    @classmethod
    def reject_line_breaks(cls, value: str) -> str:
        """Keep API error text compact and unsuitable for log injection."""

        return " ".join(value.split())


class ServiceSummary(ContractModel):
    service_id: ServiceId
    name: str = Field(min_length=1)
    department: str = Field(min_length=1)


class Evidence(ContractModel):
    media_id: str = Field(min_length=1)
    filename: str = Field(min_length=1)
    relevant: bool
    reason: str = Field(min_length=1)
    candidates: list[Candidate] = Field(default_factory=list)


class Location(ContractModel):
    query: str = Field(min_length=1)
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: Literal["curated_location", "citizen"] | None = None


class SessionState(ContractModel):
    session_id: UUID
    state: State = "IDLE"
    service_id: ServiceId | None = None
    schema_version: str = "1.0"
    messages: list[Message] = Field(default_factory=list)
    fields: list[FieldValue] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    location: Location | None = None
    validation: ValidationResult = Field(default_factory=ValidationResult)
    confirmation: Confirmation = Field(default_factory=Confirmation)
    receipt: Receipt | None = None
    error: CivicError | None = None


class SessionView(SessionState):
    """API response shape; frontend-only message is never workflow state."""

    agent_message: str | None = None
    service: ServiceSummary | None = None


class MessageIn(ContractModel):
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message cannot be empty")
        return value


class LocationIn(ContractModel):
    text: str = Field(min_length=1, max_length=1000)

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("location text cannot be empty")
        return value


class FieldEditIn(ContractModel):
    value: Any


class ConfirmIn(ContractModel):
    confirmed: bool


def idle_session(session_id: UUID) -> SessionState:
    """Create a clean anonymous session without carrying prior user data."""

    return SessionState(session_id=session_id)


def session_view(
    state: SessionState,
    *,
    agent_message: str | None = None,
    service: ServiceSummary | None = None,
) -> SessionView:
    return SessionView(
        **state.model_dump(),
        agent_message=agent_message,
        service=service,
    )
