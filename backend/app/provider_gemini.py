"""Optional Gemini proposals with deterministic schema fallback.

The workflow still validates, transitions, and gates submission. Gemini may only
classify or extract; it cannot confirm or submit.
"""

from __future__ import annotations

import json
import logging
import base64
from typing import Any

import httpx

from .config import Settings
from .contracts import Candidate, ImageDetail, ImageResult, RouterResult, ServiceId
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

    def generate_image_json(self, prompt: str, content_type: str, content: bytes) -> dict[str, Any] | None:
        url = "https://generativelanguage.googleapis.com/v1beta/models/" f"{self._model}:generateContent"
        payload = {
            "contents": [{"parts": [
                {"inlineData": {"mimeType": content_type, "data": base64.b64encode(content).decode("ascii")}},
                {"text": prompt},
            ]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
        }
        try:
            response = httpx.post(url, params={"key": self._api_key}, json=payload, timeout=self._timeout)
            response.raise_for_status()
            text = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            logger.info("gemini_image_fallback", extra={"civic_event": {"event": "image_provider_failure"}})
            return None


class GeminiBackedRouter:
    def __init__(self, client: GeminiClient, fallback: SchemaRouterAdapter) -> None:
        self._client = client
        self._fallback = fallback

    def classify(self, message: str, schemas: dict[ServiceId, ServiceSchema]) -> RouterResult:
        fallback = self._fallback.classify(message, schemas)
        if fallback.service_id and not fallback.needs_clarification:
            return fallback
        try:
            data = self._client.generate_json(
                "Classify this civic complaint into exactly one service_id. "
                f"Allowed ids: {list(KNOWN_SERVICES)}. "
                'Return JSON {"service_id": string|null, "confidence": number, "needs_clarification": boolean}. '
                f"Citizen message: {message[:1000]}"
            )
            service_id = str((data or {}).get("service_id") or "").strip().lower()
            confidence = _confidence((data or {}).get("confidence"))
            if service_id in schemas and confidence >= 0.7:
                return RouterResult(
                    service_id=service_id,  # type: ignore[arg-type]
                    confidence=confidence,
                    needs_clarification=False,
                    message=f"I identified this as a {schemas[service_id].service_name.lower()}.",
                )
        except Exception:
            logger.info("gemini_fallback", extra={"civic_event": {"event": "classify_fallback"}})
        return fallback


class GeminiBackedCollector:
    def __init__(self, client: GeminiClient, fallback: SchemaCollectorAdapter) -> None:
        self._client = client
        self._fallback = fallback

    def collect(self, field: SchemaField, message: str) -> Candidate | None:
        local = self._fallback.collect(field, message)
        if local is not None:
            return local
        try:
            options = list(field.options) if field.options else []
            data = self._client.generate_json(
                f'Extract a value for field "{field.id}" of type "{field.field_type}". '
                f"Allowed options: {options or 'any short text'}. "
                'Return JSON {"value": string|null, "confidence": number}. '
                "If the message does not contain this field, value must be null. "
                f"Citizen message: {message[:1000]}"
            )
            value = (data or {}).get("value")
            if value in (None, ""):
                return None
            if options and str(value).lower() not in {option.lower() for option in options}:
                return None
            if options:
                value = str(value).lower()
            return Candidate(
                field_id=field.id,
                value=value,
                source="conversation",
                confidence=_confidence((data or {}).get("confidence") or 0.75),
                reason="Suggested from the citizen’s message",
            )
        except Exception:
            logger.info("gemini_fallback", extra={"civic_event": {"event": "collect_fallback"}})
            return None


class GeminiImageAnalyzer:
    def __init__(self, client: GeminiClient, fallback: ImageAnalyzerAdapter, threshold: float) -> None:
        self._client = client
        self._fallback = fallback
        self._threshold = threshold

    def analyze(self, schema: ServiceSchema, *, filename: str, content_type: str, content: bytes) -> ImageResult:
        data = self._client.generate_image_json(
            "Analyze only what is visibly present in this civic-issue image. Do not use the filename. "
            f"The reported service is {schema.service_name}. Available image-derivable fields are "
            f"{[{'id': field.id, 'type': field.field_type, 'options': list(field.options)} for field in schema.fields if field.image_derivable]}. "
            'Return JSON with relevant (boolean), relevance_confidence (0..1), reason, summary, '
            'details [{label,value,confidence,reason}], and candidates [{field_id,value,confidence,reason}]. '
            "Return candidates only for facts directly visible in the image. An irrelevant image must return no candidates.",
            content_type,
            content,
        )
        if data is None:
            fallback = self._fallback.analyze(schema=schema, filename=filename, content_type=content_type, content=content)
            return fallback.model_copy(update={"reason": "The image was stored, but automated analysis is unavailable."})
        relevant = bool(data.get("relevant"))
        relevance_confidence = _confidence(data.get("relevance_confidence"))
        details: list[ImageDetail] = []
        candidates: list[Candidate] = []
        if relevant and relevance_confidence >= self._threshold:
            for raw in data.get("details", []):
                confidence = _confidence(raw.get("confidence")) if isinstance(raw, dict) else 0.0
                if confidence < self._threshold or not raw.get("label") or not raw.get("value"):
                    continue
                details.append(ImageDetail(label=str(raw["label"]), value=str(raw["value"]), confidence=confidence, reason=raw.get("reason")))
            fields = {field.id: field for field in schema.fields if field.image_derivable}
            for raw in data.get("candidates", []):
                if not isinstance(raw, dict):
                    continue
                field = fields.get(str(raw.get("field_id")))
                confidence = _confidence(raw.get("confidence"))
                value = raw.get("value")
                if field is None or confidence < self._threshold or value in (None, ""):
                    continue
                if field.options and str(value).lower() not in field.options:
                    continue
                candidates.append(Candidate(field_id=field.id, value=str(value).lower() if field.options else value, source="photo", confidence=confidence, reason=raw.get("reason")))
        return ImageResult(
            relevant=relevant and relevance_confidence >= self._threshold,
            relevance_confidence=relevance_confidence,
            reason=str(data.get("reason") or "Image analysis completed."),
            summary=str(data.get("summary")) if data.get("summary") else None,
            details=details,
            candidates=candidates,
        )


def _confidence(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return 0.0
    return min(max(parsed, 0.0), 1.0)


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
        image = GeminiImageAnalyzer(client, image, settings.image_confidence_threshold)
    return schemas, router, collector, image
