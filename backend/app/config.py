"""Environment-backed runtime settings with safe demo defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .contracts import ServiceId

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name, str(default)).strip()
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _origins_env() -> tuple[str, ...]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return tuple(origin.strip() for origin in raw.split(",") if origin.strip())


@dataclass(frozen=True)
class Settings:
    provider_mode: str = os.getenv("PROVIDER_MODE", "mock").strip().lower() or "mock"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    cors_origins: tuple[str, ...] = _origins_env()
    max_upload_bytes: int = _int_env("MAX_UPLOAD_BYTES", 10 * 1024 * 1024)
    max_sessions: int = _int_env("MAX_SESSIONS", 100)
    schema_count: int = 5

    @property
    def known_service_ids(self) -> tuple[ServiceId, ...]:
        return (
            "road_issue",
            "garbage_issue",
            "streetlight_issue",
            "water_issue",
            "sanitation_issue",
        )


settings = Settings()

# Backward-compatible names for the existing prototype and Shrey's provider work.
GEMINI_API_KEY = settings.gemini_api_key
GEMINI_MODEL = settings.gemini_model
PROVIDER_MODE = settings.provider_mode
CORS_ORIGINS = settings.cors_origins
MAX_UPLOAD_BYTES = settings.max_upload_bytes
MAX_SESSIONS = settings.max_sessions
