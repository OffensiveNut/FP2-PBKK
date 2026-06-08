import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_email(to: str, subject: str, body: str) -> bool:
    smtp_host = settings.SMTP_HOST
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASSWORD
    smtp_from = settings.SMTP_FROM_EMAIL

    if not smtp_host or not smtp_user or not smtp_pass or not smtp_from:
        logger.warning("SMTP not configured, skipping email to %s", to)
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_from
    msg["To"] = to

    try:
        with smtplib.SMTP(smtp_host, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info("Email sent to %s", to)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to, e)
        return False


def send_password_email(to: str, username: str, password: str, nama_lengkap: str) -> bool:
    subject = "Akun FastPresensi telah dibuat"
    body = f"""Halo {nama_lengkap},

Akun FastPresensi Anda telah dibuat. Berikut adalah kredensial login Anda:

Username: {username}
Password: {password}

Silakan login di aplikasi dan segera ganti password Anda.

Terima kasih.
"""
    return _send_email(to, subject, body)
