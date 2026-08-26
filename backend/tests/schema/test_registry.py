from pathlib import Path
import json
import pytest
from app.schemas.registry import SchemaRegistry

def test_registry_loads_exactly_five_services():
    registry = SchemaRegistry()
    assert set(registry.all()) == {"road_issue", "garbage_issue", "streetlight_issue", "water_issue", "sanitation_issue"}

def test_registry_rejects_duplicate_or_unknown(tmp_path: Path):
    source = Path(__file__).parents[2] / "app" / "data" / "schemas"
    for path in source.glob("*.json"):
        (tmp_path / path.name).write_text(path.read_text(), encoding="utf-8")
    (tmp_path / "bad.json").write_text(json.dumps({"service_id":"unknown"}), encoding="utf-8")
    with pytest.raises(ValueError): SchemaRegistry(tmp_path)
