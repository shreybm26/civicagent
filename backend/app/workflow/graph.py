"""Deterministic CivicAgent workflow graph.

This is intentionally a small StateGraph-compatible engine. It keeps all
transitions explicit while leaving router/collector/image providers as ports
that Shrey can replace without changing the HTTP contract.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..contracts import (
    CivicError,
    Evidence,
    FieldValue,
    Location,
    LocationResult,
    Message,
    ServiceId,
    ServiceSummary,
    SessionState,
    SessionView,
    ValidationResult,
    session_view,
)
from ..mock_backend.civic_api import MockCivicBackend
from ..policy.confirmation import apply_confirmation, can_confirm
from ..policy.guardrails import (
    is_prompt_injection,
    is_unsupported_policy_request,
    redacted_event,
    safe_citizen_message,
    validate_schema_authority,
)
from ..tools.location import resolve_location
from ..tools.submit import SubmissionError, submit_state
from ..integration_adapters import RegistrySchemaAdapter, SchemaRouterAdapter, SchemaCollectorAdapter, ImageAnalyzerAdapter
from .schema import ServiceSchema, field_value_is_valid, mock_service_schemas
from .ports import CollectorPort, ImagePort, MockCollector, MockImageService, MockRouter, RouterPort
from .states import WorkflowError, WorkflowResult
from .transitions import transition


class WorkflowGraph:
    """Own the workflow state and delegate only proposals to provider ports."""

    def __init__(
        self,
        *,
        schemas: Mapping[ServiceId, ServiceSchema] | None = None,
        backend: MockCivicBackend | None = None,
        router: RouterPort | None = None,
        collector: CollectorPort | None = None,
        image_service: ImagePort | None = None,
    ) -> None:
        self.schemas = dict(schemas or RegistrySchemaAdapter().as_graph_schemas())
        if set(self.schemas) != {
            "road_issue",
            "garbage_issue",
            "streetlight_issue",
            "water_issue",
            "sanitation_issue",
        }:
            raise ValueError("CivicAgent requires exactly five known service schemas")
        for schema in self.schemas.values():
            validate_schema_authority(schema)
        self.backend = backend or MockCivicBackend()
        self.router = router or SchemaRouterAdapter(self.schemas)
        self.collector = collector or SchemaCollectorAdapter()
        self.image_service = image_service or ImageAnalyzerAdapter()

    def view(self, state: SessionState, *, message: str | None = None) -> SessionView:
        schema = self.schema_for(state)
        service = (
            ServiceSummary(
                service_id=schema.service_id,
                name=schema.service_name,
                department=schema.department,
            )
            if schema
            else None
        )
        return session_view(state, agent_message=message, service=service)

    def schema_for(self, state: SessionState) -> ServiceSchema | None:
        return self.schemas.get(state.service_id) if state.service_id else None

    def handle_message(self, state: SessionState, text: str) -> WorkflowResult:
        text = text.strip()
        if not text:
            raise WorkflowError("Message cannot be empty")

        if is_prompt_injection(text) or is_unsupported_policy_request(text):
            next_state = state.model_copy(deep=True)
            next_state.messages.append(Message(role="citizen", text=text))
            return WorkflowResult(
                state=next_state,
                message=safe_citizen_message(text),
                event="unrecognized_intent",
                metadata={"redacted_event": redacted_event(state, "guardrail")},
            )

        next_state = state.model_copy(deep=True)
        if next_state.state == "COMPLETED":
            # Keep the anonymous session ID, but start a clean second report.
            next_state = SessionState(session_id=next_state.session_id)

        next_state.messages.append(Message(role="citizen", text=text))

        if next_state.service_id is None:
            return self._identify(next_state, text)

        if next_state.state == "LOCATION_REQUIRED":
            return self._resolve_location(next_state, text)

        return self._collect_text(next_state, text)

    def resolve_location(self, state: SessionState, text: str) -> WorkflowResult:
        if state.service_id is None:
            raise WorkflowError("Identify a service before resolving a location")
        next_state = state.model_copy(deep=True)
        if next_state.state == "COLLECTING":
            next_state.state = transition(next_state.state, "location_requested")
        return self._resolve_location(next_state, text)

    def analyze_media(
        self,
        state: SessionState,
        *,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> WorkflowResult:
        if state.service_id is None:
            raise WorkflowError("Identify a service before uploading evidence")
        if state.state not in {"COLLECTING", "LOCATION_REQUIRED"}:
            raise WorkflowError("Evidence can be uploaded while collecting report details")

        next_state = state.model_copy(deep=True)
        next_state.state = transition(next_state.state, "image_uploaded")
        result = self.image_service.analyze(
            schema=self.schemas[state.service_id],
            filename=filename,
            content_type=content_type,
            content=content,
        )
        next_state.state = transition(next_state.state, "media_analyzed")
        media_id = f"media-{len(next_state.evidence) + 1}"
        next_state.evidence.append(
            Evidence(
                media_id=media_id,
                filename=filename,
                relevant=result.relevant,
                reason=result.reason,
                candidates=list(result.candidates),
            )
        )
        changed: list[str] = []
        if result.relevant:
            self._set_field(
                next_state,
                "photo",
                filename,
                source="photo",
                confidence=1.0,
                status="accepted",
                changed=changed,
            )
            for candidate in result.candidates:
                current = self._field(next_state, candidate.field_id)
                if current is None or current.value in (None, ""):
                    self._set_field(
                        next_state,
                        candidate.field_id,
                        candidate.value,
                        source=candidate.source,
                        confidence=candidate.confidence,
                        status="candidate",
                        reason=candidate.reason,
                        changed=changed,
                    )

        result_state, follow_up = self._finish_collection(next_state)
        message = f"{result.reason} {follow_up}" if result.relevant else f"{result.reason} Please upload a relevant civic photo."
        return WorkflowResult(
            state=result_state,
            message=message,
            event="media_analyzed",
            changed_fields=tuple(changed),
            metadata={"relevant": result.relevant, "redacted_event": redacted_event(result_state, "media_analyzed")},
        )

    def edit_field(self, state: SessionState, field_id: str, value: Any) -> WorkflowResult:
        schema = self.schema_for(state)
        if schema is None:
            raise WorkflowError("Identify a service before editing fields")
        field = schema.field(field_id)
        if field is None:
            raise WorkflowError(f"Unknown field: {field_id}")
        if not field_value_is_valid(field, value):
            raise WorkflowError(f"Invalid value for field: {field_id}")

        next_state = state.model_copy(deep=True)
        if next_state.state == "REVIEWING":
            next_state.state = transition(next_state.state, "citizen_edits")
        self._set_field(next_state, field_id, value, source="correction", confidence=1.0, status="accepted")
        if field_id == "location" and isinstance(value, str):
            location = resolve_location(value)
            if location.address:
                self._apply_location(next_state, location)
        next_state.confirmation.confirmed = False
        next_state.confirmation.confirmed_at = None
        result_state, message = self._finish_collection(next_state)
        return WorkflowResult(
            state=result_state,
            message=f"Updated {field_id}. {message}",
            event="citizen_edits",
            changed_fields=(field_id,),
            metadata={"redacted_event": redacted_event(result_state, "citizen_edits")},
        )

    def confirm(self, state: SessionState, *, confirmed: bool) -> WorkflowResult:
        next_state = state.model_copy(deep=True)
        if next_state.state == "SUBMISSION_FAILED":
            next_state.state = transition(next_state.state, "retry_review")
        if next_state.state != "REVIEWING":
            raise WorkflowError("Complete the review before submitting")
        if not confirmed:
            raise WorkflowError("Submission requires explicit confirmation")
        schema = self.schema_for(next_state)
        if schema is None:
            raise WorkflowError("A service schema is required before submission")

        allowed, reason = can_confirm(next_state, confirmed)
        if not allowed:
            raise WorkflowError(reason or "Submission confirmation failed.")
        next_state = apply_confirmation(next_state)
        next_state.state = transition(next_state.state, "citizen_confirms")
        try:
            receipt = submit_state(next_state, schema, self.backend, confirmed=confirmed)
        except SubmissionError as exc:
            next_state.state = transition(next_state.state, "backend_error")
            next_state.error = CivicError(code="SUBMISSION_FAILED", message=str(exc), retryable=exc.retryable)
            return WorkflowResult(
                state=next_state,
                message=str(exc),
                event="backend_error",
                metadata={"retryable": exc.retryable, "redacted_event": redacted_event(next_state, "backend_error")},
            )

        next_state.receipt = receipt
        next_state.error = None
        next_state.state = transition(next_state.state, "receipt")
        return WorkflowResult(
            state=next_state,
            message=f"Complaint submitted successfully. Reference: {receipt.reference}",
            event="receipt",
            metadata={"reference": receipt.reference, "redacted_event": redacted_event(next_state, "receipt")},
        )

    def _identify(self, state: SessionState, text: str) -> WorkflowResult:
        state.state = transition(state.state, "citizen_message")
        proposal = self.router.classify(text, self.schemas)
        if proposal.service_id is None or proposal.needs_clarification:
            state.state = transition(state.state, "unrecognized_intent")
            state.error = None
            return WorkflowResult(
                state=state,
                message="I can currently help with road, garbage, streetlight, water, or sanitation issues. Which issue would you like to report?",
                event="unrecognized_intent",
                metadata={"redacted_event": redacted_event(state, "unrecognized_intent")},
            )

        service_id = proposal.service_id
        schema = self.schemas[service_id]
        state.service_id = service_id
        state.schema_version = schema.schema_version
        state.state = transition(state.state, "service_identified")
        state.fields = [
            FieldValue(id=field.id, required=field.required, status="missing")
            for field in schema.fields
        ]
        self._set_field(
            state,
            "description",
            text,
            source="citizen",
            confidence=1.0,
            status="accepted",
        )
        return WorkflowResult(
            state=state,
            message=f"I can help report this {schema.service_name.lower()}. Where exactly is the issue?",
            event="service_identified",
            changed_fields=("description",),
            metadata={"service_id": service_id, "redacted_event": redacted_event(state, "service_identified")},
        )

    def _collect_text(self, state: SessionState, text: str) -> WorkflowResult:
        schema = self.schema_for(state)
        if schema is None:
            raise WorkflowError("A service schema is required before collecting fields")
        missing = self._missing_required(state, schema)
        if not missing:
            result_state, message = self._finish_collection(state)
            return WorkflowResult(state=result_state, message=message, event="all_required_present")
        field = missing[0]
        if field.id == "location":
            state.state = transition(state.state, "location_requested")
            return self._resolve_location(state, text)

        candidate = self.collector.collect(field, text)
        if candidate is None:
            return WorkflowResult(
                state=state,
                message=self._question_for(field),
                event="citizen_edits",
                metadata={"redacted_event": redacted_event(state, "clarification")},
            )
        changed: list[str] = []
        self._set_field(
            state,
            field.id,
            candidate.value,
            source=candidate.source,
            confidence=candidate.confidence,
            status="accepted",
            changed=changed,
        )
        result_state, message = self._finish_collection(state)
        return WorkflowResult(
            state=result_state,
            message=message,
            event="all_required_present" if result_state.state == "REVIEWING" else "citizen_edits",
            changed_fields=tuple(changed),
            metadata={"redacted_event": redacted_event(result_state, "field_collected")},
        )

    def _resolve_location(self, state: SessionState, text: str) -> WorkflowResult:
        result = resolve_location(text)
        if result.address:
            self._apply_location(state, result)
            state.state = transition(state.state, "location_resolved")
            result_state, follow_up = self._finish_collection(state)
            return WorkflowResult(
                state=result_state,
                message=f"{result.message} {follow_up}",
                event="location_resolved",
                changed_fields=("location",),
                metadata={"redacted_event": redacted_event(result_state, "location_resolved")},
            )
        state.state = "LOCATION_REQUIRED"
        return WorkflowResult(
            state=state,
            message=result.message or "Please provide a nearby landmark or area.",
            event="location_failed",
            metadata={"redacted_event": redacted_event(state, "location_failed")},
        )

    def _finish_collection(self, state: SessionState) -> tuple[SessionState, str]:
        schema = self.schema_for(state)
        if schema is None:
            raise WorkflowError("A service schema is required before validation")
        state.validation = self._validate(state, schema)
        if not state.validation.valid:
            state.state = "COLLECTING"
            missing = state.validation.missing_fields
            field = schema.field(missing[0]) if missing else None
            return state, self._question_for(field) if field else "I still need one more detail."
        if state.state == "COLLECTING":
            state.state = transition(state.state, "all_required_present")
        state.state = transition(state.state, "validation_passed")
        return state, "Please review the details below and confirm submission."

    def _validate(self, state: SessionState, schema: ServiceSchema) -> ValidationResult:
        fields = {field.id: field for field in state.fields}
        missing: list[str] = []
        errors: list[str] = []
        for spec in schema.required_fields:
            current = fields.get(spec.id)
            if current is None or not field_value_is_valid(spec, current.value):
                missing.append(spec.id)
                if current is not None and current.value not in (None, ""):
                    errors.append(f"Invalid value for {spec.id}")
        return ValidationResult(valid=not missing and not errors, missing_fields=missing, errors=errors)

    def _question_for(self, field: Any | None) -> str:
        if field is None:
            return "Please provide the missing detail."
        labels = {
            "location": "Where exactly is the issue?",
            "description": "Please describe the issue.",
            "severity": "How severe is the issue: low, medium, or high?",
            "duration": "How long has this been happening?",
            "leak_type": "What kind of leak is it: pipe, tap, supply, or unknown?",
            "issue_type": "What kind of sanitation issue is it: sewage, drain, public hygiene, or other?",
            "pole_number": "Do you know the streetlight pole number? You can say I don't know.",
            "time_noticed": "When did you first notice the issue?",
        }
        return labels.get(field.id, f"Please provide the {field.id.replace('_', ' ')}.")

    def _missing_required(self, state: SessionState, schema: ServiceSchema) -> list[Any]:
        fields = {field.id: field for field in state.fields}
        return [
            spec
            for spec in schema.required_fields
            if spec.id not in fields or not field_value_is_valid(spec, fields[spec.id].value)
        ]

    def _field(self, state: SessionState, field_id: str) -> FieldValue | None:
        return next((field for field in state.fields if field.id == field_id), None)

    def _set_field(
        self,
        state: SessionState,
        field_id: str,
        value: Any,
        *,
        source: Any,
        confidence: float,
        status: Any,
        reason: str | None = None,
        changed: list[str] | None = None,
    ) -> None:
        field = self._field(state, field_id)
        if field is None:
            return
        field.value = value
        field.source = source
        field.confidence = confidence
        field.status = status
        field.reason = reason
        if changed is not None and field_id not in changed:
            changed.append(field_id)

    def _apply_location(self, state: SessionState, result: LocationResult) -> None:
        state.location = Location(
            query=result.query,
            address=result.address,
            lat=result.lat,
            lng=result.lng,
            confidence=result.confidence,
            source=result.source,
        )
        self._set_field(
            state,
            "location",
            result.address,
            source="location",
            confidence=result.confidence,
            status="accepted",
        )
