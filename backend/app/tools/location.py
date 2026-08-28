"""Location resolver: curated Hyderabad aliases, then bounded OpenStreetMap search.

Typed places must not depend on an LLM inventing coordinates. All locations in this
GHMC prototype are restricted to the Hyderabad metropolitan area.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import re
from typing import Any

import httpx

from ..contracts import LocationResult

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_USER_AGENT = (
    "CivicAgent/1.0 (civic grievance prototype; https://github.com/shreybm26/civicagent)"
)

GeocodeHits = list[dict[str, Any]]
GeocodeFn = Callable[[str], GeocodeHits]

VAGUE_QUERIES = {
    "near my house",
    "my house",
    "near home",
    "home",
    "somewhere nearby",
    "here",
    "nearby",
}

HYDERABAD_BOUNDS = {
    "min_lat": 17.25,
    "max_lat": 17.65,
    "min_lng": 78.20,
    "max_lng": 78.65,
}

OUTSIDE_SERVICE_CITIES = (
    "bengaluru",
    "bangalore",
    "mumbai",
    "delhi",
    "new delhi",
    "chennai",
    "kolkata",
    "pune",
    "ahmedabad",
    "jaipur",
    "lucknow",
    "kochi",
    "mysuru",
    "mysore",
    "gurgaon",
    "gurugram",
    "noida",
    "chandigarh",
    "koramangala",
    "koramangla",
)

HYDERABAD_MARKERS = (
    "hyderabad",
    "secunderabad",
    "telangana",
)


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
    CuratedLocation("JNTU Metro Station", "Kukatpally", "Hyderabad", "500085", 17.4933, 78.3914, ("jntu", "jntu metro", "near jntu", "kukatpally metro", "जेएनटीयू", "जेएनटीयू मेट्रो")),
    CuratedLocation("KPHB Metro Station", "Kukatpally", "Hyderabad", "500072", 17.4841, 78.3986, ("kphb", "kphb metro", "kphb colony")),
    CuratedLocation("Miyapur Metro Station", "Miyapur", "Hyderabad", "500049", 17.4968, 78.3570, ("miyapur", "miyapur metro")),
    CuratedLocation("Hitech City Metro Station", "Madhapur", "Hyderabad", "500081", 17.4474, 78.3762, ("hitech city", "hitech metro", "madhapur metro", "हाइटेक", "हाइटेक सिटी")),
    CuratedLocation("Charminar", "Old City", "Hyderabad", "500002", 17.3616, 78.4747, ("charminar", "old city", "चारमीनार")),
    CuratedLocation("Secunderabad Railway Station", "Secunderabad", "Hyderabad", "500003", 17.4334, 78.5013, ("secunderabad station", "secunderabad railway", "सिकंदराबाद")),
    CuratedLocation("Ameerpet Metro Station", "Ameerpet", "Hyderabad", "500016", 17.4375, 78.4483, ("ameerpet", "ameerpet metro", "अमीरपेट")),
    CuratedLocation("Gachibowli Stadium", "Gachibowli", "Hyderabad", "500032", 17.4401, 78.3489, ("gachibowli", "gachibowli stadium")),
    CuratedLocation("LB Nagar Metro Station", "LB Nagar", "Hyderabad", "500074", 17.3457, 78.5522, ("lb nagar", "lb nagar metro")),
    CuratedLocation("Tank Bund", "Hussain Sagar", "Hyderabad", "500080", 17.4239, 78.4738, ("tank bund", "hussain sagar")),
    CuratedLocation("Nampally Station", "Nampally", "Hyderabad", "500001", 17.3924, 78.4660, ("nampally", "nampally station")),
    CuratedLocation("Kukatpally Housing Board", "Kukatpally", "Hyderabad", "500072", 17.4848, 78.4138, ("kukatpally housing board", "kphb housing board")),
)


FILLER_PREFIX = re.compile(
    r"^(?:my\s+area\s+is|my\s+location\s+is|the\s+area\s+is|the\s+location\s+is|"
    r"i\s+live\s+in|i\s+am\s+in|i['’]m\s+in|it\s+is\s+in|it['’]s\s+in|"
    r"the\s+issue\s+is\s+(?:in|at)|issue\s+is\s+(?:in|at)|"
    r"located\s+(?:in|at)|area\s+is|location\s+is|"
    r"near|around|at|in)\s+",
    re.IGNORECASE,
)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\u0900-\u097f ]", " ", value.casefold())).strip()


def outside_service_area_message() -> str:
    return "This demo only covers Hyderabad (GHMC). Share a Hyderabad landmark or pin it on the map."


def is_within_hyderabad_bounds(lat: float, lng: float) -> bool:
    return (
        HYDERABAD_BOUNDS["min_lat"] <= lat <= HYDERABAD_BOUNDS["max_lat"]
        and HYDERABAD_BOUNDS["min_lng"] <= lng <= HYDERABAD_BOUNDS["max_lng"]
    )


def mentions_outside_service_area(text: str) -> bool:
    normalized = _normalize(text)
    if any(marker in normalized for marker in HYDERABAD_MARKERS):
        return False
    return any(city in normalized for city in OUTSIDE_SERVICE_CITIES)


def address_looks_hyderabad(address: str) -> bool:
    normalized = _normalize(address)
    return "hyderabad" in normalized or "secunderabad" in normalized


def validate_hyderabad_coordinates(lat: float, lng: float) -> bool:
    return is_within_hyderabad_bounds(lat, lng)


def strip_location_filler(text: str) -> str:
    """Drop chat phrasing so geocoders see a place name, not 'my area is …'."""

    value = text.strip().strip(" ,")
    original = value
    for _ in range(4):
        next_value = FILLER_PREFIX.sub("", value).strip(" ,")
        if next_value == value:
            break
        value = next_value
    return value or original


def _looks_complete(text: str) -> bool:
    cleaned = strip_location_filler(text)
    if len([part for part in cleaned.split(",") if part.strip()]) >= 2:
        return True
    normalized = _normalize(cleaned)
    return any(marker in normalized for marker in HYDERABAD_MARKERS) or any(
        city in normalized for city in OUTSIDE_SERVICE_CITIES
    )


def _with_hyderabad_context(query: str) -> str:
    cleaned = query.strip(" ,")
    if not cleaned:
        return cleaned
    normalized = _normalize(cleaned)
    if _looks_complete(cleaned):
        return cleaned
    if any(marker in normalized for marker in HYDERABAD_MARKERS):
        return cleaned
    return f"{cleaned}, Hyderabad, Telangana"


def compose_location_query(text: str, prior_query: str | None = None) -> str:
    """Build the best single search string for a typed place."""

    return candidate_location_queries(text, prior_query)[0] if text.strip() else ""


def candidate_location_queries(text: str, prior_query: str | None = None) -> list[str]:
    """Try the citizen's latest place first; only reuse a failed attempt as extra context."""

    cleaned = strip_location_filler(text)
    prior = strip_location_filler(prior_query) if prior_query else ""
    ordered: list[str] = []

    def add(query: str) -> None:
        query = query.strip(" ,")
        if not query:
            return
        if any(_normalize(query) == _normalize(existing) for existing in ordered):
            return
        ordered.append(query)

    if prior and not _looks_complete(cleaned) and not mentions_outside_service_area(prior):
        add(f"{cleaned}, {prior}")
    add(_with_hyderabad_context(cleaned))
    add(cleaned)
    return ordered or [text.strip()]


