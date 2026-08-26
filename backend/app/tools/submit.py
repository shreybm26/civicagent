"""Validation and confirmation-gated submission tool."""

from __future__ import annotations

from ..contracts import Receipt, SessionState
from ..mock_backend.civic_api import MockBackendError, MockCivicBackend
from ..workflow.schema import ServiceSchema, field_value_is_valid


class SubmissionError(RuntimeError):
    """Submission precondition or backend failure."""

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


def validate_for_submission(state: SessionState, schema: ServiceSchema) -> tuple[bool, list[str]]:
    fields = {field.id: field for field in state.fields}
    missing: list[str] = []
    for spec in schema.required_fields:
        field = fields.get(spec.id)
        if field is None or not field_value_is_valid(spec, field.value):
            missing.append(spec.id)
    return not missing, missing


def submit_state(
    state: SessionState,
    schema: ServiceSchema,
    backend: MockCivicBackend,
    *,
    confirmed: bool,
) -> Receipt:
    if not confirmed or not state.confirmation.confirmed:
        raise SubmissionError("Submission requires explicit confirmation.")
    if state.state != "SUBMITTING":
        raise SubmissionError("Submission must be in the SUBMITTING state.")
    valid, missing = validate_for_submission(state, schema)
    if not valid:
        raise SubmissionError(f"Complete required fields before submitting: {', '.join(missing)}")

    payload = {
        "service_id": schema.service_id,
        "schema_version": schema.schema_version,
        "fields": [field.model_dump(mode="json") for field in state.fields],
        "evidence": [evidence.model_dump(mode="json") for evidence in state.evidence],
        "location": state.location.model_dump(mode="json") if state.location else None,
    }
    try:
        return backend.submit(
            session_id=state.session_id,
            service_id=schema.service_id,
            department=schema.department,
            payload=payload,
            id_prefix=schema.id_prefix,
        )
    except MockBackendError as exc:
        raise SubmissionError(str(exc), retryable=True) from exc
