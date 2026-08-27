"""HTTP adapters for the deterministic CivicAgent workflow."""

from __future__ import annotations

import logging
from pathlib import PurePath
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from .config import Settings
from .contracts import CivicError, ConfirmIn, FieldEditIn, LocationIn, Message, MessageIn, SessionView
from .provider_stub import ConversationProvider
from .store import SessionNotFound, SessionStore
from .workflow.graph import WorkflowGraph
from .workflow.states import WorkflowError

logger = logging.getLogger("civicagent.workflow")


def build_api_router(
    *,
    store: SessionStore,
    provider: ConversationProvider,
    settings: Settings,
    graph: WorkflowGraph,
) -> APIRouter:
    """Create route adapters around the shared store and workflow ports."""

    # Preserve the provider injection seam for Shrey's router/collector adapter.
    _ = provider
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "provider": settings.provider_mode, "schemas": settings.schema_count}

    @router.post("/api/session", response_model=SessionView, status_code=status.HTTP_200_OK)
    def create_session() -> SessionView:
        return graph.view(store.create())

    @router.post("/api/session/{session_id}/reset", response_model=SessionView)
    def reset_session(session_id: UUID) -> SessionView:
        try:
            state = store.reset(session_id)
        except SessionNotFound:
            raise _not_found() from None
        _log_event(state, "reset")
        return graph.view(state)

    @router.post("/api/session/{session_id}/message", response_model=SessionView)
    def message(session_id: UUID, body: MessageIn) -> SessionView:
        try:
            result = graph.handle_message(_get_state(store, session_id), body.message)
        except WorkflowError as exc:
            raise _workflow_error(exc) from exc
        return _persist_result(store, graph, result)

    @router.post("/api/session/{session_id}/location/resolve", response_model=SessionView)
    def resolve_session_location(session_id: UUID, body: LocationIn) -> SessionView:
        try:
            result = graph.resolve_location(_get_state(store, session_id), body.text)
        except WorkflowError as exc:
            raise _workflow_error(exc) from exc
        return _persist_result(store, graph, result)

    @router.post("/api/session/{session_id}/media", response_model=SessionView)
    def analyze_session_media(session_id: UUID, media: UploadFile = File(...)) -> SessionView:
        state = _get_state(store, session_id)
        filename = PurePath(media.filename or "upload").name
        content_type = (media.content_type or "").lower()
        if content_type not in {"image/jpeg", "image/png"}:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=_error("UNSUPPORTED_MEDIA", "Upload a JPEG or PNG image.", False),
            )
        content = media.file.read(settings.max_upload_bytes + 1)
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=_error("MEDIA_TOO_LARGE", "That image is too large for this demo.", False),
            )
        try:
            result = graph.analyze_media(
                state,
                filename=filename,
                content_type=content_type,
                content=content,
            )
        except WorkflowError as exc:
            raise _workflow_error(exc) from exc
        return _persist_result(store, graph, result)

    @router.patch("/api/session/{session_id}/fields/{field_id}", response_model=SessionView)
    def edit_session_field(session_id: UUID, field_id: str, body: FieldEditIn) -> SessionView:
        try:
            result = graph.edit_field(_get_state(store, session_id), field_id, body.value)
        except WorkflowError as exc:
            raise _workflow_error(exc) from exc
        return _persist_result(store, graph, result)

    @router.post("/api/session/{session_id}/confirm", response_model=SessionView)
    def confirm_session(session_id: UUID, body: ConfirmIn) -> SessionView:
        try:
            result = graph.confirm(_get_state(store, session_id), confirmed=body.confirmed)
        except WorkflowError as exc:
            raise _workflow_error(exc) from exc
        return _persist_result(store, graph, result)

    return router


def _persist_result(store: SessionStore, graph: WorkflowGraph, result) -> SessionView:
    _append_agent_turn(result.state, result.message)
    saved = store.save(result.state)
    _log_event(saved, result.event)
    return graph.view(saved, message=result.message)


def _append_agent_turn(state, text: str | None) -> None:
    """Keep agent replies in the transcript so the UI can render a conversation."""

    if not text:
        return
    last = state.messages[-1] if state.messages else None
    if last is not None and last.role == "agent" and last.text == text:
        return
    state.messages.append(Message(role="agent", text=text))


def _get_state(store: SessionStore, session_id: UUID):
    try:
        return store.get(session_id)
    except SessionNotFound:
        raise _not_found() from None


def _log_event(state, event: str) -> None:
    logger.info(
        "workflow_event",
        extra={"civic_event": {"session_id": str(state.session_id), "state": state.state, "event": event}},
    )


def _error(code: str, message: str, retryable: bool) -> dict[str, object]:
    return CivicError(code=code, message=message, retryable=retryable).model_dump(mode="json")


def _workflow_error(error: WorkflowError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=_error("WORKFLOW_INPUT", str(error), False),
    )


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=_error("SESSION_NOT_FOUND", "Session not found.", False),
    )
