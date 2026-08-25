"""Deterministic provider boundary for Phase 1.

The default provider never invents a service or field value. Phase 2 can
replace this implementation behind the same methods without changing the API.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .contracts import Candidate, RouterResult, ServiceId


class ConversationProvider:
    """Provider interface with explicit fixture injection and safe defaults."""

    def __init__(
        self,
        *,
        classifications: Mapping[str, RouterResult] | None = None,
        candidates: Mapping[str, Sequence[Candidate]] | None = None,
    ) -> None:
        self._classifications = {
            key.strip().lower(): value for key, value in (classifications or {}).items()
        }
        self._candidates = {
            key.strip().lower(): list(value) for key, value in (candidates or {}).items()
        }

    def classify(self, message: str, known_services: Sequence[ServiceId]) -> RouterResult:
        """Return only an explicitly configured, known service fixture."""

        result = self._classifications.get(message.strip().lower())
        if result is not None and result.service_id in known_services:
            return result
        return RouterResult(
            service_id=None,
            confidence=0.0,
            needs_clarification=True,
            message="I need a little more detail about the civic issue you want to report.",
        )

    def collect(self, message: str) -> list[Candidate]:
        """Return only explicitly configured extraction fixtures."""

        return list(self._candidates.get(message.strip().lower(), []))