def _short_address(display_name: str) -> str:
    parts = [part.strip() for part in display_name.split(",") if part.strip()]
    return ", ".join(parts[:5]) if parts else display_name


def nominatim_search(query: str) -> GeocodeHits:
    """Forward-geocode within the Hyderabad metropolitan viewbox."""

    try:
        response = httpx.get(
            NOMINATIM_SEARCH_URL,
            params={
                "format": "jsonv2",
                "q": query,
                "countrycodes": "in",
                "limit": "5",
                "addressdetails": "1",
                "viewbox": "78.20,17.65,78.65,17.25",
                "bounded": "1",
            },
            headers={
                "User-Agent": NOMINATIM_USER_AGENT,
                "Accept": "application/json",
                "Accept-Language": "en-IN,en",
            },
            timeout=8.0,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError, TypeError):
        return []
    return payload if isinstance(payload, list) else []


def _hit_is_hyderabad(lat: float, lng: float, address: str) -> bool:
    if is_within_hyderabad_bounds(lat, lng):
        return True
    return address_looks_hyderabad(address)


def _geocode_hits_to_result(query: str, hits: GeocodeHits) -> LocationResult:
    usable: list[tuple[float, float, str]] = []
    seen: set[tuple[float, float]] = set()
    for hit in hits:
        try:
            lat = float(hit["lat"])
            lng = float(hit["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        name = hit.get("display_name")
        if not isinstance(name, str) or not name.strip():
            continue
        address = _short_address(name)
        if not _hit_is_hyderabad(lat, lng, address):
            continue
        key = (round(lat, 3), round(lng, 3))
        if key in seen:
            continue
        seen.add(key)
        usable.append((lat, lng, address))

    if not usable:
        return LocationResult(
            query=query,
            needs_clarification=True,
            message=outside_service_area_message(),
        )

    lat, lng, address = usable[0]
    return LocationResult(
        query=query,
        address=address,
        lat=lat,
        lng=lng,
        confidence=0.86,
        source="geocoded",
        message=f"Is this the spot — {address}?",
    )


def _curated_match(query: str) -> LocationResult | None:
    normalized = _normalize(query)
    matches = [
        location
        for location in CURATED_LOCATIONS
        if any(alias in normalized or normalized in alias for alias in map(_normalize, location.aliases))
    ]
    unique = {location.address: location for location in matches}
    if len(unique) > 1:
        names = ", ".join(location.name for location in unique.values())
        return LocationResult(
            query=query,
            needs_clarification=True,
            message=f"A few matches came up ({names}). Which one?",
        )
    if len(unique) == 1:
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
    return None


def resolve_location(
    text: str,
    *,
    prior_query: str | None = None,
    geocode: GeocodeFn | None = None,
) -> LocationResult:
    raw = text.strip()
    if not raw:
        return LocationResult(query="unknown", needs_clarification=True, message="Share a nearby landmark or area.")

    cleaned = strip_location_filler(raw)
    if _normalize(raw) in VAGUE_QUERIES or _normalize(cleaned) in VAGUE_QUERIES:
        return LocationResult(query=raw, needs_clarification=True, message="Please share a landmark, area, or street.")

    if mentions_outside_service_area(cleaned) or (prior_query and mentions_outside_service_area(prior_query)):
        return LocationResult(
            query=raw,
            needs_clarification=True,
            message=outside_service_area_message(),
        )

    for candidate in (cleaned, raw):
        curated = _curated_match(candidate)
        if curated is not None:
            return curated

    if geocode is None:
        geocode = nominatim_search
    last: LocationResult | None = None
    for query in candidate_location_queries(raw, prior_query):
        last = _geocode_hits_to_result(query, geocode(query))
        if last.address:
            return last
    return last or LocationResult(
        query=cleaned or raw,
        needs_clarification=True,
        message=outside_service_area_message(),
    )
