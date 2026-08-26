from uuid import uuid4

import pytest

from app.contracts import Message
from app.store import SessionNotFound, SessionStore


def test_store_create_get_save_and_reset() -> None:
    store = SessionStore(max_sessions=2)
    state = store.create()

    fetched = store.get(state.session_id)
    fetched.state = "COLLECTING"
    store.save(fetched)
    assert store.get(state.session_id).state == "COLLECTING"

    reset = store.reset(state.session_id)
    assert reset.session_id == state.session_id
    assert reset.state == "IDLE"
    assert reset.messages == []


def test_store_returns_copies_and_evicts_oldest_session() -> None:
    store = SessionStore(max_sessions=2)
    first = store.create()
    first.messages.append(
        Message(
            role="citizen",
            text="local copy",
        )
    )
    assert store.get(first.session_id).messages == []

    second = store.create()
    store.create()
    with pytest.raises(SessionNotFound):
        store.get(first.session_id)
    assert store.get(second.session_id).state == "IDLE"


def test_store_unknown_session_is_explicit() -> None:
    with pytest.raises(SessionNotFound):
        SessionStore().get(uuid4())
