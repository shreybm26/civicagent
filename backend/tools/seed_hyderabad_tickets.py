"""Idempotent Hyderabad demonstration grievances for the public dashboard."""

from __future__ import annotations

import argparse
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.config import settings
from app.contracts import TicketStatus
from app.grievance_store import StoredGrievance, build_grievance_store
from app.ward_lookup import WardInfo, WardLookup, get_ward_lookup

ACCESS_KEY_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
SERVICE_IDS = (
    "road_issue",
    "garbage_issue",
    "streetlight_issue",
    "water_issue",
    "sanitation_issue",
)
DEPARTMENTS = {
    "road_issue": "Roads & Infrastructure",
    "garbage_issue": "Sanitation Services",
    "streetlight_issue": "Electrical Services",
    "water_issue": "Water Services",
    "sanitation_issue": "Sanitation Services",
}
DESCRIPTIONS = {
    "road_issue": "Large pothole causing traffic slowdown near the junction.",
    "garbage_issue": "Uncollected garbage pile blocking the footpath.",
    "streetlight_issue": "Streetlight not working for several nights.",
    "water_issue": "Water leak flooding the lane.",
    "sanitation_issue": "Overflowing drain with foul smell.",
}
SEVERITIES = ("low", "medium", "high")
LANDMARKS = ("near metro exit", "opposite community hall", "beside bus stop", "near school gate")

ZONE_PROFILES: dict[str, tuple[float, float, float]] = {
    "hot": (0.55, 0.35, 0.10),
    "mixed": (0.40, 0.35, 0.25),
    "good": (0.20, 0.30, 0.50),
}

DEFAULT_THRESHOLD = 40
TARGET_COUNT = 325


def _dummy_key_hash(seed: str) -> str:
    return hashlib.sha256(f"seed-only:{seed}".encode("utf-8")).hexdigest()


def _pick_status(zone: str, index: int) -> TicketStatus:
    pending_w, progress_w, completed_w = ZONE_PROFILES[zone]
    slot = (index * 17 + hash(zone)) % 100
    if slot < pending_w * 100:
        return "pending"
    if slot < (pending_w + progress_w) * 100:
        return "in_progress"
    return "completed"


def _ward_sort_key(ward: WardInfo) -> tuple[int, str]:
    return (int(ward.ward_id), ward.ward_name) if ward.ward_id.isdigit() else (9999, ward.ward_name)


def _zone_for_index(index: int) -> str:
    return ("hot", "hot", "mixed", "mixed", "good", "good")[index % 6]


def _build_payload(
    *,
    service_id: str,
    ward: WardInfo,
    lat: float,
    lng: float,
    status: TicketStatus,
    index: int,
) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "schema_version": "1.0",
        "source": "demonstration",
        "fields": [
            {"id": "description", "value": DESCRIPTIONS[service_id]},
            {"id": "severity", "value": SEVERITIES[index % len(SEVERITIES)]},
            {"id": "landmark", "value": LANDMARKS[index % len(LANDMARKS)]},
        ],
        "location": {
            "query": f"Ward {ward.ward_id} {ward.ward_name}",
            "address": f"Ward {ward.ward_id}, {ward.ward_name}, Hyderabad",
            "lat": lat,
            "lng": lng,
            "confidence": 1.0,
            "source": "ward_centroid",
        },
        "ward": {"ward_id": ward.ward_id, "ward_name": ward.ward_name},
        "evidence": [],
    }


def _sr_id(day: datetime, sequence: int) -> str:
    nonce = "".join(secrets.choice(ACCESS_KEY_ALPHABET) for _ in range(4))
    return f"DEMO-{day:%Y%m%d}-{sequence:04d}-{nonce}"


def clear_demo_tickets(store) -> int:
    """Remove prior demonstration rows so the map can be rebalanced."""
    if store.backend_name == "sqlite":
        with sqlite3.connect(store.database_path) as connection:
            cursor = connection.execute("DELETE FROM grievances WHERE sr_id LIKE 'DEMO-%'")
            connection.commit()
            return int(cursor.rowcount or 0)

    if store.backend_name == "supabase":
        response = httpx.delete(
            f"{store._url.rstrip('/')}/rest/v1/grievances",
            headers={**store._headers, "Prefer": "return=minimal"},
            params={"sr_id": "like.DEMO-*"},
            timeout=store._timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError("Could not clear demonstration tickets from Supabase.")
        content_range = response.headers.get("content-range", "")
        if "/" in content_range:
            total = content_range.split("/")[-1]
            if total.isdigit():
                return int(total)
        return 0

    if store.backend_name == "memory":
        demo_ids = [sr_id for sr_id in store._rows if sr_id.startswith("DEMO-")]
        for sr_id in demo_ids:
            del store._rows[sr_id]
        return len(demo_ids)

    raise RuntimeError(f"Unsupported store backend: {store.backend_name}")


def seed_hyderabad_tickets(
    store=None,
    *,
    threshold: int = DEFAULT_THRESHOLD,
    target_count: int = TARGET_COUNT,
    lookup: WardLookup | None = None,
    replace: bool = False,
) -> int:
    store = store or build_grievance_store(
        database_path=settings.grievance_database_path,
        supabase_url=settings.supabase_url,
        supabase_service_role_key=settings.supabase_service_role_key,
    )
    lookup = lookup or get_ward_lookup()
    wards = sorted(lookup.all_wards(), key=_ward_sort_key)
    if not wards:
        raise RuntimeError("GHMC ward boundaries are not loaded.")

    if replace:
        clear_demo_tickets(store)

    existing = store.count()
    if not replace and existing >= threshold:
        return 0

    now = datetime.now(timezone.utc)
    created = 0
    sequence = existing + 1
    for index in range(target_count):
        ward = wards[index % len(wards)]
        point = lookup.representative_point(ward.ward_id)
        if point is None:
            continue
        lat, lng = point
        jitter = ((index % 5) - 2) * 0.00008
        lat += jitter
        lng -= jitter
        zone = _zone_for_index(index)
        service_id = SERVICE_IDS[index % len(SERVICE_IDS)]
        status = _pick_status(zone, index)
        created_at = now - timedelta(days=index % 14, hours=index % 20, minutes=index * 3)
        sr_id = _sr_id(created_at, sequence)
        sequence += 1
        record = StoredGrievance(
            sr_id=sr_id,
            key_hash=_dummy_key_hash(sr_id),
            service_id=service_id,
            department=DEPARTMENTS[service_id],
            status=status,
            payload=_build_payload(
                service_id=service_id,
                ward=ward,
                lat=lat,
                lng=lng,
                status=status,
                index=index,
            ),
            created_at=created_at,
        )
        store.save(record)
        created += 1
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Hyderabad demonstration grievances.")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete existing DEMO-* tickets and re-seed with city-wide ward distribution.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=TARGET_COUNT,
        help=f"Number of tickets to insert (default: {TARGET_COUNT}).",
    )
    args = parser.parse_args()
    inserted = seed_hyderabad_tickets(replace=args.replace, target_count=args.count)
    if inserted:
        print(f"Seeded {inserted} demonstration grievances across GHMC wards.")
    elif args.replace:
        print("Re-seed finished — no new tickets were inserted.")
    else:
        print("Seed skipped — store already has enough demonstration tickets.")


if __name__ == "__main__":
    main()
