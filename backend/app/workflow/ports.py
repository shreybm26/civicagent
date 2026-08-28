"""Replaceable proposal ports and deterministic Phase 2 mocks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from ..contracts import Candidate, ImageResult, RouterResult, ServiceId
from .schema import SchemaField, ServiceSchema


class RouterPort(Protocol):
    def classify(self, message: str, schemas: Mapping[ServiceId, ServiceSchema]) -> RouterResult: ...


class CollectorPort(Protocol):
    def collect(self, field: SchemaField, message: str) -> Candidate | None: ...


class ImagePort(Protocol):
    def analyze(
        self,
        schema: ServiceSchema,
        *,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> ImageResult: ...


class MockRouter:
    """Keyword proposal constrained to the five schema IDs."""

    def classify(self, message: str, schemas: Mapping[ServiceId, ServiceSchema]) -> RouterResult:
        lowered = message.casefold()
        scores = {
            service_id: sum(1 for keyword in schema.keywords if keyword in lowered)
            for service_id, schema in schemas.items()
        }
        best = max(scores.values(), default=0)
        winners = [service_id for service_id, score in scores.items() if score == best and score > 0]
        if len(winners) != 1:
            return RouterResult(
                service_id=None,
                confidence=0.0,
                needs_clarification=True,
                message="I can take road, garbage, streetlight, water, or sanitation complaints. Which one is this?",
            )
        confidence = min(0.95, 0.6 + (0.1 * best))
        service_id = winners[0]
        return RouterResult(
            service_id=service_id,
            confidence=confidence,
            needs_clarification=confidence < 0.7,
            message=f"Got it — a {schemas[service_id].service_name.lower()} issue.",
        )


class MockCollector:
    """Minimal deterministic field collector; no civic policy inference."""

    def collect(self, field: SchemaField, message: str) -> Candidate | None:
        text = message.strip()
        if not text:
            return None
        lowered = text.casefold()
        if field.options:
            for option in field.options:
                if option in lowered.replace("-", " "):
                    return Candidate(field_id=field.id, value=option, source="citizen", confidence=1.0)
            if field.id == "severity":
                if any(word in lowered for word in ("huge", "danger", "fell", "blocked", "major")):
                    return Candidate(field_id=field.id, value="high", source="conversation", confidence=0.8)
                if any(word in lowered for word in ("small", "minor", "slight")):
                    return Candidate(field_id=field.id, value="low", source="conversation", confidence=0.8)
            return None
        return Candidate(field_id=field.id, value=text, source="citizen", confidence=1.0)


class MockImageService:
    """Deterministic evidence fixture until Shrey's vision adapter lands."""

    def analyze(
        self,
        schema: ServiceSchema,
        *,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> ImageResult:
        from ..tools.image import ImageAnalyzer

        return ImageAnalyzer().analyze(filename, content)
