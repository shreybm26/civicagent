import json
from pathlib import Path
from typing import Any

from ..contracts import ServiceId

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data"
REQUIRED = {"service_id", "schema_version", "service_name", "description", "department", "keywords", "fields", "submission"}
KNOWN = {"road_issue", "garbage_issue", "streetlight_issue", "water_issue", "sanitation_issue"}

class SchemaRegistry:
    def __init__(self, directory: Path = DATA / "schemas"):
        self.directory = directory
        self._schemas = self._load()

    def _load(self) -> dict[str, dict[str, Any]]:
        found = {}
        for path in sorted(self.directory.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            missing = REQUIRED - set(data)
            if missing or data["service_id"] not in KNOWN or data["service_id"] in found:
                raise ValueError(f"Invalid civic schema {path.name}: {sorted(missing)}")
            ids = [f.get("id") for f in data["fields"]]
            if len(ids) != len(set(ids)) or any("type" not in f or "required" not in f for f in data["fields"]):
                raise ValueError(f"Invalid fields in {path.name}")
            found[data["service_id"]] = data
        if set(found) != KNOWN:
            raise ValueError(f"Expected exactly five schemas, found {sorted(found)}")
        return found

    def get(self, service_id: ServiceId) -> dict[str, Any]:
        if service_id not in self._schemas: raise KeyError(service_id)
        return self._schemas[service_id]

    def all(self) -> dict[str, dict[str, Any]]: return dict(self._schemas)
