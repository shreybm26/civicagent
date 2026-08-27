"""Public dashboard aggregation over stored grievances."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from .contracts import (
    DashboardSummary,
    DepartmentStats,
    PublicTicketRow,
    ServiceId,
    TicketStatus,
    WardStats,
    normalize_ticket_status,
)
from .grievance_store import StoredGrievance
from .neighbourhood import SERVICE_LABELS
from .ward_lookup import WardInfo, WardLookup, get_ward_lookup, ward_for_record

STATUS_KEYS: tuple[TicketStatus, ...] = ("pending", "in_progress", "completed")


def mask_sr_id(sr_id: str) -> str:
    parts = sr_id.split("-")
    if len(parts) >= 2:
        return f"···-{parts[-1]}"
    return f"···-{sr_id[-4:]}" if len(sr_id) >= 4 else "···"


def _status_bucket(record: StoredGrievance) -> TicketStatus:
    return normalize_ticket_status(record.status)


def _empty_status_counts() -> dict[TicketStatus, int]:
    return {key: 0 for key in STATUS_KEYS}


def build_summary(records: list[StoredGrievance], lookup: WardLookup | None = None) -> DashboardSummary:
    lookup = lookup or get_ward_lookup()
    totals = _empty_status_counts()
    departments: dict[str, dict[TicketStatus, int]] = defaultdict(_empty_status_counts)
    wards: dict[tuple[str, str], dict[TicketStatus, int]] = defaultdict(_empty_status_counts)
    last_updated = datetime.fromtimestamp(0, tz=timezone.utc)

    for record in records:
        status = _status_bucket(record)
        totals[status] += 1
        departments[record.department][status] += 1
        ward = ward_for_record(record.payload, lookup)
        wards[(ward.ward_id, ward.ward_name)][status] += 1
        if record.created_at > last_updated:
            last_updated = record.created_at

    if records and last_updated.timestamp() == 0:
        last_updated = datetime.now(timezone.utc)

    department_rows = [
        DepartmentStats(
            department=department,
            total=sum(counts.values()),
            pending=counts["pending"],
            in_progress=counts["in_progress"],
            completed=counts["completed"],
        )
        for department, counts in sorted(departments.items(), key=lambda item: item[0])
    ]

    ward_rows: list[WardStats] = []
    for (ward_id, ward_name), counts in wards.items():
        total = sum(counts.values())
        open_count = counts["pending"] + counts["in_progress"]
        ward_rows.append(
            WardStats(
                ward_id=ward_id,
                ward_name=ward_name,
                total=total,
                pending=counts["pending"],
                in_progress=counts["in_progress"],
                completed=counts["completed"],
                open_ratio=round(open_count / total, 3) if total else 0.0,
            )
        )
    ward_rows.sort(key=lambda item: (-item.open_ratio, -item.total, item.ward_name))

    return DashboardSummary(
        total=len(records),
        pending=totals["pending"],
        in_progress=totals["in_progress"],
        completed=totals["completed"],
        last_updated=last_updated if records else datetime.now(timezone.utc),
        departments=department_rows,
        wards=ward_rows,
    )


def build_public_tickets(
    records: list[StoredGrievance],
    *,
    status_filter: TicketStatus | None = None,
    limit: int = 50,
    lookup: WardLookup | None = None,
) -> list[PublicTicketRow]:
    lookup = lookup or get_ward_lookup()
    rows: list[PublicTicketRow] = []
    for record in records:
        status = _status_bucket(record)
        if status_filter and status != status_filter:
            continue
        ward = ward_for_record(record.payload, lookup)
        service_id = record.service_id if record.service_id in SERVICE_LABELS else "road_issue"
        rows.append(
            PublicTicketRow(
                ref_masked=mask_sr_id(record.sr_id),
                service_id=service_id,  # type: ignore[arg-type]
                service_label=SERVICE_LABELS.get(record.service_id, record.service_id),
                ward_name=ward.ward_name,
                department=record.department,
                status=status,
                reported_at=record.created_at,
            )
        )
        if len(rows) >= limit:
            break
    return rows


def ward_stats_for_map(records: list[StoredGrievance], lookup: WardLookup | None = None) -> dict[str, dict[str, Any]]:
    lookup = lookup or get_ward_lookup()
    stats: dict[str, dict[str, Any]] = {}
    for record in records:
        ward = ward_for_record(record.payload, lookup)
        bucket = stats.setdefault(
            ward.ward_id,
            {
                "ward_id": ward.ward_id,
                "ward_name": ward.ward_name,
                "total": 0,
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
            },
        )
        status = _status_bucket(record)
        bucket["total"] += 1
        bucket[status] += 1
    for bucket in stats.values():
        open_count = bucket["pending"] + bucket["in_progress"]
        total = bucket["total"]
        bucket["open_ratio"] = round(open_count / total, 3) if total else 0.0
    return stats


def build_ward_map_geojson(records: list[StoredGrievance], lookup: WardLookup | None = None) -> dict[str, Any]:
    lookup = lookup or get_ward_lookup()
    stats = ward_stats_for_map(records, lookup)
    payload = lookup.load_geojson()
    features = []
    for feature in payload.get("features") or []:
        if not isinstance(feature, dict):
            continue
        props = dict(feature.get("properties") or {})
        name = props.get("name") or ""
        parsed = None
        if isinstance(name, str):
            from .ward_lookup import parse_ward_name

            parsed = parse_ward_name(name)
        if parsed is None:
            features.append(feature)
            continue
        counts = stats.get(
            parsed.ward_id,
            {
                "ward_id": parsed.ward_id,
                "ward_name": parsed.ward_name,
                "total": 0,
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "open_ratio": 0.0,
            },
        )
        props.update(counts)
        features.append({**feature, "properties": props})
    return {"type": "FeatureCollection", "features": features}
