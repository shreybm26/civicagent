"""Bounded in-memory task store for anonymous hackathon sessions."""

from __future__ import annotations

from collections import OrderedDict
from threading import RLock
from uuid import UUID, uuid4

from .contracts import SessionState, idle_session


class SessionNotFound(KeyError):
    """Raised when an API request references an unknown session."""


class SessionStore:
    """Thread-safe bounded store that never logs session contents."""

    def __init__(self, max_sessions: int = 100) -> None:
        if max_sessions < 1:
            raise ValueError("max_sessions must be at least 1")
        self._max_sessions = max_sessions
        self._sessions: OrderedDict[UUID, SessionState] = OrderedDict()
        self._lock = RLock()

    def create(self) -> SessionState:
        with self._lock:
            session_id = uuid4()
            self._sessions[session_id] = idle_session(session_id)
            self._evict_if_needed()
            return self._copy(self._sessions[session_id])

    def get(self, session_id: UUID) -> SessionState:
        with self._lock:
            try:
                state = self._sessions[session_id]
            except KeyError as exc:
                raise SessionNotFound(str(session_id)) from exc
            self._sessions.move_to_end(session_id)
            return self._copy(state)

    def save(self, state: SessionState) -> SessionState:
        with self._lock:
            if state.session_id not in self._sessions:
                raise SessionNotFound(str(state.session_id))
            self._sessions[state.session_id] = self._copy(state)
            self._sessions.move_to_end(state.session_id)
            return self._copy(state)

    def reset(self, session_id: UUID) -> SessionState:
        with self._lock:
            if session_id not in self._sessions:
                raise SessionNotFound(str(session_id))
            self._sessions[session_id] = idle_session(session_id)
            self._sessions.move_to_end(session_id)
            return self._copy(self._sessions[session_id])

    def clear(self) -> None:
        with self._lock:
            self._sessions.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._sessions)

    def _evict_if_needed(self) -> None:
        while len(self._sessions) > self._max_sessions:
            self._sessions.popitem(last=False)

    @staticmethod
    def _copy(state: SessionState) -> SessionState:
        return state.model_copy(deep=True)
