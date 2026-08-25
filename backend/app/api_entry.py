"""Phase 1 HTTP adapters; domain workflow is intentionally not here yet."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from .config import Settings
from .contracts import CivicError, MessageIn, SessionView, session_view
from .provider_stub import ConversationProvider
from .store import SessionNotFound, SessionStore


def build_api_router(
    *,
    store: SessionStore,
    provider: ConversationProvider,
    settings: Settings,
) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "provider": settings.provider_mode,
            "schemas": settings.schema_count,
        }

    @router.post("/api/session", response_model=SessionView, status_code=status.HTTP_200_OK)
    def create_session() -> SessionView:
        return session_view(store.create())

    @router.post("/api/session/{session_id}/reset", response_model=SessionView)
    def reset_session(session_id: UUID) -> SessionView:
        try:
            return session_view(store.reset(session_id))
        except SessionNotFound:
            raise _not_found() from None

    @router.post("/api/session/{session_id}/message", response_model=SessionView)
    def message(session_id: UUID, body: MessageIn) -> SessionView:
        """Provide a safe Phase 1 message seam without advancing workflow state."""

        try:
            state = store.get(session_id)
        except SessionNotFound:
            raise _not_found() from None

        result = provider.classify(body.message, settings.known_service_ids)
        return session_view(state, agent_message=result.message)

    return router


def _not_found() -> HTTPException:
    error = CivicError(
        code="SESSION_NOT_FOUND",
        message="Session not found.",
        retryable=False,
    )
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.model_dump())
