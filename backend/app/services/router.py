from ..contracts import RouterResult, ServiceId

THRESHOLD = 0.7

class ServiceRouter:
    def __init__(self, schemas: dict[str, dict]): self.schemas = schemas

    def route(self, text: str, provider=None) -> RouterResult:
        text = text.strip(); lower = text.lower()
        if provider:
            result = provider.classify(text, tuple(self.schemas))
            if result.service_id and result.confidence >= THRESHOLD: return result
        scores = {sid: sum(1 for word in schema.get("keywords", []) if word in lower) for sid, schema in self.schemas.items()}
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if not ranked or ranked[0][1] == 0:
            return RouterResult(message="I can help with potholes, garbage, streetlights, water leaks, or sanitation issues. Which one would you like to report?")
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            return RouterResult(message="I’m not sure which civic service fits. Could you describe the issue a little more?")
        return RouterResult(service_id=ranked[0][0], confidence=min(0.95, .7 + .1 * ranked[0][1]), needs_clarification=False, message="I’ve matched this to the right civic service.")
