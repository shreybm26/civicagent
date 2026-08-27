from fastapi.testclient import TestClient

from app.main import FRONTEND_DIST, app


client = TestClient(app)


def test_health_exposes_safe_runtime_metadata() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "mock"
    assert payload["schemas"] == 5
    assert payload["tracking_store"] in {"sqlite", "supabase"}
    assert payload["mail_configured"] in {True, False}
    assert payload["mail_backend"] in {"sendgrid", "smtp", "resend", "none"}
    assert "GEMINI_API_KEY" not in response.text
    assert "SUPABASE_SERVICE_ROLE_KEY" not in response.text


def test_create_message_and_reset_use_typed_shape() -> None:
    created = client.post("/api/session")
    assert created.status_code == 200
    session = created.json()
    assert session["state"] == "IDLE"
    assert session["receipt"] is None
    assert session["confirmation"] == {"confirmed": False, "confirmed_at": None}

    message = client.post(
        f"/api/session/{session['session_id']}/message",
        json={"message": "There is a pothole"},
    )
    assert message.status_code == 200
    assert message.json()["state"] == "COLLECTING"
    assert message.json()["service_id"] == "road_issue"
    assert message.json()["agent_message"]

    reset = client.post(f"/api/session/{session['session_id']}/reset")
    assert reset.status_code == 200
    assert reset.json()["state"] == "IDLE"
    assert message.json()["messages"][-1]["role"] == "agent"
    assert message.json()["messages"][-1]["text"] == message.json()["agent_message"]


def test_unknown_session_and_invalid_message_are_safe() -> None:
    unknown = client.post(
        "/api/session/00000000-0000-0000-0000-000000000000/message",
        json={"message": "hello"},
    )
    assert unknown.status_code == 404
    assert unknown.json()["detail"]["code"] == "SESSION_NOT_FOUND"

    created = client.post("/api/session").json()
    invalid = client.post(
        f"/api/session/{created['session_id']}/message",
        json={"message": "   "},
    )
    assert invalid.status_code == 422


def test_frontend_bundle_does_not_shadow_api_routes() -> None:
    health = client.get("/health")
    created = client.post("/api/session")
    assert health.status_code == 200
    assert created.status_code == 200

    index = FRONTEND_DIST / "index.html"
    if not index.is_file():
        return

    page = client.get("/")
    assert page.status_code == 200
    assert "text/html" in page.headers.get("content-type", "")
