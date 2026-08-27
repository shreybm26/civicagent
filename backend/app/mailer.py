"""Send a demonstration acknowledgement email via SMTP or Resend."""

from __future__ import annotations

import html
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

import httpx

from .contracts import TrackingField, TrackingView, normalize_ticket_status
from .field_labels import field_label

RESEND_URL = "https://api.resend.com/emails"
SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

NAVY = "#0b3a6e"
GOLD = "#c9a227"
SAFFRON_BG = "#fff4d6"
SAFFRON_BORDER = "#e6c36a"
INK = "#10243e"
MUTED = "#4e5d6b"

STATUS_BADGE_STYLES = {
    "pending": ("#fff4d6", "#8a5d19", "Pending"),
    "in_progress": ("#e8f1fb", "#0b3a6e", "In Progress"),
    "completed": ("#e8f6ee", "#187443", "Completed"),
}


class MailError(RuntimeError):
    """The acknowledgement could not be sent."""


def normalize_email(value: str) -> str:
    email = value.strip().casefold()
    if not EMAIL_RE.match(email) or len(email) > 254:
        raise MailError("Enter a valid email address.")
    return email


def smtp_configured(username: str, password: str) -> bool:
    return bool(username.strip() and password.strip())


def _field_lines(fields: list[TrackingField]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for field in fields:
        value = field.value
        if value is None or value == "":
            continue
        rows.append((field_label(field.id), str(value)))
    return rows


def status_badge_html(status: str) -> str:
    key = normalize_ticket_status(status)
    background, color, label = STATUS_BADGE_STYLES[key]
    return (
        f'<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
        f'background:{background};color:{color};font-size:12px;font-weight:700;">'
        f"{html.escape(label)}</span>"
    )


def build_acknowledgement_bodies(
    *,
    view: TrackingView,
    access_key: str,
    track_url: str,
) -> tuple[str, str]:
    department = view.department or "Civic services"
    location = view.location or "Not recorded"
    field_rows = _field_lines(view.fields)
    field_text = "\n".join(f"{label}: {value}" for label, value in field_rows) or "(no extra fields)"
    text = (
        "Municipal Civic Cell — demonstration acknowledgement\n"
        "This is not an official government email.\n\n"
        f"Service request ID: {view.sr_id}\n"
        f"Access key: {access_key}\n"
        f"Status: {view.status}\n"
        f"Department: {department}\n"
        f"Location: {location}\n\n"
        "Filed details:\n"
        f"{field_text}\n\n"
        f"Track this request: {track_url}\n"
        "Keep the access key private. Anyone with both values can open this demo ticket.\n"
    )

    detail_rows = "".join(
        f"""
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #d9e2ec;color:{MUTED};width:42%;vertical-align:top">{html.escape(label)}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #d9e2ec;color:{INK};vertical-align:top">{html.escape(value)}</td>
        </tr>
        """
        for label, value in field_rows
    ) or f'<tr><td colspan="2" style="padding:8px 12px;color:{MUTED}">No extra fields recorded.</td></tr>'

    html_body = f"""
    <div style="margin:0 auto;max-width:560px;background:#ffffff;color:{INK};font-family:Arial,sans-serif">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse">
        <tr>
          <td style="background:{NAVY};padding:18px 20px;border-bottom:4px solid {GOLD}">
            <div style="color:#ffffff;font-size:18px;font-weight:700">Municipal Civic Cell</div>
            <div style="color:#dbe7f5;font-size:13px;margin-top:4px">Demonstration grievance acknowledgement</div>
          </td>
        </tr>
        <tr>
          <td style="background:{SAFFRON_BG};border-bottom:1px solid {SAFFRON_BORDER};padding:10px 16px;color:#5c4308;font-size:13px;font-weight:600">
            Demonstration only. This is not an official government email and was not sent by a department.
          </td>
        </tr>
        <tr>
          <td style="padding:20px">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border:1px solid #d9e2ec;border-radius:8px;border-collapse:separate">
              <tr>
                <td style="padding:16px">
                  <div style="font-size:12px;color:{MUTED};text-transform:uppercase;letter-spacing:0.04em">Service request</div>
                  <div style="font-size:20px;font-weight:700;color:{NAVY};margin:6px 0 12px">{html.escape(view.sr_id)}</div>
                  <div style="font-size:12px;color:{MUTED};margin-bottom:4px">Access key</div>
                  <div style="font-family:Consolas,Monaco,monospace;font-size:16px;font-weight:700;margin-bottom:12px">{html.escape(access_key)}</div>
                  <div style="margin-bottom:12px">{status_badge_html(view.status_key)}</div>
                  <div style="font-size:14px;margin-bottom:6px"><strong>Department:</strong> {html.escape(department)}</div>
                  <div style="font-size:14px"><strong>Location:</strong> {html.escape(location)}</div>
                </td>
              </tr>
            </table>
            <div style="height:16px"></div>
            <div style="font-size:15px;font-weight:700;color:{NAVY};margin-bottom:8px">Filed details</div>
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border:1px solid #d9e2ec;border-collapse:collapse">
              {detail_rows}
            </table>
            <div style="height:18px"></div>
            <a href="{html.escape(track_url)}" style="display:inline-block;background:{NAVY};color:#ffffff;text-decoration:none;padding:12px 18px;border-radius:6px;font-weight:700">Track this request</a>
            <div style="height:18px"></div>
            <p style="margin:0;color:{MUTED};font-size:13px">Keep the access key private. Anyone with both the service request ID and access key can open this demonstration ticket.</p>
          </td>
        </tr>
        <tr>
          <td style="padding:14px 20px;background:#f4f7fb;color:{MUTED};font-size:12px;border-top:1px solid #d9e2ec">
            Privacy note: this message contains your one-time access key. Do not forward it.
          </td>
        </tr>
      </table>
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
    sendgrid_api_key: str = "",
    sendgrid_from: str = "",
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
    # HTTPS first: Railway Hobby blocks outbound SMTP (587/465).
    if sendgrid_api_key.strip():
        _send_via_sendgrid(
            api_key=sendgrid_api_key,
            from_address=sendgrid_from or smtp_from or smtp_username,
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
    except TimeoutError as exc:
        raise MailError(
            "Could not reach Gmail SMTP. Railway Hobby blocks outbound mail ports; use SendGrid or Resend over HTTPS."
        ) from exc
    except (smtplib.SMTPException, OSError) as exc:
        raise MailError(
            "Could not reach Gmail SMTP. Railway Hobby blocks outbound mail ports; use SendGrid or Resend over HTTPS."
        ) from exc


def _send_via_sendgrid(
    *,
    api_key: str,
    from_address: str,
    to_email: str,
    subject: str,
    text: str,
    html_body: str,
) -> None:
    name, email = parseaddr(from_address)
    if not email:
        raise MailError("Set SENDGRID_FROM to the Gmail address you verified in SendGrid.")
    try:
        response = httpx.post(
            SENDGRID_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": email, "name": name or "CivicAgent Demo"},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": text},
                    {"type": "text/html", "value": html_body},
                ],
            },
            timeout=20.0,
        )
    except httpx.HTTPError as exc:
        raise MailError("The mail service is temporarily unavailable.") from exc
    if response.status_code >= 400:
        raise MailError(_sendgrid_error_message(response))


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


def _sendgrid_error_message(response: httpx.Response) -> str:
    generic = "The acknowledgement email could not be sent. Check the address and try again."
    try:
        payload = response.json()
    except ValueError:
        return generic
    errors = payload.get("errors") if isinstance(payload, dict) else None
    raw = ""
    if isinstance(errors, list) and errors:
        first = errors[0]
        raw = str(first.get("message") if isinstance(first, dict) else first)
    text = raw.lower()
    if "verified" in text or ("from" in text and "permission" in text):
        return "Verify this From address as a Single Sender in SendGrid, then try again."
    return generic
