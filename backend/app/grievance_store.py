"""Persistent storage for submitted grievances so they can be tracked later.

Live chat sessions stay in memory. Only a successful submit is written here:
the service request id, a hash of the one-time access key, and the filed
payload. The plaintext key is never stored.

SQLite is the local/default backend. Supabase is used when
SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set (Railway).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import sqlite3
from threading import RLock
from typing import Any, Protocol

import httpx

from .contracts import Receipt, SessionState, TrackingField, TrackingView

ACCESS_KEY_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class GrievanceStoreError(RuntimeError):
    """Retryable failure while recording or looking up a grievance."""


@dataclass(frozen=True)
class StoredGrievance:
    sr_id: str
    key_hash: str
    service_id: str
    department: str
    status: str
    payload: dict[str, Any]
    created_at: datetime


class GrievanceStore(Protocol):
    backend_name: str

    def save(self, record: StoredGrievance) -> None: ...

    def get(self, sr_id: str) -> StoredGrievance | None: ...


def generate_access_key() -> str:
    """Readable 12-character key, grouped for the receipt screen."""

    groups = ["".join(secrets.choice(ACCESS_KEY_ALPHABET) for _ in range(4)) for _ in range(3)]
    return "-".join(groups)


def normalize_sr_id(value: str) -> str:
    return " ".join(value.strip().upper().split())


def normalize_access_key(value: str) -> str:
    return value.strip().upper().replace(" ", "")


def hash_access_key(access_key: str, pepper: str) -> str:
    return hmac.new(
        pepper.encode("utf-8"),
        normalize_access_key(access_key).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def access_key_matches(access_key: str, key_hash: str, pepper: str) -> bool:
    candidate = hash_access_key(access_key, pepper)
    return hmac.compare_digest(candidate, key_hash)


def snapshot_payload(state: SessionState) -> dict[str, Any]:
    """Store filed values only — not the chat transcript or photo bytes."""

    return {
        "service_id": state.service_id,
        "schema_version": state.schema_version,
        "fields": [{"id": field.id, "value": field.value} for field in state.fields],
        "location": state.location.model_dump(mode="json") if state.location else None,
        "evidence": [
            {"filename": item.filename, "relevant": item.relevant, "summary": item.summary}
            for item in state.evidence
        ],
    }


def persist_submission(
    store: GrievanceStore,
    *,
    state: SessionState,
    service_id: str,
    department: str,
    receipt: Receipt,
    pepper: str,
) -> str:
    access_key = generate_access_key()
    created = receipt.timestamp if receipt.timestamp.tzinfo else receipt.timestamp.replace(tzinfo=timezone.utc)
    record = StoredGrievance(
        sr_id=normalize_sr_id(receipt.reference),
        key_hash=hash_access_key(access_key, pepper),
        service_id=service_id,
        department=department,
        status=receipt.status,
        payload=snapshot_payload(state),
        created_at=created,
    )
    store.save(record)
    return access_key


def tracking_view_from_record(record: StoredGrievance) -> TrackingView:
    raw_fields = record.payload.get("fields") or []
    fields: list[TrackingField] = []
    if isinstance(raw_fields, list):
        for item in raw_fields:
            if isinstance(item, dict) and item.get("id"):
                fields.append(TrackingField(id=str(item["id"]), value=item.get("value")))
    location = record.payload.get("location") if isinstance(record.payload.get("location"), dict) else None
    address = location.get("address") if location else None
    return TrackingView(
        sr_id=record.sr_id,
        status=record.status,
        department=record.department,
        service_id=record.service_id,
        submitted_at=record.created_at,
        location=address if isinstance(address, str) else None,
        fields=fields,
    )


class MemoryGrievanceStore:
    """In-process store used by unit tests that do not need a database."""

    backend_name = "memory"

    def __init__(self) -> None:
        self._rows: dict[str, StoredGrievance] = {}
        self._lock = RLock()

    def save(self, record: StoredGrievance) -> None:
        with self._lock:
            self._rows[record.sr_id] = record

    def get(self, sr_id: str) -> StoredGrievance | None:
        with self._lock:
            return self._rows.get(normalize_sr_id(sr_id))


class SqliteGrievanceStore:
    backend_name = "sqlite"

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
                CREATE TABLE IF NOT EXISTS grievances (
                    sr_id TEXT PRIMARY KEY,
                    key_hash TEXT NOT NULL,
                    service_id TEXT NOT NULL,
                    department TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save(self, record: StoredGrievance) -> None:
        try:
            with self._lock, self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO grievances
                    (sr_id, key_hash, service_id, department, status, payload_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.sr_id,
                        record.key_hash,
                        record.service_id,
                        record.department,
                        record.status,
                        json.dumps(record.payload),
                        record.created_at.isoformat(),
                    ),
                )
        except sqlite3.Error as exc:
            raise GrievanceStoreError("The tracking record could not be saved. Please retry review.") from exc

    def get(self, sr_id: str) -> StoredGrievance | None:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM grievances WHERE sr_id = ?",
                (normalize_sr_id(sr_id),),
            ).fetchone()
        if row is None:
            return None
        return _row_to_record(
            sr_id=row["sr_id"],
            key_hash=row["key_hash"],
            service_id=row["service_id"],
            department=row["department"],
            status=row["status"],
            payload=json.loads(row["payload_json"]),
            created_at=row["created_at"],
        )


class SupabaseGrievanceStore:
    """PostgREST client using the service role. Never expose that key to the browser."""

    backend_name = "supabase"

    def __init__(self, url: str, service_role_key: str, *, timeout_seconds: float = 12.0) -> None:
        self._url = url.rstrip("/")
        self._headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
        }
        self._timeout = timeout_seconds

    def save(self, record: StoredGrievance) -> None:
        try:
            response = httpx.post(
                f"{self._url}/rest/v1/grievances",
                headers={**self._headers, "Prefer": "return=minimal"},
                json={
                    "sr_id": record.sr_id,
                    "key_hash": record.key_hash,
                    "service_id": record.service_id,
                    "department": record.department,
                    "status": record.status,
                    "payload": record.payload,
                    "created_at": record.created_at.isoformat(),
                },
                timeout=self._timeout,
            )
        except httpx.HTTPError as exc:
            raise GrievanceStoreError("The tracking service is temporarily unavailable. Please retry review.") from exc
        if response.status_code >= 400:
            raise GrievanceStoreError("The tracking record could not be saved. Please retry review.")

    def get(self, sr_id: str) -> StoredGrievance | None:
        try:
            response = httpx.get(
                f"{self._url}/rest/v1/grievances",
                headers=self._headers,
                params={"sr_id": f"eq.{normalize_sr_id(sr_id)}", "select": "*"},
                timeout=self._timeout,
            )
        except httpx.HTTPError as exc:
            raise GrievanceStoreError("The tracking service is temporarily unavailable.") from exc
        if response.status_code >= 400:
            raise GrievanceStoreError("The tracking service is temporarily unavailable.")
        rows = response.json()
        if not rows:
            return None
        row = rows[0]
        return _row_to_record(
            sr_id=row["sr_id"],
            key_hash=row["key_hash"],
            service_id=row["service_id"],
            department=row["department"],
            status=row["status"],
            payload=row.get("payload") or {},
            created_at=row["created_at"],
        )


def _row_to_record(
    *,
    sr_id: str,
    key_hash: str,
    service_id: str,
    department: str,
    status: str,
    payload: Any,
    created_at: str,
) -> StoredGrievance:
    parsed_payload = payload if isinstance(payload, dict) else {}
    timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return StoredGrievance(
        sr_id=sr_id,
        key_hash=key_hash,
        service_id=service_id,
        department=department,
        status=status,
        payload=parsed_payload,
        created_at=timestamp,
    )


def build_grievance_store(*, database_path: Path, supabase_url: str, supabase_service_role_key: str) -> GrievanceStore:
    if supabase_url and supabase_service_role_key:
        return SupabaseGrievanceStore(supabase_url, supabase_service_role_key)
    return SqliteGrievanceStore(database_path)
