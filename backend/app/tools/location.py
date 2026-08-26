"""Curated Hyderabad location resolver with deterministic fuzzy aliases."""

from __future__ import annotations

from dataclasses import dataclass
import re

from ..contracts import LocationResult


@dataclass(frozen=True)
class CuratedLocation:
    name: str
    area: str
    city: str
    pin: str
    lat: float
    lng: float
    aliases: tuple[str, ...]

    @property
    def address(self) -> str:
        return f"{self.name}, {self.area}, {self.city} {self.pin}"


CURATED_LOCATIONS: tuple[CuratedLocation, ...] = (
    CuratedLocation("JNTU Metro Station", "Kukatpally", "Hyderabad", "500085", 17.4933, 78.3914, ("jntu", "jntu metro", "near jntu", "kukatpally metro")),
    CuratedLocation("KPHB Metro Station", "Kukatpally", "Hyderabad", "500072", 17.4841, 78.3986, ("kphb", "kphb metro", "kphb colony")),
    CuratedLocation("Miyapur Metro Station", "Miyapur", "Hyderabad", "500049", 17.4968, 78.3570, ("miyapur", "miyapur metro")),
    CuratedLocation("Hitech City Metro Station", "Madhapur", "Hyderabad", "500081", 17.4474, 78.3762, ("hitech city", "hitech metro", "madhapur metro")),
    CuratedLocation("Charminar", "Old City", "Hyderabad", "500002", 17.3616, 78.4747, ("charminar", "old city")),
    CuratedLocation("Secunderabad Railway Station", "Secunderabad", "Hyderabad", "500003", 17.4334, 78.5013, ("secunderabad station", "secunderabad railway")),
    CuratedLocation("Ameerpet Metro Station", "Ameerpet", "Hyderabad", "500016", 17.4375, 78.4483, ("ameerpet", "ameerpet metro")),
    CuratedLocation("Gachibowli Stadium", "Gachibowli", "Hyderabad", "500032", 17.4401, 78.3489, ("gachibowli", "gachibowli stadium")),
    CuratedLocation("LB Nagar Metro Station", "LB Nagar", "Hyderabad", "500074", 17.3457, 78.5522, ("lb nagar", "lb nagar metro")),
    CuratedLocation("Tank Bund", "Hussain Sagar", "Hyderabad", "500080", 17.4239, 78.4738, ("tank bund", "hussain sagar")),
    CuratedLocation("Nampally Station", "Nampally", "Hyderabad", "500001", 17.3924, 78.4660, ("nampally", "nampally station")),
    CuratedLocation("Kukatpally Housing Board", "Kukatpally", "Hyderabad", "500072", 17.4848, 78.4138, ("kukatpally housing board", "kphb housing board")),
)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", value.casefold())).strip()


def resolve_location(text: str) -> LocationResult:
    query = text.strip()
    if not query:
        return LocationResult(query="unknown", needs_clarification=True, message="Please tell me a nearby landmark or area.")

    normalized = _normalize(query)
    if normalized in {"near my house", "my house", "near home", "home", "somewhere nearby"}:
        return LocationResult(query=query, needs_clarification=True, message="Please provide a recognizable landmark, area, or street.")

    matches = [
        location
        for location in CURATED_LOCATIONS
        if any(alias in normalized or normalized in alias for alias in map(_normalize, location.aliases))
    ]
    unique = {location.address: location for location in matches}
    if len(unique) != 1:
        if len(unique) > 1:
            names = ", ".join(location.name for location in unique.values())
            message = f"I found more than one possible location ({names}). Which one is correct?"
        else:
            message = "I could not match that location yet. Please provide a nearby landmark, area, or street."
        return LocationResult(query=query, needs_clarification=True, message=message)

    location = next(iter(unique.values()))
    return LocationResult(
        query=query,
        address=location.address,
        lat=location.lat,
        lng=location.lng,
        confidence=0.98,
        source="curated_location",
        message=f"I found this location: {location.address}. Is that correct?",
    )
