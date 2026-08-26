from ..contracts import Candidate

PRIORITY = {"citizen": 4, "correction": 4, "conversation": 3, "photo": 2, "location": 3}

class CandidateResolver:
    def resolve(self, candidates: list[Candidate]) -> tuple[list[Candidate], list[str]]:
        grouped = {}
        for candidate in candidates: grouped.setdefault(candidate.field_id, []).append(candidate)
        accepted, conflicts = [], []
        for field_id, items in grouped.items():
            top = max(PRIORITY.get(x.source, 0) for x in items); ranked = [x for x in items if PRIORITY.get(x.source, 0) == top]
            values = {str(x.value).strip().lower() for x in ranked}
            if len(values) > 1: conflicts.append(field_id); continue
            accepted.append(max(ranked, key=lambda x: x.confidence))
        return accepted, conflicts
