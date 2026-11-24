"""Email delivery adapters.

The application depends on the :class:`EmailSender` protocol; only this module
knows about SMTP. Swapping in an HTTP provider (Resend, Postmark, ...) or a fake
in tests means implementing the same one-method interface.
"""

import asyncio
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr
from typing import Protocol

from app.core.config import Settings
from app.core.errors import AppError


class EmailNotConfiguredError(AppError):
    """Raised when no SMTP relay is configured, instead of claiming delivery."""

    status_code = 503
    code = "EMAIL_NOT_CONFIGURED"
    message = "Email delivery is not configured on this server."


class EmailDeliveryError(AppError):
    """Raised when the relay rejects or cannot be reached."""

    status_code = 502
    code = "EMAIL_DELIVERY_FAILED"
    message = "The email could not be sent. Please try again later."


@dataclass(frozen=True)
class EmailContent:
    """A rendered message, ready for any transport."""

    subject: str
    text: str
    html: str


class EmailSender(Protocol):
    """Port implemented by every email transport."""

    async def send(self, *, to: str, content: EmailContent) -> None: ...


def build_password_reset_email(*, reset_url: str, ttl_minutes: int) -> EmailContent:
    """Render the Persian password-reset message for ``reset_url``."""
    subject = "بازیابی رمز عبور روتین کده"
    text = (
        "سلام،\n\n"
        "درخواست بازیابی رمز عبور برای حساب شما در روتین کده ثبت شد.\n"
        f"برای تعیین رمز جدید این لینک را باز کنید: {reset_url}\n\n"
        f"این لینک {ttl_minutes} دقیقه اعتبار دارد و فقط یک بار قابل استفاده است.\n"
        "اگر این درخواست را شما نداده‌اید، این ایمیل را نادیده بگیرید؛ رمز فعلی "
        "شما تغییر نمی‌کند.\n\n"
        "روتین کده — عادت‌های کوچک، تغییرات بزرگ"
    )
    html = (
        '<div dir="rtl" style="font-family:Tahoma,Arial,sans-serif;line-height:1.9;'
        'color:#0f172a">'
        "<h2 style=\"margin:0 0 12px\">بازیابی رمز عبور روتین کده</h2>"
        "<p>درخواست بازیابی رمز عبور برای حساب شما ثبت شد. برای تعیین رمز جدید "
        "روی دکمه زیر بزنید.</p>"
        f'<p><a href="{reset_url}" style="display:inline-block;padding:10px 18px;'
        "border-radius:10px;background:#2563eb;color:#fff;text-decoration:none;"
        'font-weight:bold">تعیین رمز عبور جدید</a></p>'
        f'<p style="font-size:13px;color:#475569">این لینک {ttl_minutes} دقیقه '
        "اعتبار دارد و فقط یک بار قابل استفاده است. اگر این درخواست را شما "
        "نداده‌اید، این ایمیل را نادیده بگیرید.</p>"
        "</div>"
    )
    return EmailContent(subject=subject, text=text, html=html)


class SmtpEmailSender:
    """Send mail through a plain SMTP relay (STARTTLS or implicit TLS)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send(self, *, to: str, content: EmailContent) -> None:
        """Deliver the message off the event loop, mapping failures to AppError."""
        if not self._settings.smtp_host or not self._settings.smtp_from_email:
            raise EmailNotConfiguredError

        try:
            await asyncio.to_thread(self._send_sync, to, content)
        except (OSError, smtplib.SMTPException) as exc:
            raise EmailDeliveryError from exc

    def _send_sync(self, to: str, content: EmailContent) -> None:
        settings = self._settings
        message = EmailMessage()
        message["Subject"] = content.subject
        message["From"] = formataddr((settings.smtp_from_name, settings.smtp_from_email))
        message["To"] = to
        message.set_content(content.text)
        message.add_alternative(content.html, subtype="html")

        smtp_class = smtplib.SMTP_SSL if settings.smtp_use_ssl else smtplib.SMTP
        with smtp_class(settings.smtp_host, settings.smtp_port, timeout=20) as client:
            if settings.smtp_use_tls and not settings.smtp_use_ssl:
                client.starttls()
            if settings.smtp_username:
                client.login(settings.smtp_username, settings.smtp_password)
            client.send_message(message)
