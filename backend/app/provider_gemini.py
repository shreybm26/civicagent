"""Optional Gemini proposals with deterministic schema fallback.

The workflow still validates, transitions, and gates submission. Gemini may only
classify or extract; it cannot confirm or submit.
"""

from __future__ import annotations

import json
import logging
import base64
import re
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
    def __init__(self, api_key: str, model: str, timeout: float = 120.0) -> None:
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
            parsed = _parse_json_object(text)
            return parsed if isinstance(parsed, dict) else None
        except httpx.HTTPStatusError as exc:
            logger.warning("gemini_fallback http_status=%s", exc.response.status_code)
            return None
        except (httpx.RequestError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            logger.warning("gemini_fallback error_type=%s", type(exc).__name__)
            return None

    def generate_image_json(self, prompt: str, content_type: str, content: bytes) -> dict[str, Any] | None:
        url = "https://generativelanguage.googleapis.com/v1beta/models/" f"{self._model}:generateContent"
        payload = {
            "contents": [{"parts": [
                {"inline_data": {"mime_type": content_type, "data": base64.b64encode(content).decode("ascii")}},
                {"text": prompt},
            ]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
        }
        try:
            response = httpx.post(url, params={"key": self._api_key}, json=payload, timeout=self._timeout)
            response.raise_for_status()
            text = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            parsed = _parse_json_object(text)
            if not isinstance(parsed, dict):
                logger.warning("gemini_image_fallback error_type=MissingJsonObject")
                return None
            return parsed if isinstance(parsed, dict) else None
        except httpx.HTTPStatusError as exc:
            logger.warning("gemini_image_fallback http_status=%s", exc.response.status_code)
            return None
        except (httpx.RequestError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            logger.warning("gemini_image_fallback error_type=%s", type(exc).__name__)
            return None


def _parse_json_object(text: str) -> dict[str, Any] | None:
    """Parse strict JSON or JSON wrapped in a markdown fence/prose."""
    candidate = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, re.IGNORECASE | re.DOTALL)
    if fenced:
        candidate = fenced.group(1)
    else:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start >= 0 and end > start:
            candidate = candidate[start : end + 1]
    parsed = json.loads(candidate)
    return parsed if isinstance(parsed, dict) else None


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
                    message=f"Got it — a {schemas[service_id].service_name.lower()} issue.",
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
            "Set relevant=true only when the image clearly shows this reported civic issue. "
            "If irrelevant, set relevant=false, explain why in reason (what the image shows vs what was needed), "
            "and return no candidates. "
            "When relevant: fill candidates for every image-derivable field you can confidently infer "
            "(including choice fields such as severity, issue_type, or leak_type using only the allowed options). "
            "If a landmark field is listed and a readable place name, mall, metro station, junction, or building "
            "name is visible, you MUST also return a landmark candidate with that exact readable text "
            "(for example field_id=landmark, value='NEXUS FORUM'). Do not leave landmarks only in the summary. "
            "summary must be a short civic-report description of the problem only — what is wrong, how severe it looks, "
            "and useful place landmarks (metro/station/building names that help locate the issue). "
            "Do NOT include advertising text, phone numbers, marketing slogans, or unrelated signage. "
            "details must also stay limited to civic-issue facts (damage, waste, leak, hazard, landmark for location).",
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
                label = str(raw["label"])
                value = str(raw["value"])
                if _noise_detail(label, value):
                    continue
                details.append(ImageDetail(label=label, value=value, confidence=confidence, reason=raw.get("reason")))
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
                if field.id == "landmark" and _noise_detail("landmark", str(value)):
                    continue
                candidates.append(Candidate(field_id=field.id, value=str(value).lower() if field.options else value, source="photo", confidence=confidence, reason=raw.get("reason")))
            # If the model described a place in summary/details but omitted the landmark candidate, recover it.
            if "landmark" in fields and not any(item.field_id == "landmark" for item in candidates):
                recovered = _recover_landmark(
                    summary=str(data.get("summary") or ""),
                    details=details,
                    reason=str(data.get("reason") or ""),
                )
                if recovered:
                    candidates.append(
                        Candidate(
                            field_id="landmark",
                            value=recovered,
                            source="photo",
                            confidence=max(relevance_confidence, 0.8),
                            reason="Visible place name recovered from image analysis text",
                        )
                    )
        summary = str(data.get("summary")).strip() if data.get("summary") else None
        if summary and _noise_detail("summary", summary):
            # Keep place names; strip obvious ad sentences if the whole summary is mostly ads.
            summary = _strip_ad_sentences(summary)
        return ImageResult(
            relevant=relevant and relevance_confidence >= self._threshold,
            relevance_confidence=relevance_confidence,
            reason=str(data.get("reason") or "Image analysis completed."),
            summary=summary or None,
            details=details,
            candidates=candidates,
        )


def _recover_landmark(*, summary: str, details: list[ImageDetail], reason: str) -> str | None:
    """Pull a quoted/proper place name out of analysis prose when landmark candidate is missing."""

    import re

    chunks = [summary, reason, *[f"{item.label}: {item.value}" for item in details]]
    blob = " ".join(part for part in chunks if part).strip()
    if not blob:
        return None
    for match in re.finditer(r"['\"]([A-Z][^'\"]{1,80})['\"]", blob):
        candidate = match.group(1).strip(" .,;:")
        if candidate and not _noise_detail("landmark", candidate):
            return candidate
    match = re.search(
        r"(?:in front of|near|beside|outside|next to)\s+(?:the\s+)?['\"]?([A-Z][A-Za-z0-9 .&'/,-]{1,60})",
        blob,
    )
    if match:
        candidate = match.group(1).strip(" .,;:")
        candidate = re.sub(r"\b(building|mall|complex|road|street)\b\.?$", "", candidate, flags=re.I).strip(" .,;:")
        if candidate and not _noise_detail("landmark", candidate):
            return candidate
    return None


def _noise_detail(label: str, value: str) -> bool:
    import re

    blob = f"{label} {value}".lower()
    if "advertise" in blob or "to advertise" in blob:
        return True
    if re.search(r"\b(call|contact|whatsapp)\b", blob) and re.search(r"\d{3,}", blob):
        return True
    if re.search(r"\b\d{3,5}[\s-]?\d{3,5}[\s-]?\d{3,5}\b", blob) and "metro" not in blob:
        return True
    return False


def _strip_ad_sentences(text: str) -> str:
    parts = [part.strip() for part in text.replace("!", ".").split(".") if part.strip()]
    kept = [part for part in parts if not _noise_detail("summary", part)]
    return ". ".join(kept).strip() or text


def _confidence(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return 0.0
    return min(max(parsed, 0.0), 1.0)


def build_workflow_ports(settings: Settings):
    """Return schemas and ports. Gemini is used only when explicitly enabled.

    OpenRouter, when configured, replaces only the image analyzer; router and
    collector remain Gemini-backed (or deterministic mock).
    """

    from .integration_adapters import RegistrySchemaAdapter
    from .provider_openrouter import OpenRouterClient

    schemas = RegistrySchemaAdapter(SchemaRegistry()).as_graph_schemas()
    router = SchemaRouterAdapter(schemas)
    collector = SchemaCollectorAdapter()
    image = ImageAnalyzerAdapter()
    gemini_enabled = settings.provider_mode in {"gemini", "llm", "auto"} and bool(settings.gemini_api_key)
    gemini_client: GeminiClient | None = None
    if gemini_enabled:
        gemini_client = GeminiClient(
            settings.gemini_api_key,
            settings.gemini_model,
            timeout=settings.gemini_timeout_seconds,
        )
        router = GeminiBackedRouter(gemini_client, router)
        collector = GeminiBackedCollector(gemini_client, collector)

    if settings.openrouter_api_key:
        image = GeminiImageAnalyzer(
            OpenRouterClient(
                settings.openrouter_api_key,
                settings.openrouter_model,
                timeout=settings.openrouter_timeout_seconds,
            ),
            image,
            settings.image_confidence_threshold,
        )
    elif gemini_client is not None:
        image = GeminiImageAnalyzer(gemini_client, image, settings.image_confidence_threshold)
    return schemas, router, collector, image
