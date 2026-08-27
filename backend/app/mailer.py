"""Send a demonstration acknowledgement email via SMTP or Resend."""

from __future__ import annotations

import html
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

import httpx

from .contracts import TrackingField, TrackingView

RESEND_URL = "https://api.resend.com/emails"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class MailError(RuntimeError):
    """The acknowledgement could not be sent."""


def normalize_email(value: str) -> str:
    email = value.strip().casefold()
    if not EMAIL_RE.match(email) or len(email) > 254:
        raise MailError("Enter a valid email address.")
    return email


def smtp_configured(username: str, password: str) -> bool:
    return bool(username.strip() and password.strip())


def _field_lines(fields: list[TrackingField]) -> str:
    lines: list[str] = []
    for field in fields:
        value = field.value
        if value is None or value == "":
            continue
        lines.append(f"- {field.id}: {value}")
    return "\n".join(lines) or "- (no extra fields)"


def build_acknowledgement_bodies(
    *,
    view: TrackingView,
    access_key: str,
    track_url: str,
) -> tuple[str, str]:
    field_text = _field_lines(view.fields)
    text = (
        "CivicAgent demonstration acknowledgement\n"
        "This is not an official government email.\n\n"
        f"Service request ID: {view.sr_id}\n"
        f"Access key: {access_key}\n"
        f"Status: {view.status}\n"
        f"Department: {view.department or 'Civic services'}\n"
        f"Location: {view.location or 'Not recorded'}\n\n"
        "Filed details:\n"
        f"{field_text}\n\n"
        f"Track this request: {track_url}\n"
        "Open the link, enter the service request ID and access key, and you can see status and nearby demonstration reports.\n\n"
        "Keep the access key private. Anyone with both values can open this demo ticket.\n"
    )
    field_html = html.escape(field_text)
    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;color:#10243e">
      <p style="background:#fff4d6;border:1px solid #e6c36a;padding:8px 12px;font-size:13px">
        <strong>Demonstration only.</strong> This is not an official government email and was not sent by a department.
      </p>
      <h1 style="font-size:20px">Grievance acknowledgement</h1>
      <p><strong>Service request ID:</strong> {html.escape(view.sr_id)}<br/>
      <strong>Access key:</strong> {html.escape(access_key)}<br/>
      <strong>Status:</strong> {html.escape(view.status)}<br/>
      <strong>Department:</strong> {html.escape(view.department or "Civic services")}<br/>
      <strong>Location:</strong> {html.escape(view.location or "Not recorded")}</p>
      <p><a href="{html.escape(track_url)}">Open tracking</a> and enter the ID and access key.</p>
      <pre style="white-space:pre-wrap;background:#f4f7fb;padding:12px">{field_html}</pre>
      <p style="color:#5c4308;font-size:13px">Keep the access key private.</p>
    </div>
    """
    return text, html_body


def send_acknowledgement(
    *,
    to_email: str,
    view: TrackingView,
    access_key: str,
    track_url: str,
    resend_api_key: str = "",
    resend_from: str = "",
    smtp_host: str = "",
    smtp_port: int = 587,
    smtp_username: str = "",
    smtp_password: str = "",
    smtp_from: str = "",
) -> None:
    to_email = normalize_email(to_email)
    text, html_body = build_acknowledgement_bodies(view=view, access_key=access_key, track_url=track_url)
    subject = f"Demo acknowledgement {view.sr_id}"
    smtp_password = "".join(smtp_password.split())
    smtp_username = smtp_username.strip()
    if smtp_configured(smtp_username, smtp_password):
        _send_via_smtp(
            host=smtp_host or "smtp.gmail.com",
            port=smtp_port or 587,
            username=smtp_username,
            password=smtp_password,
            from_address=_smtp_from(smtp_from, smtp_username),
            to_email=to_email,
            subject=subject,
            text=text,
            html_body=html_body,
        )
        return
    if resend_api_key.strip():
        _send_via_resend(
            api_key=resend_api_key,
            from_address=resend_from,
            to_email=to_email,
            subject=subject,
            text=text,
            html_body=html_body,
        )
        return
    raise MailError("Email sending is not configured on this server.")


def _smtp_from(explicit: str, username: str) -> str:
    if explicit.strip():
        return explicit.strip()
    return formataddr(("CivicAgent Demo", username.strip()))


def _send_via_smtp(
    *,
    host: str,
    port: int,
    username: str,
    password: str,
    from_address: str,
    to_email: str,
    subject: str,
    text: str,
    html_body: str,
) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = from_address
    message["To"] = to_email
    message.attach(MIMEText(text, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))
    _, envelope_from = parseaddr(from_address)
    envelope_from = envelope_from or username
    try:
        with smtplib.SMTP(host, port, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.sendmail(envelope_from, [to_email], message.as_string())
    except smtplib.SMTPAuthenticationError as exc:
        raise MailError("The mail service rejected the SMTP login. Check the app password.") from exc
    except (smtplib.SMTPException, OSError) as exc:
        raise MailError("The mail service is temporarily unavailable.") from exc


def _send_via_resend(
    *,
    api_key: str,
    from_address: str,
    to_email: str,
    subject: str,
    text: str,
    html_body: str,
) -> None:
    try:
        response = httpx.post(
            RESEND_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "from": from_address,
                "to": [to_email],
                "subject": subject,
                "text": text,
                "html": html_body,
            },
            timeout=20.0,
        )
    except httpx.HTTPError as exc:
        raise MailError("The mail service is temporarily unavailable.") from exc
    if response.status_code >= 400:
        raise MailError(_resend_error_message(response))


def _resend_error_message(response: httpx.Response) -> str:
    generic = "The acknowledgement email could not be sent. Check the address and try again."
    try:
        payload = response.json()
    except ValueError:
        return generic
    raw = payload.get("message") if isinstance(payload, dict) else None
    text = str(raw or payload).lower()
    if "own email" in text or "testing emails" in text:
        return (
            "This demo sender can only deliver to the Resend account owner's inbox. "
            "Use Track application with the service request ID if you entered a different address."
        )
    return generic
