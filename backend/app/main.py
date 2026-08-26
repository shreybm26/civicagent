"""FastAPI application factory for the CivicAgent workflow API."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api_entry import build_api_router
from .config import PROJECT_ROOT, Settings, settings
from .provider_stub import ConversationProvider
from .store import SessionStore
from .workflow.graph import WorkflowGraph

FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


def _mount_frontend(app: FastAPI) -> None:
    """Serve the built React app from the same origin as the API when present."""

    index = FRONTEND_DIST / "index.html"
    if not index.is_file():
        return

    assets = FRONTEND_DIST / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="frontend-assets")

    @app.get("/")
    def frontend_index() -> FileResponse:
        return FileResponse(index)

    @app.get("/{full_path:path}")
    def frontend_spa(full_path: str) -> FileResponse:
        candidate = (FRONTEND_DIST / full_path).resolve()
        try:
            candidate.relative_to(FRONTEND_DIST.resolve())
        except ValueError:
            return FileResponse(index)
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index)


def create_app(runtime_settings: Settings = settings) -> FastAPI:
    app = FastAPI(title="CivicAgent API", version="0.2.0")
    store = SessionStore(max_sessions=runtime_settings.max_sessions)
    provider = ConversationProvider()
    workflow = WorkflowGraph()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(runtime_settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    app.include_router(
        build_api_router(
            store=store,
            provider=provider,
            settings=runtime_settings,
            graph=workflow,
        )
    )
    _mount_frontend(app)
    app.state.session_store = store
    app.state.conversation_provider = provider
    app.state.workflow = workflow
    return app


app = create_app()
