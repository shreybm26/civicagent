import json
import urllib.request
import urllib.error
from dataclasses import dataclass

from app.config import GEMINI_API_KEY, GEMINI_MODEL

@dataclass
class ServiceCandidate:
    service_id: str | None
    confidence: float

class GeminiProvider:
    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL, timeout: float = 8.0):
        self.api_key, self.model, self.timeout = api_key, model, timeout

    def classify(self, text: str, services: dict) -> ServiceCandidate:
        if not self.api_key:
            return ServiceCandidate(None, 0.0)
        allowed = ", ".join(services)
        prompt = ("Classify this civic issue into exactly one allowed service ID. "
                  'Return JSON only: {"service_id": string|null, "confidence": number}. '
                  f"Allowed IDs: {allowed}. Issue: {text}")
        try:
            payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}
            req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "X-goog-api-key": self.api_key}, method="POST")
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                body = json.loads(response.read())
            raw = body["candidates"][0]["content"]["parts"][0]["text"]
            result = json.loads(raw)
            service_id = result.get("service_id") if result.get("service_id") in services else None
            confidence = max(0.0, min(1.0, float(result.get("confidence", 0))))
            return ServiceCandidate(service_id if confidence >= 0.7 else None, confidence)
        except (OSError, KeyError, TypeError, ValueError, urllib.error.URLError):
            return ServiceCandidate(None, 0.0)
