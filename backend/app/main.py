from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.provider import GeminiProvider

app = FastAPI(title="CivicAgent API", version="0.1.0")
sessions = {}
provider = GeminiProvider()

SERVICES = {
    "road_issue": {"name": "Road / Pothole Complaint", "department": "Roads & Infrastructure", "fields": ["location", "description", "severity"]},
    "streetlight_issue": {"name": "Streetlight Complaint", "department": "Electrical Services", "fields": ["location", "description", "duration"]},
}

class MessageIn(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("message cannot be empty")
        return value

def snapshot(session):
    service = SERVICES.get(session.get("service_id"))
    fields = [{"id": key, "value": session["fields"].get(key), "required": key in service["fields"]} for key in service["fields"]] if service else []
    return {"session_id": session["id"], "state": session["state"], "service": service, "fields": fields, "review_ready": all(f["value"] for f in fields), "receipt": session.get("receipt")}

def process(session, text):
    lower = text.lower()
    if not session.get("service_id"):
        candidate = provider.classify(text, SERVICES)
        fallback = "streetlight_issue" if "streetlight" in lower or "light" in lower else "road_issue" if any(word in lower for word in ("pothole", "road", "street", "pavement")) else None
        if not candidate.service_id and not fallback:
            session["state"] = "idle"
            return "I can currently help with potholes and streetlights. Which issue would you like to report?"
        session["service_id"] = candidate.service_id or fallback
        session["fields"]["description"] = text
        session["state"] = "collecting"
        return "I can help report this. Where exactly is the issue?"
    service = SERVICES[session["service_id"]]
    missing = [f for f in service["fields"] if not session["fields"].get(f)]
    if "location" in missing:
        session["fields"]["location"] = text
        return "Thanks. What is the severity or duration of the issue?" if session["service_id"] == "road_issue" else "Thanks. How long has the streetlight been off?"
    if session["service_id"] == "road_issue" and "severity" in missing:
        session["fields"]["severity"] = "high" if any(x in lower for x in ["huge", "danger", "fell"]) else "medium"
    elif session["service_id"] == "streetlight_issue" and "duration" in missing:
        session["fields"]["duration"] = text
    session["state"] = "reviewing" if all(session["fields"].get(f) for f in service["fields"]) else "collecting"
    return "Please review the details below and confirm submission." if session["state"] == "reviewing" else "I still need one more detail."

@app.get("/health")
def health():
    return {"status": "ok", "gemini": {"configured": bool(GEMINI_API_KEY), "model": GEMINI_MODEL}}

@app.post("/api/session")
def create_session():
    sid = str(uuid4()); sessions[sid] = {"id": sid, "state": "idle", "fields": {}}
    return snapshot(sessions[sid])

@app.post("/api/session/{sid}/message")
def message(sid: str, body: MessageIn):
    session = sessions.get(sid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    reply = process(session, body.message)
    result = snapshot(session); result["message"] = reply; return result

@app.post("/api/session/{sid}/confirm")
def confirm(sid: str):
    session = sessions.get(sid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["state"] != "reviewing": return {"error": "Complete required fields before confirming"}
    session["state"] = "completed"; session["receipt"] = {"reference": f"CIV-{sid[:8].upper()}", "status": "Received"}
    return snapshot(session)
