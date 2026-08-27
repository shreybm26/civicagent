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
    assert "access_key" not in body
    assert "key_hash" not in body
    assert [step["id"] for step in body["timeline"]] == ["received", "logged", "ward"]
    assert body["timeline"][0]["done"] is True
    assert body["timeline"][2]["done"] is False
    assert any(item["source"] == "demonstration" for item in body["nearby"])
    assert any(item["count"] >= 1 for item in body["type_counts"])


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


def _settings(tmp_path: Path, **overrides: object) -> Settings:
    values = {
        "grievance_database_path": tmp_path / "grievances.db",
        "media_database_path": tmp_path / "media.db",
        "supabase_url": "",
        "supabase_service_role_key": "",
        "tracking_pepper": PEPPER,
        "resend_api_key": "",
        "public_base_url": "https://civicagent.example",
    }
    values.update(overrides)
    return Settings(**values)


def _lodge_pothole(client: TestClient) -> dict:
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
    client.patch(f"/api/session/{session_id}/fields/severity", json={"value": "high"})
    completed = client.post(f"/api/session/{session_id}/confirm", json={"confirmed": True})
    receipt = completed.json()["receipt"]
    assert receipt["access_key"]
    return receipt


def test_track_email_requires_key_and_explicit_confirm(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    receipt = _lodge_pothole(client)
    payload = {
        "sr_id": receipt["reference"],
        "access_key": receipt["access_key"],
        "email": "judge@example.com",
        "confirm_send": False,
    }
    denied_confirm = client.post("/api/track/email", json=payload)
    assert denied_confirm.status_code == 422
    assert "Confirm the email" in denied_confirm.json()["detail"]["message"]

    denied_key = client.post(
        "/api/track/email",
        json={**payload, "access_key": "NOPE-NOPE-NOPE", "confirm_send": True},
    )
    assert denied_key.status_code == 401
    assert "access_key" not in denied_key.json()["detail"]

    unconfigured = client.post("/api/track/email", json={**payload, "confirm_send": True})
    assert unconfigured.status_code == 503
    assert unconfigured.json()["detail"]["code"] == "EMAIL_FAILED"


def test_track_email_sends_via_resend_when_confirmed(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path, resend_api_key="re_test_key")))
    receipt = _lodge_pothole(client)
    response_mock = Mock(status_code=200)
    response_mock.json.return_value = {"id": "msg_demo"}
    with patch("app.mailer.httpx.post", return_value=response_mock) as posted:
        sent = client.post(
            "/api/track/email",
            json={
                "sr_id": receipt["reference"],
                "access_key": receipt["access_key"],
                "email": "Judge.Demo@example.com",
                "confirm_send": True,
            },
        )
    assert sent.status_code == 200
    assert sent.json() == {"sent": True, "to": "judge.demo@example.com"}
    body = posted.call_args.kwargs["json"]
    assert body["to"] == ["judge.demo@example.com"]
    assert receipt["reference"] in body["text"]
    assert receipt["access_key"] in body["text"]
    assert "https://civicagent.example/track" in body["text"]
    assert "not an official government email" in body["text"].lower()
    assert posted.call_args.kwargs["headers"]["Authorization"] == "Bearer re_test_key"


def test_track_email_explains_resend_test_sender_limit(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path, resend_api_key="re_test_key")))
    receipt = _lodge_pothole(client)
    response_mock = Mock(status_code=403)
    response_mock.json.return_value = {
        "statusCode": 403,
        "message": "You can only send testing emails to your own email address.",
    }
    with patch("app.mailer.httpx.post", return_value=response_mock):
        denied = client.post(
            "/api/track/email",
            json={
                "sr_id": receipt["reference"],
                "access_key": receipt["access_key"],
                "email": "judge@example.com",
                "confirm_send": True,
            },
        )
    assert denied.status_code == 422
    assert "account owner's inbox" in denied.json()["detail"]["message"]
    assert "gmail.com" not in denied.text.lower()


def test_sqlite_list_recent_returns_newest_first(tmp_path: Path) -> None:
    store = SqliteGrievanceStore(tmp_path / "grievances.db")
    schema = mock_service_schemas()["road_issue"]
    first = persist_submission(
        store,
        state=_state_with_fields(),
        service_id=schema.service_id,
        department=schema.department,
        receipt=Receipt(
            reference="CIV-OLD",
            status="Received",
            department=schema.department,
            timestamp=datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc),
        ),
        pepper=PEPPER,
    )
    second = persist_submission(
        store,
        state=_state_with_fields(),
        service_id=schema.service_id,
        department=schema.department,
        receipt=Receipt(
            reference="CIV-NEW",
            status="Received",
            department=schema.department,
            timestamp=datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc),
        ),
        pepper=PEPPER,
    )
    recent = store.list_recent()
    assert [row.sr_id for row in recent] == ["CIV-NEW", "CIV-OLD"]
    assert first and second
    assert all(row.key_hash != first for row in recent)
