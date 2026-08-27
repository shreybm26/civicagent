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


def _float_env(name: str, default: float) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except ValueError:
        return default
    return min(max(value, 0.0), 1.0)


def _positive_float_env(name: str, default: float) -> float:
    """Read a positive duration without allowing an unusable zero timeout."""
    try:
        value = float(os.getenv(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


@dataclass(frozen=True)
class Settings:
    provider_mode: str = os.getenv("PROVIDER_MODE", "mock").strip().lower() or "mock"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    # Multimodal Gemini requests can take considerably longer than text-only
    # requests, especially on the first request or when the model is busy.
    gemini_timeout_seconds: float = _positive_float_env("GEMINI_TIMEOUT_SECONDS", 120.0)
    # OpenRouter is used only for image analysis when OPENROUTER_API_KEY is set.
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    openrouter_timeout_seconds: float = _positive_float_env("OPENROUTER_TIMEOUT_SECONDS", 120.0)
    cors_origins: tuple[str, ...] = _origins_env()
    max_upload_bytes: int = _int_env("MAX_UPLOAD_BYTES", 10 * 1024 * 1024)
    max_sessions: int = _int_env("MAX_SESSIONS", 100)
    media_database_path: Path = Path(
        os.getenv("MEDIA_DATABASE_PATH", str(PROJECT_ROOT / "backend" / "data" / "civicagent-media.db"))
    )
    grievance_database_path: Path = Path(
        os.getenv(
            "GRIEVANCE_DATABASE_PATH",
            str(PROJECT_ROOT / "backend" / "data" / "civicagent-grievances.db"),
        )
    )
    supabase_url: str = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    tracking_pepper: str = os.getenv("TRACKING_PEPPER", "civicagent-demo-tracking").strip() or "civicagent-demo-tracking"
    resend_api_key: str = os.getenv("RESEND_API_KEY", "").strip()
    resend_from: str = os.getenv("RESEND_FROM", "CivicAgent Demo <onboarding@resend.dev>").strip()
    sendgrid_api_key: str = os.getenv("SENDGRID_API_KEY", "").strip()
    sendgrid_from: str = os.getenv("SENDGRID_FROM", "").strip()
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com").strip() or "smtp.gmail.com"
    smtp_port: int = _int_env("SMTP_PORT", 587)
    smtp_username: str = os.getenv("SMTP_USERNAME", "").strip()
    smtp_password: str = "".join(os.getenv("SMTP_PASSWORD", "").split())
    smtp_from: str = os.getenv("SMTP_FROM", "").strip()
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
    image_confidence_threshold: float = _float_env("IMAGE_CONFIDENCE_THRESHOLD", 0.7)
    schema_count: int = 5
    demo_status_updates: bool = os.getenv("DEMO_STATUS_UPDATES", "").strip() == "1"
    seed_demo_tickets: bool = os.getenv("SEED_DEMO_TICKETS", "").strip() == "1"

    @property
    def known_service_ids(self) -> tuple[ServiceId, ...]:
        return (
            "road_issue",
            "garbage_issue",
            "streetlight_issue",
            "water_issue",
            "sanitation_issue",
        )

    @property
    def mail_configured(self) -> bool:
        return bool(self.sendgrid_api_key) or bool(self.resend_api_key) or bool(self.smtp_username and self.smtp_password)

    @property
    def mail_backend(self) -> str:
        if self.sendgrid_api_key:
            return "sendgrid"
        if self.resend_api_key:
            return "resend"
        if self.smtp_username and self.smtp_password:
            return "smtp"
        return "none"


settings = Settings()

# Backward-compatible names for the existing prototype and Shrey's provider work.
GEMINI_API_KEY = settings.gemini_api_key
GEMINI_MODEL = settings.gemini_model
PROVIDER_MODE = settings.provider_mode
CORS_ORIGINS = settings.cors_origins
MAX_UPLOAD_BYTES = settings.max_upload_bytes
MAX_SESSIONS = settings.max_sessions
