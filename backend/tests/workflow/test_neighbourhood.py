from datetime import datetime, timezone

from app.grievance_store import StoredGrievance
from app.neighbourhood import (
    assemble_tracking_view,
    coords_from_payload,
    demo_timeline,
    filed_nearby,
    haversine_km,
    synthetic_nearby,
)


def _record(
    sr_id: str,
    *,
    lat: float | None = 17.49,
    lng: float | None = 78.39,
    service_id: str = "road_issue",
) -> StoredGrievance:
    location = {"address": "JNTU Metro", "lat": lat, "lng": lng} if lat is not None else None
    return StoredGrievance(
        sr_id=sr_id,
        key_hash="deadbeef",
        service_id=service_id,
        department="Roads",
        status="Received",
        payload={"fields": [{"id": "description", "value": "pothole"}], "location": location},
        created_at=datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc),
    )


def test_haversine_is_zero_for_the_same_point() -> None:
    assert haversine_km(17.49, 78.39, 17.49, 78.39) == 0


def test_coords_from_payload_reads_location_pin() -> None:
    assert coords_from_payload(_record("CIV-1").payload) == (17.49, 78.39)
    assert coords_from_payload({"location": None}) is None


def test_demo_timeline_keeps_ward_assignment_pending() -> None:
    steps = demo_timeline(datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc))
    assert [step.id for step in steps] == ["received", "logged", "ward"]
    assert steps[0].done is True
    assert steps[1].done is True
    assert steps[2].done is False
    assert steps[2].at is None


def test_filed_nearby_only_includes_reports_within_two_km() -> None:
    origin = _record("CIV-ORIGIN")
    close = _record("CIV-CLOSE", lat=17.492, lng=78.391, service_id="garbage_issue")
    far = _record("CIV-FAR", lat=18.0, lng=78.39, service_id="water_issue")
    nearby = filed_nearby(origin, [origin, close, far])
    assert [item.service_id for item in nearby] == ["garbage_issue"]
    assert nearby[0].source == "filed"
    assert nearby[0].count == 1


def test_assemble_tracking_view_mixes_synthetic_and_filed_without_keys() -> None:
    origin = _record("CIV-ORIGIN")
    neighbour = _record("CIV-NEXT", lat=17.491, lng=78.3905, service_id="streetlight_issue")
    view = assemble_tracking_view(origin, [origin, neighbour])
    dumped = view.model_dump()
    assert "access_key" not in dumped
    assert "key_hash" not in dumped
    assert len(view.timeline) == 3
    assert any(item.source == "demonstration" for item in view.nearby)
    assert any(item.source == "filed" and item.service_id == "streetlight_issue" for item in view.nearby)
    assert any(item.count > 0 for item in view.type_counts)
    assert "Not live municipal data" in view.neighbourhood_note


def test_synthetic_nearby_is_stable_for_the_same_sr_id() -> None:
    first = synthetic_nearby(17.49, 78.39, "CIV-SAME")
    second = synthetic_nearby(12.97, 77.59, "CIV-SAME")
    assert [item.count for item in first] == [item.count for item in second]
