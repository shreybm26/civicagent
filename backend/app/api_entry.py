"""HTTP adapters for the deterministic CivicAgent workflow."""

from __future__ import annotations

import logging
from pathlib import PurePath
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from fastapi.responses import Response

from .config import Settings
from .contracts import (
    CivicError,
    ConfirmIn,
    DashboardSummary,
    DemoStatusIn,
    EmailSentView,
    FieldEditIn,
    LocationIn,
    LocationResult,
    MediaDecisionIn,
    Message,
    MessageIn,
    PublicTicketRow,
    SessionView,
    ServiceId,
    TicketStatus,
    TrackEmailIn,
    TrackIn,
    TrackingView,
)
from .dashboard import build_public_tickets, build_summary, build_ward_map_geojson
from .grievance_store import (
    GrievanceStore,
    GrievanceStoreError,
    StoredGrievance,
    access_key_matches,
)
from .mailer import MailError, normalize_email, send_acknowledgement
from .media_store import MediaNotFound, MediaStore
from .neighbourhood import assemble_tracking_view
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
    grievance_store: GrievanceStore,
) -> APIRouter:
    """Create route adapters around the shared store and workflow ports."""

    # Preserve the provider injection seam for Shrey's router/collector adapter.
    _ = provider
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "provider": settings.provider_mode,
            "schemas": settings.schema_count,
            # Never return the key; this only confirms whether the live process
            # constructed the Gemini-backed workflow ports.
            "gemini_enabled": settings.provider_mode in {"gemini", "llm", "auto"} and bool(settings.gemini_api_key),
            "gemini_model": settings.gemini_model if settings.gemini_api_key else None,
            "gemini_timeout_seconds": settings.gemini_timeout_seconds,
            "tracking_store": grievance_store.backend_name,
            "mail_configured": settings.mail_configured,
            "mail_backend": settings.mail_backend,
        }

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
        message = "Upload a photo when you're ready." if body.has_image else "No photo — that's fine. A few details still needed."
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
            relevant = bool(result.state.evidence and result.state.evidence[-1].relevant)
            result.state.image_decision = "added" if relevant else "pending"
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

    @router.post("/api/track", response_model=TrackingView)
    def track_grievance(body: TrackIn) -> TrackingView:
        record = _authorized_record(grievance_store, body, settings)
        return _enriched_tracking_view(grievance_store, record)

    @router.post("/api/track/email", response_model=EmailSentView)
    def email_grievance(request: Request, body: TrackEmailIn) -> EmailSentView:
        if not body.confirm_send:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=_error(
                    "EMAIL_NOT_CONFIRMED",
                    "Confirm the email address before sending. A typo would send the access key to the wrong inbox.",
                    False,
                ),
            )
        record = _authorized_record(grievance_store, body, settings)
        view = _enriched_tracking_view(grievance_store, record)
        try:
            to_email = normalize_email(body.email)
            send_acknowledgement(
                to_email=to_email,
                view=view,
                access_key=body.access_key,
                track_url=_public_track_url(request, settings),
                resend_api_key=settings.resend_api_key,
                resend_from=settings.resend_from,
                sendgrid_api_key=settings.sendgrid_api_key,
                sendgrid_from=settings.sendgrid_from,
                smtp_host=settings.smtp_host,
                smtp_port=settings.smtp_port,
                smtp_username=settings.smtp_username,
                smtp_password=settings.smtp_password,
                smtp_from=settings.smtp_from,
            )
        except MailError as exc:
            message = str(exc)
            retryable = "temporarily" in message.lower() or "not configured" in message.lower()
            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                    if retryable
                    else status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=_error("EMAIL_FAILED", message, retryable),
            ) from exc
        return EmailSentView(sent=True, to=to_email)

    @router.get("/api/public/dashboard/summary", response_model=DashboardSummary)
    def dashboard_summary() -> DashboardSummary:
        try:
            records = grievance_store.list_recent(500)
        except GrievanceStoreError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=_error("DASHBOARD_UNAVAILABLE", str(exc), True),
            ) from exc
        return build_summary(records)

    @router.get("/api/public/dashboard/tickets", response_model=list[PublicTicketRow])
    def dashboard_tickets(
        status: TicketStatus | None = None,
        service_id: ServiceId | None = None,
        ward_id: str | None = None,
        limit: int = 50,
    ) -> list[PublicTicketRow]:
        capped = min(max(limit, 1), 100)
        try:
            records = grievance_store.list_recent(500)
        except GrievanceStoreError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=_error("DASHBOARD_UNAVAILABLE", str(exc), True),
            ) from exc
        return build_public_tickets(
            records,
            status_filter=status,
            service_id_filter=service_id,
            ward_id_filter=ward_id,
            limit=capped,
        )

    @router.get("/api/public/dashboard/ward-map")
    def dashboard_ward_map() -> dict[str, object]:
        try:
            records = grievance_store.list_recent(500)
        except GrievanceStoreError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=_error("DASHBOARD_UNAVAILABLE", str(exc), True),
            ) from exc
        return build_ward_map_geojson(records)

    @router.patch("/api/demo/tickets/{sr_id}/status", response_model=TrackingView)
    def demo_update_ticket_status(sr_id: str, body: DemoStatusIn) -> TrackingView:
        if not settings.demo_status_updates:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=_error(
                    "DEMO_STATUS_DISABLED",
                    "Demo status updates are disabled. Set DEMO_STATUS_UPDATES=1 to enable.",
                    False,
                ),
            )
        try:
            updated = grievance_store.update_status(sr_id, body.status)
        except GrievanceStoreError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=_error("TRACK_UNAVAILABLE", str(exc), True),
            ) from exc
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_error("TRACK_NOT_FOUND", "Service request not found.", False),
            )
        return _enriched_tracking_view(grievance_store, updated)

    return router


def _authorized_record(grievance_store: GrievanceStore, body: TrackIn, settings: Settings) -> StoredGrievance:
    try:
        record = grievance_store.get(body.sr_id)
    except GrievanceStoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_error("TRACK_UNAVAILABLE", str(exc), True),
        ) from exc
    if record is None or not access_key_matches(body.access_key, record.key_hash, settings.tracking_pepper):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_error(
                "TRACK_NOT_FOUND",
                "Service request not found or access key is incorrect.",
                False,
            ),
        )
    return record


def _enriched_tracking_view(grievance_store: GrievanceStore, record: StoredGrievance) -> TrackingView:
    try:
        others = grievance_store.list_recent()
    except GrievanceStoreError:
        others = []
    return assemble_tracking_view(record, others)


def _public_track_url(request: Request, settings: Settings) -> str:
    base = settings.public_base_url or str(request.base_url).rstrip("/")
    return f"{base}/track"


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
