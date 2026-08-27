"""Optional Gemini proposals with deterministic schema fallback.

The workflow still validates, transitions, and gates submission. Gemini may only
classify or extract; it cannot confirm or submit.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from .config import Settings
from .contracts import Candidate, RouterResult, ServiceId
from .integration_adapters import ImageAnalyzerAdapter, SchemaCollectorAdapter, SchemaRouterAdapter
from .schemas.registry import SchemaRegistry
from .workflow.schema import SchemaField, ServiceSchema

logger = logging.getLogger("civicagent.gemini")

KNOWN_SERVICES: tuple[ServiceId, ...] = (
    "road_issue",
    "garbage_issue",
    "streetlight_issue",
    "water_issue",
    "sanitation_issue",
)


class GeminiClient:
    def __init__(self, api_key: str, model: str, timeout: float = 8.0) -> None:
        self._api_key = api_key
        self._model = model.strip() or "gemini-flash-latest"
        self._timeout = timeout

    def generate_json(self, prompt: str) -> dict[str, Any] | None:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
        }
        try:
            response = httpx.post(
                url,
                params={"key": self._api_key},
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
            text = (
                response.json()
                .get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            logger.info("gemini_fallback", extra={"civic_event": {"event": "provider_timeout"}})
            return None


class GeminiBackedRouter:
    def __init__(self, client: GeminiClient, fallback: SchemaRouterAdapter) -> None:
        self._client = client
        self._fallback = fallback

    def classify(self, message: str, schemas: dict[ServiceId, ServiceSchema]) -> RouterResult:
        prompt = (
            "Classify this civic complaint into exactly one service_id. "
            f"Allowed ids: {list(KNOWN_SERVICES)}. "
            'Return JSON {"service_id": string|null, "confidence": number, "needs_clarification": boolean}. '
            f"Citizen message: {message[:1000]}"
        )
        data = self._client.generate_json(prompt)
        service_id = data.get("service_id") if data else None
        confidence = float((data or {}).get("confidence") or 0.0)
        if service_id in schemas and confidence >= 0.7:
            return RouterResult(
                service_id=service_id,
                confidence=min(confidence, 1.0),
                needs_clarification=False,
                message=f"I identified this as a {schemas[service_id].service_name.lower()}.",
            )
        return self._fallback.classify(message, schemas)


class GeminiBackedCollector:
    def __init__(self, client: GeminiClient, fallback: SchemaCollectorAdapter) -> None:
        self._client = client
        self._fallback = fallback

    def collect(self, field: SchemaField, message: str) -> Candidate | None:
        local = self._fallback.collect(field, message)
        if local is not None:
            return local
        options = list(field.options) if field.options else []
        prompt = (
            f'Extract a value for field "{field.id}" of type "{field.field_type}". '
            f"Allowed options: {options or 'any short text'}. "
            'Return JSON {"value": string|null, "confidence": number}. '
            "If the message does not contain this field, value must be null. "
            f"Citizen message: {message[:1000]}"
        )
        data = self._client.generate_json(prompt)
        value = data.get("value") if data else None
        if value in (None, ""):
            return None
        if options and str(value).lower() not in {option.lower() for option in options}:
            return None
        if options:
            value = str(value).lower()
        confidence = float(data.get("confidence") or 0.75)
        return Candidate(
            field_id=field.id,
            value=value,
            source="conversation",
            confidence=min(max(confidence, 0.0), 1.0),
            reason="Suggested from the citizen’s message",
        )


def build_workflow_ports(settings: Settings):
    """Return schemas and ports. Gemini is used only when explicitly enabled."""

    from .integration_adapters import RegistrySchemaAdapter

    schemas = RegistrySchemaAdapter(SchemaRegistry()).as_graph_schemas()
    router = SchemaRouterAdapter(schemas)
    collector = SchemaCollectorAdapter()
    image = ImageAnalyzerAdapter()
    enabled = settings.provider_mode in {"gemini", "llm", "auto"} and bool(settings.gemini_api_key)
    if enabled:
        client = GeminiClient(settings.gemini_api_key, settings.gemini_model)
        router = GeminiBackedRouter(client, router)
        collector = GeminiBackedCollector(client, collector)
    return schemas, router, collector, image
