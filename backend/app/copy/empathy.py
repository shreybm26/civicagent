"""Short, message-aware empathy lines for the grievance chat flow."""

from __future__ import annotations

import re

from ..contracts import ServiceId

_INJURY_WORDS = (
    "hurt",
    "injured",
    "injury",
    "pain",
    "hospital",
    "bleeding",
    "fell",
    "fall",
    "accident",
    "fracture",
)
_VAGUE_HERE = re.compile(r"\b(here|this spot|this place|right here|over here)\b")


def _lower(text: str) -> str:
    return text.casefold()


def _mentions_injury(lower: str) -> bool:
    return any(word in lower for word in _INJURY_WORDS)


def _mentions_pothole(lower: str) -> bool:
    return "pothole" in lower or "pot hole" in lower or "pot-hole" in lower


def _needs_exact_spot(lower: str) -> bool:
    return bool(_VAGUE_HERE.search(lower))


def empathetic_location_prompt(service_id: ServiceId, citizen_text: str) -> str:
    """Return a crisp location follow-up that reflects what the citizen said."""

    text = citizen_text.strip()
    lower = _lower(text)

    if _mentions_injury(lower):
        if _needs_exact_spot(lower):
            return "Sorry you got hurt — please share the exact spot or a nearby landmark."
        if service_id == "road_issue" and _mentions_pothole(lower):
            return "Sorry you got hurt on that pothole — where exactly is it?"
        return "Sorry you got hurt — where exactly did this happen?"

    if service_id == "road_issue":
        if _mentions_pothole(lower):
            if _needs_exact_spot(lower):
                return "Sorry about the pothole — please share the exact spot or a nearby landmark."
            if "my street" in lower or "on my street" in lower:
                return "Sorry about the pothole on your street — where exactly is it?"
            return "Sorry about the pothole — where is it?"
        if any(word in lower for word in ("damage", "broken", "crack", "cracked")):
            return "Sorry about the road damage — where is it?"
        return "Sorry about the road issue — where is it happening?"

    if service_id == "garbage_issue":
        if any(phrase in lower for phrase in ("not been collected", "hasn't been collected", "not collected", "not picked")):
            return "Sorry your garbage hasn't been collected — which area is this?"
        if "my area" in lower or "in my area" in lower:
            return "Sorry about the garbage in your area — where exactly?"
        if any(word in lower for word in ("pile", "dump", "overflow", "smell")):
            return "Sorry about the garbage pile — where is it?"
        return "Sorry about the garbage issue — where is it?"

    if service_id == "streetlight_issue":
        if any(phrase in lower for phrase in ("my house", "outside my house", "outside my home", "near my house")):
            if any(word in lower for word in ("week", "days", "off", "out", "dark")):
                return "Sorry the streetlight outside your home has been out — where is it?"
            return "Sorry about the streetlight outside your home — where is it?"
        if any(word in lower for word in ("off", "out", "dark", "not working", "broken")):
            return "Sorry the streetlight has been off — where is it?"
        return "Sorry about the streetlight — where is it?"

    if service_id == "water_issue":
        if "my building" in lower or "near my building" in lower:
            return "Sorry about the leak near your building — where exactly?"
        if "my street" in lower or "on my street" in lower:
            return "Sorry about the leak on your street — where exactly?"
        return "Sorry about the water leak — where is it?"

    if service_id == "sanitation_issue":
        if "neighbourhood" in lower or "neighborhood" in lower or "my area" in lower:
            return "Sorry about the sanitation issue in your neighbourhood — where is it?"
        if any(word in lower for word in ("sewage", "drain", "smell", "overflow")):
            return "Sorry about that — where is the sanitation issue?"
        return "Sorry about the sanitation issue — where is it?"

    return "Sorry about that — where is it happening?"
