"""Small replaceable schema port used until the canonical JSON registry lands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..contracts import ServiceId


@dataclass(frozen=True)
class SchemaField:
    id: str
    field_type: str
    required: bool
    options: tuple[str, ...] = ()
    image_derivable: bool = False


@dataclass(frozen=True)
class ServiceSchema:
    service_id: ServiceId
    service_name: str
    description: str
    department: str
    keywords: tuple[str, ...]
    fields: tuple[SchemaField, ...]
    schema_version: str = "1.0"
    submission_endpoint: str = "/api/submit"
    id_prefix: str = "CIV"

    @property
    def required_fields(self) -> tuple[SchemaField, ...]:
        return tuple(field for field in self.fields if field.required)

    def field(self, field_id: str) -> SchemaField | None:
        return next((field for field in self.fields if field.id == field_id), None)


def mock_service_schemas() -> dict[ServiceId, ServiceSchema]:
    """Return the deterministic five-service fallback for Phase 2.

    Shrey's JSON registry can replace this function without changing graph or
    API contracts. Departments and field requirements are kept here solely as
    a runnable mock until that registry is merged.
    """

    text = lambda field_id, required=False, image_derivable=False: SchemaField(
        field_id, "text", required, (), image_derivable
    )
    location = lambda: SchemaField("location", "location", True)
    choice = lambda field_id, options, required=True, image_derivable=False: SchemaField(
        field_id, "choice", required, tuple(options), image_derivable
    )
    image = lambda: SchemaField("photo", "image", False)
    additional = lambda: SchemaField("additional_details", "text", False, image_derivable=True)

    return {
        "road_issue": ServiceSchema(
            "road_issue",
            "Road / Pothole Complaint",
            "Report road damage, potholes, or surface deterioration",
            "Roads & Infrastructure",
            ("pothole", "road", "crack", "damage", "pavement", "asphalt", "surface"),
            (
                location(),
                text("description", True),
                choice("severity", ("low", "medium", "high"), True, True),
                image(),
                additional(),
                text("landmark", False, True),
            ),
        ),
        "garbage_issue": ServiceSchema(
            "garbage_issue",
            "Garbage Accumulation Complaint",
            "Report garbage accumulation or missed collection",
            "Sanitation Services",
            ("garbage", "trash", "waste", "dump", "litter"),
            (
                location(),
                text("description", True),
                choice("severity", ("low", "medium", "high"), True, True),
                text("duration"),
                image(),
                additional(),
                text("landmark", False, True),
            ),
        ),
        "streetlight_issue": ServiceSchema(
            "streetlight_issue",
            "Streetlight Complaint",
            "Report a broken or inactive streetlight",
            "Electrical Services",
            ("streetlight", "street light", "lamp", "pole", "light"),
            (
                location(),
                text("description", True),
                text("pole_number", False, True),
                text("duration", True),
                text("time_noticed"),
                image(),
                additional(),
                text("landmark", False, True),
            ),
        ),
        "water_issue": ServiceSchema(
            "water_issue",
            "Water Leak Complaint",
            "Report a water leak or supply infrastructure problem",
            "Water Services",
            ("water", "leak", "pipe", "burst", "supply"),
            (
                location(),
                text("description", True),
                choice("leak_type", ("pipe", "tap", "supply", "unknown"), True, True),
                choice("severity", ("low", "medium", "high"), True, True),
                image(),
                additional(),
                text("landmark", False, True),
            ),
        ),
        "sanitation_issue": ServiceSchema(
            "sanitation_issue",
            "Sanitation Complaint",
            "Report a sanitation or public hygiene issue",
            "Sanitation Services",
            ("sanitation", "sewage", "drain", "toilet", "hygiene"),
            (
                location(),
                text("description", True),
                choice("issue_type", ("sewage", "drain", "public_hygiene", "other"), True, True),
                text("duration"),
                image(),
                additional(),
                text("landmark", False, True),
            ),
        ),
    }


def field_value_is_valid(field: SchemaField, value: Any) -> bool:
    if value is None or (isinstance(value, str) and not value.strip()):
        return False
    if field.options and str(value).lower() not in field.options:
        return False
    return True
