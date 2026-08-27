"""Contract-level backup demo client. Run with the backend already started."""
import json
import sys
from urllib.request import Request, urlopen

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"

def call(path, method="GET", payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(BASE + path, data=data, method=method, headers={"Content-Type":"application/json"})
    with urlopen(req, timeout=10) as response: return json.loads(response.read())

health = call("/health")
assert health["status"] == "ok"
session = call("/api/session", "POST")
sid = session["session_id"]
call(f"/api/session/{sid}/message", "POST", {"message":"There is a huge pothole near JNTU Metro"})
located = call(f"/api/session/{sid}/location/resolve", "POST", {"text":"near JNTU metro"})
assert located["location"]["source"] == "curated_location"
review = call(f"/api/session/{sid}/message", "POST", {"message":"high"})
assert review["state"] == "REVIEWING"
completed = call(f"/api/session/{sid}/confirm", "POST", {"confirmed":True})
assert completed["state"] == "COMPLETED" and completed["receipt"]["reference"]
assert completed["receipt"]["access_key"]
tracked = call("/api/track", "POST", {"sr_id": completed["receipt"]["reference"], "access_key": completed["receipt"]["access_key"]})
assert tracked["sr_id"] == completed["receipt"]["reference"]
print(f"backup demo passed: {completed['receipt']['reference']}")
