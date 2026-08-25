from fastapi.testclient import TestClient

from app.main import app, sessions

client = TestClient(app)


def new_session():
    sessions.clear()
    return client.post("/api/session").json()["session_id"]


def test_unsupported_issue_stays_idle():
    sid = new_session()
    result = client.post(f"/api/session/{sid}/message", json={"message": "My neighbor is playing loud music"}).json()
    assert result["state"] == "idle"
    assert result["service"] is None


def test_pothole_journey_requires_confirmation_and_returns_receipt():
    sid = new_session()
    first = client.post(f"/api/session/{sid}/message", json={"message": "There is a dangerous pothole on the road"}).json()
    assert first["service"]["name"] == "Road / Pothole Complaint"
    client.post(f"/api/session/{sid}/message", json={"message": "Near JNTU Metro, Kukatpally"})
    review = client.post(f"/api/session/{sid}/message", json={"message": "It is huge and dangerous"}).json()
    assert review["state"] == "reviewing"
    assert review["review_ready"] is True
    completed = client.post(f"/api/session/{sid}/confirm").json()
    assert completed["state"] == "completed"
    assert completed["receipt"]["reference"].startswith("CIV-")


def test_confirmation_is_gated():
    sid = new_session()
    result = client.post(f"/api/session/{sid}/confirm").json()
    assert result["error"] == "Complete required fields before confirming"


def test_missing_session_returns_404():
    assert client.post("/api/session/missing/message", json={"message": "pothole"}).status_code == 404

