from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.contracts import FieldValue, Location, Receipt, SessionState
from app.dashboard import build_public_tickets, build_summary, mask_sr_id
from app.grievance_store import MemoryGrievanceStore, StoredGrievance, persist_submission
from app.mailer import build_acknowledgement_bodies
from app.main import create_app
from app.neighbourhood import assemble_tracking_view, demo_timeline
from app.workflow.schema import mock_service_schemas

PEPPER = "dashboard-test-pepper"


def _record(
    sr_id: str,
    *,
    status: str = "pending",
    department: str = "Roads & Infrastructure",
    service_id: str = "road_issue",
    lat: float = 17.49,
    lng: float = 78.39,
    ward_name: str = "Kukatpally",
    ward_id: str = "101",
) -> StoredGrievance:
    return StoredGrievance(
        sr_id=sr_id,
        key_hash="seed-only",
        service_id=service_id,
        department=department,
        status=status,
        payload={
            "source": "demonstration",
            "fields": [{"id": "description", "value": "Large pothole"}],
            "location": {
                "address": f"{ward_name}, Hyderabad",
                "lat": lat,
                "lng": lng,
            },
            "ward": {"ward_id": ward_id, "ward_name": ward_name},
        },
        created_at=datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc),
    )


def test_mask_sr_id_redacts_prefix() -> None:
    assert mask_sr_id("CIV-20260827-0001-K7M2") == "···-K7M2"


def test_summary_aggregates_by_department_ward_and_status() -> None:
    records = [
        _record("CIV-1", status="pending", department="Roads & Infrastructure", ward_name="Kukatpally"),
        _record("CIV-2", status="in_progress", department="Roads & Infrastructure", ward_name="Kukatpally"),
        _record("CIV-3", status="completed", department="Sanitation Services", service_id="garbage_issue", ward_name="Gachibowli"),
    ]
    summary = build_summary(records)
    assert summary.total == 3
    assert summary.pending == 1
    assert summary.in_progress == 1
    assert summary.completed == 1
    roads = next(item for item in summary.departments if item.department == "Roads & Infrastructure")
    assert roads.total == 2
    assert roads.pending == 1
    assert roads.in_progress == 1


def test_public_ticket_list_omits_sensitive_fields() -> None:
    rows = build_public_tickets([_record("CIV-20260827-0001-K7M2")])
    dumped = rows[0].model_dump()
    assert dumped["ref_masked"] == "···-K7M2"
    assert dumped["ward_id"] == "101"
    assert "access_key" not in dumped
    assert "key_hash" not in dumped
    assert "fields" not in dumped


def test_public_ticket_filters_by_status_service_and_ward() -> None:
    records = [
        _record("CIV-1", status="pending", service_id="road_issue", ward_name="Kukatpally"),
        _record("CIV-2", status="completed", service_id="garbage_issue", ward_name="Gachibowli", ward_id="102"),
        _record("CIV-3", status="pending", service_id="garbage_issue", ward_name="Kukatpally"),
    ]
    assert len(build_public_tickets(records, status_filter="pending")) == 2
    assert len(build_public_tickets(records, service_id_filter="garbage_issue")) == 2
    assert len(build_public_tickets(records, ward_id_filter="101")) == 2
    combined = build_public_tickets(
        records,
        status_filter="pending",
        service_id_filter="garbage_issue",
        ward_id_filter="101",
    )
    assert len(combined) == 1
    assert combined[0].service_id == "garbage_issue"
    assert combined[0].status == "pending"


def test_status_update_changes_track_timeline(tmp_path: Path) -> None:
    store = MemoryGrievanceStore()
    state = SessionState(
        session_id=__import__("uuid").uuid4(),
        state="SUBMITTING",
        service_id="road_issue",
        fields=[FieldValue(id="description", value="Large pothole", required=True, status="accepted")],
        location=Location(query="JNTU", address="JNTU Metro Station", lat=17.49, lng=78.39, confidence=1.0),
    )
    schema = mock_service_schemas()["road_issue"]
    receipt = Receipt(reference="CIV-STATUS-1", status="pending", department=schema.department)
    persist_submission(
        store,
        state=state,
        service_id=schema.service_id,
        department=schema.department,
        receipt=receipt,
        pepper=PEPPER,
    )
    pending_view = assemble_tracking_view(store.get("CIV-STATUS-1"), [])
    assert pending_view.status == "Pending"
    assert pending_view.timeline[-1].done is False

    updated = store.update_status("CIV-STATUS-1", "completed")
    assert updated is not None
    completed_view = assemble_tracking_view(updated, [])
    assert completed_view.status == "Completed"
    assert completed_view.timeline[-1].done is True


def test_demo_status_patch_is_guarded(tmp_path: Path) -> None:
    client = TestClient(
        create_app(
            Settings(
                grievance_database_path=tmp_path / "grievances.db",
                supabase_url="",
                supabase_service_role_key="",
                tracking_pepper=PEPPER,
                demo_status_updates=False,
            )
        )
    )
    denied = client.patch("/api/demo/tickets/CIV-1/status", json={"status": "completed"})
    assert denied.status_code == 403


def test_dashboard_public_routes_return_redacted_payload(tmp_path: Path) -> None:
    client = TestClient(
        create_app(
            Settings(
                grievance_database_path=tmp_path / "grievances.db",
                supabase_url="",
                supabase_service_role_key="",
                tracking_pepper=PEPPER,
                seed_demo_tickets=False,
            )
        )
    )
    store = client.app.state.grievance_store
    store.save(_record("DEMO-1"))
    store.save(_record("DEMO-2", status="completed", ward_name="Gachibowli"))

    summary = client.get("/api/public/dashboard/summary")
    assert summary.status_code == 200
    assert summary.json()["total"] == 2

    tickets = client.get("/api/public/dashboard/tickets")
    assert tickets.status_code == 200
    body = tickets.json()
    assert len(body) == 2
    assert all("access_key" not in row for row in body)
    assert all("key_hash" not in row for row in body)
    assert all("ward_id" in row for row in body)

    filtered = client.get("/api/public/dashboard/tickets", params={"service_id": "road_issue", "ward_id": "101"})
    assert filtered.status_code == 200

    ward_map = client.get("/api/public/dashboard/ward-map")
    assert ward_map.status_code == 200
    assert ward_map.json()["type"] == "FeatureCollection"


def test_email_html_contains_human_label_and_status_badge() -> None:
    from app.grievance_store import tracking_view_from_record

    view = tracking_view_from_record(_record("CIV-EMAIL-1", status="pending"))
    _, html_body = build_acknowledgement_bodies(
        view=view,
        access_key="ABCD-EFGH-IJKL",
        track_url="https://civicagent.example/track",
    )
    assert "Description" in html_body
    assert "Pending" in html_body
    assert "Track this request" in html_body


def test_demo_timeline_reflects_completed_status() -> None:
    steps = demo_timeline(datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc), "completed")
    assert [step.id for step in steps] == ["received", "logged", "in_progress", "completed"]
    assert steps[-1].done is True
