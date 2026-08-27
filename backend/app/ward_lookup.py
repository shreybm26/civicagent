"""Point-in-polygon lookup for GHMC ward boundaries."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from shapely.geometry import Point, shape
from shapely.strtree import STRtree

from .config import PROJECT_ROOT
from .tools.location import CURATED_LOCATIONS

WARD_NAME_RE = re.compile(r"^Ward\s+(\d+)\s+(.+)$", re.IGNORECASE)
DEFAULT_GEOJSON = PROJECT_ROOT / "backend" / "app" / "data" / "ghmc-wards.geojson"


@dataclass(frozen=True)
class WardInfo:
    ward_id: str
    ward_name: str


@dataclass
class _WardFeature:
    ward_id: str
    ward_name: str
    geometry: Any


def parse_ward_name(raw: str) -> WardInfo | None:
    match = WARD_NAME_RE.match(raw.strip())
    if not match:
        return None
    return WardInfo(ward_id=match.group(1), ward_name=match.group(2).strip())


def _load_features(path: Path) -> list[_WardFeature]:
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    features: list[_WardFeature] = []
    for feature in payload.get("features") or []:
        if not isinstance(feature, dict):
            continue
        props = feature.get("properties") or {}
        name = props.get("name") or props.get("Name") or ""
        if not isinstance(name, str):
            continue
        parsed = parse_ward_name(name)
        if parsed is None:
            continue
        geometry = feature.get("geometry")
        if not geometry:
            continue
        try:
            geom = shape(geometry)
        except (TypeError, ValueError):
            continue
        features.append(_WardFeature(parsed.ward_id, parsed.ward_name, geom))
    return features


class WardLookup:
    def __init__(self, geojson_path: Path = DEFAULT_GEOJSON) -> None:
        self._features = _load_features(geojson_path)
        self._geometries = [item.geometry for item in self._features]
        self._tree = STRtree(self._geometries) if self._geometries else None

    @property
    def loaded(self) -> bool:
        return bool(self._features)

    def lookup(self, lat: float, lng: float) -> WardInfo | None:
        if self._tree is None:
            return None
        point = Point(lng, lat)
        for index in self._tree.query(point):
            feature = self._features[int(index)]
            if feature.geometry.contains(point) or feature.geometry.touches(point):
                return WardInfo(feature.ward_id, feature.ward_name)
        return None

    def all_wards(self) -> list[WardInfo]:
        return [WardInfo(item.ward_id, item.ward_name) for item in self._features]

    def representative_point(self, ward_id: str) -> tuple[float, float] | None:
        """Return a lat/lng pair guaranteed to fall inside the ward polygon."""
        for item in self._features:
            if item.ward_id != ward_id:
                continue
            point = item.geometry.representative_point()
            return float(point.y), float(point.x)
        return None

    def load_geojson(self) -> dict[str, Any]:
        if not DEFAULT_GEOJSON.is_file():
            return {"type": "FeatureCollection", "features": []}
        return json.loads(DEFAULT_GEOJSON.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def get_ward_lookup() -> WardLookup:
    return WardLookup()


def nearest_curated_area(lat: float, lng: float) -> str:
    best = CURATED_LOCATIONS[0].area
    best_distance = float("inf")
    for location in CURATED_LOCATIONS:
        d_lat = lat - location.lat
        d_lng = lng - location.lng
        distance = d_lat * d_lat + d_lng * d_lng
        if distance < best_distance:
            best_distance = distance
            best = location.area
    return best


def ward_for_record(payload: dict[str, Any], lookup: WardLookup | None = None) -> WardInfo:
    lookup = lookup or get_ward_lookup()
    location = payload.get("location") if isinstance(payload.get("location"), dict) else None
    ward_hint = payload.get("ward") if isinstance(payload.get("ward"), dict) else None
    is_demo = payload.get("source") == "demonstration"

    if is_demo and ward_hint:
        ward_id = str(ward_hint.get("ward_id") or ward_hint.get("id") or "hyderabad")
        ward_name = str(ward_hint.get("ward_name") or ward_hint.get("name") or "Hyderabad")
        return WardInfo(ward_id=ward_id, ward_name=ward_name)

    if location:
        lat, lng = location.get("lat"), location.get("lng")
        try:
            if lat is not None and lng is not None:
                found = lookup.lookup(float(lat), float(lng))
                if found:
                    return found
        except (TypeError, ValueError):
            pass

    if ward_hint:
        ward_id = str(ward_hint.get("ward_id") or ward_hint.get("id") or "hyderabad")
        ward_name = str(ward_hint.get("ward_name") or ward_hint.get("name") or "Hyderabad")
        return WardInfo(ward_id=ward_id, ward_name=ward_name)

    if location:
        lat, lng = location.get("lat"), location.get("lng")
        try:
            if lat is not None and lng is not None:
                area = nearest_curated_area(float(lat), float(lng))
                return WardInfo(ward_id=area.lower().replace(" ", "-"), ward_name=area)
        except (TypeError, ValueError):
            pass
        address = location.get("address")
        if isinstance(address, str):
            for curated in CURATED_LOCATIONS:
                if curated.area.lower() in address.lower() or curated.name.lower() in address.lower():
                    return WardInfo(
                        ward_id=curated.area.lower().replace(" ", "-"),
                        ward_name=curated.area,
                    )
    return WardInfo(ward_id="hyderabad", ward_name="Hyderabad")
