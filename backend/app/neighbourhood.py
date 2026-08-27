"""Neighbourhood picture for the track page — filed reports plus a labelled demo cluster."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from math import asin, cos, radians, sin, sqrt
from typing import Any

from .contracts import NearbyReport, TimelineStep, TrackingView, TypeCount
from .grievance_store import StoredGrievance, tracking_view_from_record

SERVICE_LABELS = {
    "road_issue": "Road / pothole",
    "garbage_issue": "Garbage",
    "streetlight_issue": "Streetlight",
    "water_issue": "Water leak",
    "sanitation_issue": "Sanitation",
}

RADIUS_KM = 2.0


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lng2 - lng1)
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    return 2 * 6371 * asin(sqrt(min(1.0, a)))


def coords_from_payload(payload: dict[str, Any]) -> tuple[float, float] | None:
    location = payload.get("location") if isinstance(payload.get("location"), dict) else None
    if not location:
        return None
    lat, lng = location.get("lat"), location.get("lng")
    try:
        if lat is None or lng is None:
            return None
        return float(lat), float(lng)
    except (TypeError, ValueError):
        return None


def demo_timeline(submitted_at: datetime) -> list[TimelineStep]:
    stamped = submitted_at if submitted_at.tzinfo else submitted_at.replace(tzinfo=timezone.utc)
    logged = stamped + timedelta(minutes=2)
    return [
        TimelineStep(
            id="received",
            title="Received",
            detail="Acknowledgement generated for this demonstration civic cell.",
            at=stamped,
            done=True,
        ),
        TimelineStep(
            id="logged",
            title="Logged with the demonstration civic cell",
            detail="Filed details are stored for tracking. No live department inbox was notified.",
            at=logged,
            done=True,
        ),
        TimelineStep(
            id="ward",
            title="Awaiting ward assignment",
            detail="This step stays pending in the prototype. A production ULB API would sit here.",
            at=None,
            done=False,
        ),
    ]


def synthetic_nearby(lat: float, lng: float, origin_sr: str) -> list[NearbyReport]:
    """Stable fake cluster around the citizen's pin so the track page is never empty."""

    seed = int(sha256(origin_sr.encode("utf-8")).hexdigest()[:8], 16)
    mix = [
        ("road_issue", 3 + seed % 3, 0.22, 0.018, -0.010),
        ("garbage_issue", 2 + seed % 2, 0.48, -0.012, 0.014),
        ("streetlight_issue", 1 + seed % 2, 0.91, 0.009, 0.016),
        ("water_issue", 1 + (seed // 3) % 2, 1.15, -0.020, -0.008),
        ("sanitation_issue", 1, 1.40, 0.015, -0.018),
    ]
    reports: list[NearbyReport] = []
    for service_id, count, distance, d_lat, d_lng in mix:
        _ = (lat + d_lat, lng + d_lng)
        reports.append(
            NearbyReport(
                service_id=service_id,
                label=SERVICE_LABELS[service_id],
                distance_km=round(distance, 2),
                status="Received",
                source="demonstration",
                count=count,
            )
        )
    return reports


def filed_nearby(origin: StoredGrievance, others: list[StoredGrievance]) -> list[NearbyReport]:
    origin_coords = coords_from_payload(origin.payload)
    if origin_coords is None:
        return []
    lat, lng = origin_coords
    reports: list[NearbyReport] = []
    for record in others:
        if record.sr_id == origin.sr_id:
            continue
        coords = coords_from_payload(record.payload)
        if coords is None:
            continue
        distance = haversine_km(lat, lng, coords[0], coords[1])
        if distance > RADIUS_KM:
            continue
        reports.append(
            NearbyReport(
                service_id=record.service_id,
                label=SERVICE_LABELS.get(record.service_id, record.service_id),
                distance_km=round(distance, 2),
                status=record.status,
                source="filed",
                count=1,
            )
        )
    reports.sort(key=lambda item: item.distance_km)
    return reports[:8]


def type_counts(reports: list[NearbyReport], origin_service: str | None) -> list[TypeCount]:
    tallies = {key: 0 for key in SERVICE_LABELS}
    if origin_service in tallies:
        tallies[origin_service] += 1
    for report in reports:
        if report.service_id in tallies:
            tallies[report.service_id] += report.count
    return [
        TypeCount(service_id=key, label=SERVICE_LABELS[key], count=value)
        for key, value in tallies.items()
    ]


def assemble_tracking_view(record: StoredGrievance, others: list[StoredGrievance]) -> TrackingView:
    core = tracking_view_from_record(record)
    nearby = filed_nearby(record, others)
    coords = coords_from_payload(record.payload)
    if coords:
        nearby = synthetic_nearby(coords[0], coords[1], record.sr_id) + nearby
    return core.model_copy(
        update={
            "timeline": demo_timeline(record.created_at),
            "nearby": nearby,
            "type_counts": type_counts(nearby, record.service_id),
        }
    )
