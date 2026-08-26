from ..contracts import Candidate

class CollectionEngine:
    def required_fields(self, schema: dict) -> list[dict]:
        return [f for f in schema["fields"] if f.get("required")]

    def collect(self, message: str, schema: dict, current: list[Candidate] | None = None) -> list[Candidate]:
        text = message.strip()
        if not text or text.lower() in {"i don't know", "dont know", "unknown", "not sure"}: return []
        existing = {c.field_id for c in (current or [])}
        missing = [f for f in self.required_fields(schema) if f["id"] not in existing]
        if not missing: return []
        field = missing[0]
        value = text.lower() if field["type"] == "choice" and text.lower() in field.get("options", []) else text
        if field["type"] == "choice" and value == text: return []
        return [Candidate(field_id=field["id"], value=value, source="conversation", confidence=.8, reason="Extracted from the citizen’s message")]
