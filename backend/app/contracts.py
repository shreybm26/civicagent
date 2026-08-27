"""Typed contracts shared by the CivicAgent backend and frontend.

Phase 1 keeps these models independent of the schema registry and workflow
implementation so both feature branches can build against the same shapes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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

TicketStatus = Literal["pending", "in_progress", "completed"]

TICKET_STATUS_LABELS: dict[TicketStatus, str] = {
    "pending": "Pending",
    "in_progress": "In Progress",
    "completed": "Completed",
}


def normalize_ticket_status(value: str) -> TicketStatus:
    """Map stored status strings to the canonical three-state lifecycle."""

    normalized = value.strip().lower().replace(" ", "_")
    if normalized in ("pending", "received"):
        return "pending"
    if normalized in ("in_progress", "inprogress"):
        return "in_progress"
    if normalized == "completed":
        return "completed"
    return "pending"


def ticket_status_label(status: str) -> str:
    return TICKET_STATUS_LABELS.get(normalize_ticket_status(status), "Pending")


class ContractModel(BaseModel):
    """Base model that rejects accidental contract drift."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Message(ContractModel):
    role: MessageRole
    text: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    media_id: str | None = None


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
    relevance_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    summary: str | None = None
    details: list["ImageDetail"] = Field(default_factory=list)
    candidates: list[Candidate] = Field(default_factory=list)


class ImageDetail(ContractModel):
    label: str = Field(min_length=1)
    value: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str | None = None


class LocationResult(ContractModel):
    query: str = Field(min_length=1)
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: Literal["curated_location", "citizen", "geocoded"] | None = None
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
    access_key: str | None = None


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
    content_type: str = "image/jpeg"
    size_bytes: int = Field(default=1, ge=1)
    summary: str | None = None
    relevance_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    details: list[ImageDetail] = Field(default_factory=list)
    candidates: list[Candidate] = Field(default_factory=list)


class Location(ContractModel):
    query: str = Field(min_length=1)
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: Literal["curated_location", "citizen", "geocoded"] | None = None


class SessionState(ContractModel):
    session_id: UUID
    state: State = "IDLE"
    service_id: ServiceId | None = None
    schema_version: str = "1.0"
    messages: list[Message] = Field(default_factory=list)
    fields: list[FieldValue] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    image_decision: Literal["pending", "added", "skipped"] = "pending"
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
    text: str | None = Field(default=None, max_length=1000)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    label: str | None = Field(default=None, max_length=1000)

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("label")
    @classmethod
    def normalize_label(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None

    @model_validator(mode="after")
    def require_location_input(self):
        if not self.text and (self.lat is None or self.lng is None) and not self.label:
            raise ValueError("provide location text, label, or both coordinates")
        if (self.lat is None) != (self.lng is None):
            raise ValueError("provide both latitude and longitude")
        return self


class MediaDecisionIn(ContractModel):
    has_image: bool


class FieldEditIn(ContractModel):
    value: Any


class ConfirmIn(ContractModel):
    confirmed: bool


class TrackIn(ContractModel):
    sr_id: str = Field(min_length=3, max_length=64)
    access_key: str = Field(min_length=8, max_length=64)

    @field_validator("sr_id")
    @classmethod
    def normalize_sr_id(cls, value: str) -> str:
        value = " ".join(value.strip().upper().split())
        if not value:
            raise ValueError("service request id cannot be empty")
        return value

    @field_validator("access_key")
    @classmethod
    def normalize_access_key(cls, value: str) -> str:
        value = value.strip().upper().replace(" ", "")
        if not value:
            raise ValueError("access key cannot be empty")
        return value


class TrackingField(ContractModel):
    id: str = Field(min_length=1)
    value: Any = None


class TimelineStep(ContractModel):
    id: str
    title: str
    detail: str
    at: datetime | None = None
    done: bool = False


class NearbyReport(ContractModel):
    service_id: str
    label: str
    distance_km: float
    status: str
    source: Literal["filed", "demonstration"]
    count: int = 1


class TypeCount(ContractModel):
    service_id: str
    label: str
    count: int


class TrackingView(ContractModel):
    sr_id: str
    status: str
    status_key: TicketStatus = "pending"
    department: str | None = None
    service_id: str | None = None
    submitted_at: datetime
    location: str | None = None
    fields: list[TrackingField] = Field(default_factory=list)
    timeline: list[TimelineStep] = Field(default_factory=list)
    nearby: list[NearbyReport] = Field(default_factory=list)
    type_counts: list[TypeCount] = Field(default_factory=list)
    neighbourhood_note: str = (
        "Demonstration neighbourhood picture. Counts mix synthetic nearby samples with other tickets filed in this demo. Not live municipal data."
    )


class TrackEmailIn(TrackIn):
    email: str = Field(min_length=5, max_length=254)
    confirm_send: bool = False

    @field_validator("email")
    @classmethod
    def normalize_email_field(cls, value: str) -> str:
        return value.strip()


class EmailSentView(ContractModel):
    sent: bool
    to: str


class DemoStatusIn(ContractModel):
    status: TicketStatus


class DepartmentStats(ContractModel):
    department: str
    total: int
    pending: int
    in_progress: int
    completed: int


class WardStats(ContractModel):
    ward_id: str
    ward_name: str
    total: int
    pending: int
    in_progress: int
    completed: int
    open_ratio: float = Field(ge=0.0, le=1.0)


class DashboardSummary(ContractModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    last_updated: datetime
    departments: list[DepartmentStats]
    wards: list[WardStats]


class PublicTicketRow(ContractModel):
    ref_masked: str
    service_id: ServiceId
    service_label: str
    ward_name: str
    department: str
    status: TicketStatus
    reported_at: datetime


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
