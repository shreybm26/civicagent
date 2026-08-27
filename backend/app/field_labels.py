"""Human labels for schema field ids used in emails and public views."""

from __future__ import annotations

LABELS: dict[str, str] = {
    "location": "Location",
    "description": "Description",
    "severity": "Severity",
    "photo": "Photo",
    "additional_details": "Additional details",
    "landmark": "Landmark",
    "duration": "How long has this been happening?",
    "time_noticed": "When did you first notice it?",
    "pole_number": "Streetlight pole number",
    "leak_type": "Leak type",
    "issue_type": "Issue type",
}


def field_label(field_id: str) -> str:
    return LABELS.get(field_id, field_id.replace("_", " ").strip().capitalize())
