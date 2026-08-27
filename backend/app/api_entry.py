"""HTTP adapters for the deterministic CivicAgent workflow."""

from __future__ import annotations

import logging
from pathlib import PurePath
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from .config import Settings
from .contracts import CivicError, ConfirmIn, FieldEditIn, LocationIn, LocationResult, MediaDecisionIn, Message, MessageIn, SessionView
from .media_store import MediaNotFound, MediaStore
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
    media_store: MediaStore,
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
        media_store.delete_session(session_id)
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
            state = _get_state(store, session_id)
            if body.lat is not None and body.lng is not None:
                label = body.label or f"Pinned location ({body.lat:.5f}, {body.lng:.5f})"
                result = graph.confirm_location(state, LocationResult(query=body.text or label, address=label, lat=body.lat, lng=body.lng, confidence=1.0, source="citizen", message=f"Location selected: {label}"))
            else:
                result = graph.resolve_location(state, body.text or body.label or "")
        except WorkflowError as exc:
            raise _workflow_error(exc) from exc
        return _persist_result(store, graph, result)

    @router.post("/api/session/{session_id}/media/decision", response_model=SessionView)
    def media_decision(session_id: UUID, body: MediaDecisionIn) -> SessionView:
        state = _get_state(store, session_id)
        state.image_decision = "added" if body.has_image else "skipped"
        message = "Please attach a photo of the issue when you are ready." if body.has_image else "No image added. Please complete the remaining details."
        _append_agent_turn(state, message)
        saved = store.save(state)
        return graph.view(saved, message=message)

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
            from io import BytesIO
            from PIL import Image, UnidentifiedImageError
            try:
                with Image.open(BytesIO(content)) as image:
                    image.verify()
            except (UnidentifiedImageError, OSError):
                raise HTTPException(status_code=422, detail=_error("INVALID_IMAGE", "The uploaded bytes are not a readable image.", False)) from None
            media_id = media_store.save(session_id, filename, content_type, content)
            result = graph.analyze_media(
                state,
                filename=filename,
                content_type=content_type,
                content=content,
            )
            result.state.image_decision = "added"
            result.state.messages.append(Message(role="citizen", text="Uploaded an image.", media_id=media_id))
            result.state.evidence[-1].media_id = media_id
            media_store.set_analysis(media_id, result.state.evidence[-1].model_dump(mode="json"))
        except WorkflowError as exc:
            raise _workflow_error(exc) from exc
        return _persist_result(store, graph, result)

    @router.get("/api/session/{session_id}/media/{media_id}")
    def get_session_media(session_id: UUID, media_id: str):
        try:
            stored = media_store.get(session_id, media_id)
        except MediaNotFound:
            raise _not_found() from None
        return Response(content=stored.content, media_type=stored.content_type, headers={"Content-Disposition": f'inline; filename="{stored.filename}"', "X-Content-SHA256": stored.sha256})

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
