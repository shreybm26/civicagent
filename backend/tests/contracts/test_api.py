from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_exposes_safe_runtime_metadata() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "provider": "mock", "schemas": 5}
    assert "GEMINI_API_KEY" not in response.text


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
    assert message.json()["state"] == "IDLE"
    assert message.json()["agent_message"]

    reset = client.post(f"/api/session/{session['session_id']}/reset")
    assert reset.status_code == 200
    assert reset.json()["state"] == "IDLE"


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
