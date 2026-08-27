"""SQLite-backed image storage for the local CivicAgent demo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from threading import RLock
from uuid import UUID, uuid4


@dataclass(frozen=True)
class StoredMedia:
    media_id: str
    session_id: UUID
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    content: bytes
    analysis: dict | None


class MediaNotFound(KeyError):
    pass


class MediaStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS media (
                    media_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    sha256 TEXT NOT NULL,
                    content BLOB NOT NULL,
                    analysis_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS media_session_idx ON media(session_id)")

    def save(self, session_id: UUID, filename: str, content_type: str, content: bytes) -> str:
        media_id = str(uuid4())
        digest = hashlib.sha256(content).hexdigest()
        with self._lock, self._connect() as connection:
            connection.execute(
                "INSERT INTO media VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?)",
                (
                    media_id,
                    str(session_id),
                    filename,
                    content_type,
                    len(content),
                    digest,
                    content,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        return media_id

    def set_analysis(self, media_id: str, analysis: dict) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                "UPDATE media SET analysis_json = ? WHERE media_id = ?",
                (json.dumps(analysis), media_id),
            )

    def get(self, session_id: UUID, media_id: str) -> StoredMedia:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM media WHERE session_id = ? AND media_id = ?",
                (str(session_id), media_id),
            ).fetchone()
        if row is None:
            raise MediaNotFound(media_id)
        return StoredMedia(
            media_id=row["media_id"],
            session_id=UUID(row["session_id"]),
            filename=row["filename"],
            content_type=row["content_type"],
            size_bytes=row["size_bytes"],
            sha256=row["sha256"],
            content=row["content"],
            analysis=json.loads(row["analysis_json"]) if row["analysis_json"] else None,
        )

    def delete_session(self, session_id: UUID) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("DELETE FROM media WHERE session_id = ?", (str(session_id),))
