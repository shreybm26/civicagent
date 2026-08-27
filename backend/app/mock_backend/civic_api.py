"""Open311-style mock backend used to prove receipt-gated completion."""

from __future__ import annotations

from datetime import datetime, timezone
import secrets
from uuid import UUID

from ..contracts import Receipt

_ID_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class MockBackendError(RuntimeError):
    """Retryable mock backend failure."""


class MockCivicBackend:
    def __init__(self, *, fail_next: bool = False) -> None:
        self.fail_next = fail_next
        self._sequence = 0

    def submit(
        self,
        *,
        session_id: UUID,
        service_id: str,
        department: str,
        payload: dict[str, object],
        id_prefix: str = "CIV",
    ) -> Receipt:
        if self.fail_next:
            self.fail_next = False
            raise MockBackendError("The civic service is temporarily unavailable. Please retry review.")
        if not payload:
            raise MockBackendError("The civic request payload was empty.")
        self._sequence += 1
        timestamp = datetime.now(timezone.utc)
        nonce = "".join(secrets.choice(_ID_ALPHABET) for _ in range(4))
        reference = f"{id_prefix}-{timestamp:%Y%m%d}-{self._sequence:04d}-{nonce}"
        return Receipt(
            reference=reference,
            status="Received",
            department=department,
            timestamp=timestamp,
        )
