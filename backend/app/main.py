"""FastAPI application factory for the CivicAgent workflow API."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api_entry import build_api_router
from .config import Settings, settings
from .provider_stub import ConversationProvider
from .store import SessionStore
from .workflow.graph import WorkflowGraph


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
    app.state.session_store = store
    app.state.conversation_provider = provider
    app.state.workflow = workflow
    return app


app = create_app()
