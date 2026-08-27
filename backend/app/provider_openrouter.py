"""OpenRouter vision client for civic image analysis only.

Router and collector stay on Gemini (or deterministic mock). This module never
logs the API key.
"""

from __future__ import annotations

import base64
import json
import logging
from typing import Any

import httpx

from .provider_gemini import _parse_json_object

logger = logging.getLogger("civicagent.openrouter")

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_URL = OPENROUTER_CHAT_URL


class OpenRouterClient:
    """Duck-types the GeminiClient.generate_image_json surface used by GeminiImageAnalyzer."""

    def __init__(self, api_key: str, model: str, timeout: float = 120.0) -> None:
        self._api_key = api_key
        self._model = model.strip() or "google/gemini-2.5-flash"
        self._timeout = timeout

    def generate_image_json(self, prompt: str, content_type: str, content: bytes) -> dict[str, Any] | None:
        mime = content_type if content_type.startswith("image/") else "image/jpeg"
        data_url = f"data:{mime};base64,{base64.b64encode(content).decode('ascii')}"
        payload = {
            "model": self._model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = httpx.post(OPENROUTER_CHAT_URL, headers=headers, json=payload, timeout=self._timeout)
            response.raise_for_status()
            body = response.json()
            text = (
                body.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            if isinstance(text, list):
                text = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part) for part in text
                )
            parsed = _parse_json_object(str(text or ""))
            if not isinstance(parsed, dict):
                logger.warning("openrouter_image_fallback error_type=MissingJsonObject")
                return None
            return parsed
        except httpx.HTTPStatusError as exc:
            logger.warning("openrouter_image_fallback http_status=%s", exc.response.status_code)
            return None
        except (httpx.RequestError, httpx.TimeoutException, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            logger.warning("openrouter_image_fallback error_type=%s", type(exc).__name__)
            return None
