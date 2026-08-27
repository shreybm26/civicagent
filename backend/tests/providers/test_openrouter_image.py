"""OpenRouter image-analysis client and port wiring."""

from __future__ import annotations

import base64
import json
import logging
from unittest.mock import Mock, patch

import httpx

from app.config import Settings
from app.integration_adapters import ImageAnalyzerAdapter, SchemaCollectorAdapter, SchemaRouterAdapter
from app.provider_gemini import GeminiBackedCollector, GeminiBackedRouter, GeminiImageAnalyzer, build_workflow_ports
from app.provider_openrouter import OPENROUTER_CHAT_URL, OpenRouterClient
from app.workflow.schema import mock_service_schemas

SECRET_KEY = "test-openrouter-secret-key-do-not-log"


def _ok_analysis_json() -> str:
    return json.dumps(
        {
            "relevant": True,
            "relevance_confidence": 0.95,
            "reason": "Pothole visible on asphalt.",
            "summary": "Large pothole near curb.",
            "details": [
                {
                    "label": "Severity",
                    "value": "high",
                    "confidence": 0.9,
                    "reason": "Wide deep cavity",
                }
            ],
            "candidates": [
                {
                    "field_id": "severity",
                    "value": "high",
                    "confidence": 0.9,
                    "reason": "Wide deep cavity",
                }
            ],
        }
    )


def _mock_response(*, status_code: int = 200, content: str | None = None) -> Mock:
    response = Mock(spec=httpx.Response)
    response.status_code = status_code
    response.raise_for_status = Mock()
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error",
            request=Mock(),
            response=response,
        )
    body = content if content is not None else _ok_analysis_json()
    response.json.return_value = {
        "choices": [{"message": {"content": body}}],
    }
    return response


def test_openrouter_request_url_model_headers_and_data_url_image() -> None:
    client = OpenRouterClient(SECRET_KEY, "google/gemini-2.5-flash", timeout=30.0)
    image_bytes = b"fake-jpeg-bytes"
    captured: dict[str, object] = {}

    def fake_post(url, *, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return _mock_response()

    with patch("app.provider_openrouter.httpx.post", side_effect=fake_post):
        parsed = client.generate_image_json("analyze this", "image/jpeg", image_bytes)

    assert parsed is not None
    assert parsed["relevant"] is True
    assert captured["url"] == OPENROUTER_CHAT_URL
    assert captured["timeout"] == 30.0
    assert captured["headers"] == {
        "Authorization": f"Bearer {SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = captured["json"]
    assert isinstance(payload, dict)
    assert payload["model"] == "google/gemini-2.5-flash"
    assert payload["response_format"] == {"type": "json_object"}
    content = payload["messages"][0]["content"]
    assert content[0] == {"type": "text", "text": "analyze this"}
    expected_url = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('ascii')}"
    assert content[1] == {"type": "image_url", "image_url": {"url": expected_url}}


def test_openrouter_parses_fenced_json_like_gemini() -> None:
    client = OpenRouterClient(SECRET_KEY, "google/gemini-2.5-flash")
    fenced = "```json\n" + _ok_analysis_json() + "\n```"
    with patch("app.provider_openrouter.httpx.post", return_value=_mock_response(content=fenced)):
        parsed = client.generate_image_json("prompt", "image/png", b"png")
    assert parsed is not None
    assert parsed["candidates"][0]["field_id"] == "severity"


def test_openrouter_401_timeout_and_malformed_fall_back_to_none(caplog) -> None:
    client = OpenRouterClient(SECRET_KEY, "google/gemini-2.5-flash")

    with patch("app.provider_openrouter.httpx.post", return_value=_mock_response(status_code=401)):
        with caplog.at_level(logging.WARNING, logger="civicagent.openrouter"):
            assert client.generate_image_json("p", "image/jpeg", b"x") is None
        assert SECRET_KEY not in caplog.text
        assert "401" in caplog.text

    with patch(
        "app.provider_openrouter.httpx.post",
        side_effect=httpx.TimeoutException("timed out"),
    ):
        with caplog.at_level(logging.WARNING, logger="civicagent.openrouter"):
            assert client.generate_image_json("p", "image/jpeg", b"x") is None
        assert SECRET_KEY not in caplog.text
        assert "TimeoutException" in caplog.text

    with patch(
        "app.provider_openrouter.httpx.post",
        return_value=_mock_response(content="not-json-at-all"),
    ):
        with caplog.at_level(logging.WARNING, logger="civicagent.openrouter"):
            assert client.generate_image_json("p", "image/jpeg", b"x") is None
        assert SECRET_KEY not in caplog.text


def test_image_analyzer_maps_openrouter_json_candidates() -> None:
    schema = mock_service_schemas()["road_issue"]
    vision = Mock()
    vision.generate_image_json.return_value = json.loads(_ok_analysis_json())
    analyzer = GeminiImageAnalyzer(vision, ImageAnalyzerAdapter(), threshold=0.7)
    result = analyzer.analyze(
        schema,
        filename="pothole.jpg",
        content_type="image/jpeg",
        content=b"bytes",
    )
    assert result.relevant is True
    assert len(result.candidates) == 1
    assert result.candidates[0].field_id == "severity"
    assert result.candidates[0].value == "high"
    assert result.candidates[0].source == "photo"


def test_image_analyzer_falls_back_when_openrouter_returns_none() -> None:
    schema = mock_service_schemas()["road_issue"]
    vision = Mock()
    vision.generate_image_json.return_value = None
    analyzer = GeminiImageAnalyzer(vision, ImageAnalyzerAdapter(), threshold=0.7)
    result = analyzer.analyze(
        schema,
        filename="pothole.jpg",
        content_type="image/jpeg",
        content=b"bytes",
    )
    assert result.reason == "The image was stored, but automated analysis is unavailable."


def test_build_workflow_ports_uses_openrouter_for_image_only() -> None:
    settings = Settings(
        provider_mode="gemini",
        gemini_api_key="gemini-key",
        gemini_model="gemini-2.5-flash",
        openrouter_api_key=SECRET_KEY,
        openrouter_model="google/gemini-2.5-flash",
    )
    _schemas, router, collector, image = build_workflow_ports(settings)
    assert isinstance(router, GeminiBackedRouter)
    assert isinstance(collector, GeminiBackedCollector)
    assert isinstance(image, GeminiImageAnalyzer)
    assert isinstance(image._client, OpenRouterClient)
    assert image._client._model == "google/gemini-2.5-flash"
    assert image._client._api_key == SECRET_KEY


def test_build_workflow_ports_uses_gemini_image_when_openrouter_absent() -> None:
    settings = Settings(
        provider_mode="gemini",
        gemini_api_key="gemini-key",
        gemini_model="gemini-2.5-flash",
        openrouter_api_key="",
    )
    _schemas, router, collector, image = build_workflow_ports(settings)
    assert isinstance(router, GeminiBackedRouter)
    assert isinstance(collector, GeminiBackedCollector)
    assert isinstance(image, GeminiImageAnalyzer)
    assert not isinstance(image._client, OpenRouterClient)


def test_build_workflow_ports_mock_without_keys() -> None:
    settings = Settings(provider_mode="mock", gemini_api_key="", openrouter_api_key="")
    _schemas, router, collector, image = build_workflow_ports(settings)
    assert isinstance(router, SchemaRouterAdapter)
    assert isinstance(collector, SchemaCollectorAdapter)
    assert isinstance(image, ImageAnalyzerAdapter)
