from ..contracts import Candidate

CHOICE_SYNONYMS = {
    "high": ("high", "severe", "bad", "very bad", "dangerous", "urgent", "critical", "major", "huge"),
    "medium": ("medium", "moderate", "average"),
    "low": ("low", "minor", "small", "slight"),
}


class CollectionEngine:
    def required_fields(self, schema: dict) -> list[dict]:
        return [f for f in schema["fields"] if f.get("required")]

    def collect(self, message: str, schema: dict, current: list[Candidate] | None = None) -> list[Candidate]:
        text = message.strip()
        if not text or text.lower() in {"i don't know", "dont know", "unknown", "not sure"}:
            return []
        existing = {c.field_id for c in (current or [])}
        missing = [f for f in self.required_fields(schema) if f["id"] not in existing]
        if not missing:
            return []
        field = missing[0]
        value = self._value_for(field, text)
        if value is None:
            return []
        return [
            Candidate(
                field_id=field["id"],
                value=value,
                source="conversation",
                confidence=0.8,
                reason="Extracted from the citizen’s message",
            )
        ]

    def _value_for(self, field: dict, text: str) -> str | None:
        if field.get("type") != "choice":
            return text
        lowered = text.lower()
        options = [str(option).lower() for option in field.get("options", [])]
        if lowered in options:
            return lowered
        for option in options:
            synonyms = CHOICE_SYNONYMS.get(option, (option,))
            if any(synonym in lowered for synonym in synonyms):
                return option
        return None
