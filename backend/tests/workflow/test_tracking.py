from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.config import Settings
from app.contracts import FieldValue, Location, Receipt, SessionState
from app.grievance_store import (
    SqliteGrievanceStore,
    SupabaseGrievanceStore,
    access_key_matches,
    generate_access_key,
    hash_access_key,
    persist_submission,
)
from app.main import create_app
from app.workflow.schema import mock_service_schemas


PEPPER = "test-tracking-pepper"


def _state_with_fields() -> SessionState:
    return SessionState(
        session_id=uuid4(),
        state="SUBMITTING",
        service_id="road_issue",
        fields=[
            FieldValue(id="location", value="JNTU Metro", required=True, status="accepted"),
            FieldValue(id="description", value="Large pothole", required=True, status="accepted"),
        ],
        location=Location(query="JNTU", address="JNTU Metro Station", lat=17.49, lng=78.39, confidence=1.0, source="curated_location"),
    )


def test_access_key_hash_is_stable_and_case_insensitive() -> None:
    key = "AB2C-DE3F-GH4K"
    digest = hash_access_key(key, PEPPER)
    assert access_key_matches("ab2c-de3f-gh4k", digest, PEPPER) is True
    assert access_key_matches("ZZZZ-ZZZZ-ZZZZ", digest, PEPPER) is False
    assert digest != key


def test_sqlite_store_persists_hash_not_plaintext(tmp_path: Path) -> None:
    store = SqliteGrievanceStore(tmp_path / "grievances.db")
    state = _state_with_fields()
    schema = mock_service_schemas()["road_issue"]
    receipt = Receipt(reference="CIV-20260827-0001-TEST", status="Received", department=schema.department)
    access_key = persist_submission(
        store,
        state=state,
        service_id=schema.service_id,
        department=schema.department,
        receipt=receipt,
        pepper=PEPPER,
    )

    stored = store.get(receipt.reference)
    assert stored is not None
    assert stored.key_hash == hash_access_key(access_key, PEPPER)
    raw = (tmp_path / "grievances.db").read_bytes()
    assert access_key.encode() not in raw
    assert b"Large pothole" in raw


def test_track_api_round_trip_uses_isolated_sqlite(tmp_path: Path) -> None:
    client = TestClient(
        create_app(
            Settings(
                grievance_database_path=tmp_path / "grievances.db",
                supabase_url="",
                supabase_service_role_key="",
                tracking_pepper=PEPPER,
            )
        )
    )
    health = client.get("/health").json()
    assert health["tracking_store"] == "sqlite"

    session_id = client.post("/api/session").json()["session_id"]
    client.post(
        f"/api/session/{session_id}/message",
        json={"message": "There is a huge pothole and a bike almost fell"},
    )
    client.post(f"/api/session/{session_id}/location/resolve", json={"text": "near JNTU metro"})
    client.post(f"/api/session/{session_id}/media/decision", json={"has_image": False})
    client.patch(
        f"/api/session/{session_id}/fields/description",
        json={"value": "Large pothole near JNTU Metro"},
    )
    ready = client.patch(f"/api/session/{session_id}/fields/severity", json={"value": "high"})
    assert ready.json()["state"] == "REVIEWING"
    completed = client.post(f"/api/session/{session_id}/confirm", json={"confirmed": True})
    receipt = completed.json()["receipt"]
    assert completed.json()["state"] == "COMPLETED"
    assert receipt["access_key"]
    tracked = client.post(
        "/api/track",
        json={"sr_id": receipt["reference"].lower(), "access_key": receipt["access_key"].lower()},
    )
    assert tracked.status_code == 200
    body = tracked.json()
    assert body["department"]
    assert any(field["id"] == "location" for field in body["fields"])


def test_supabase_store_uses_service_role_and_never_returns_key() -> None:
    store = SupabaseGrievanceStore("https://example.supabase.co", "service-role-secret")
    record_payload = {
        "sr_id": "CIV-1",
        "key_hash": hash_access_key("AAAA-BBBB-CCCC", PEPPER),
        "service_id": "road_issue",
        "department": "Roads",
        "status": "Received",
        "payload": {"fields": [{"id": "location", "value": "JNTU"}]},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    get_response = Mock(status_code=200)
    get_response.json.return_value = [record_payload]
    with patch("app.grievance_store.httpx.get", return_value=get_response) as get:
        found = store.get("civ-1")
    assert found is not None
    assert found.sr_id == "CIV-1"
    assert get.call_args.kwargs["headers"]["apikey"] == "service-role-secret"
    assert "AAAA-BBBB-CCCC" not in str(found)


def test_generated_access_key_has_readable_groups() -> None:
    key = generate_access_key()
    parts = key.split("-")
    assert len(parts) == 3
    assert all(len(part) == 4 for part in parts)
