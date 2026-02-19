"""Email service for automated notifications.

In production, this would integrate with SendGrid, Mailgun, or Gmail API.
For now, provides the interface and logs in development mode.
"""
import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def send_welcome_email(email: str, display_name: str) -> bool:
    """Send welcome email to new user."""
    logger.info(f"[EMAIL] Welcome email to {email} ({display_name})")
    # In production: integrate with email provider
    return True


async def send_questionnaire_reminder(email: str, questionnaire_title: str) -> bool:
    """Send monthly questionnaire reminder."""
    logger.info(f"[EMAIL] Questionnaire reminder to {email}: {questionnaire_title}")
    return True


async def send_event_confirmation(email: str, event_title: str, event_date: str) -> bool:
    """Send event registration confirmation."""
    logger.info(f"[EMAIL] Event confirmation to {email}: {event_title} on {event_date}")
    return True


async def send_beit_din_update(email: str, case_title: str, new_status: str) -> bool:
    """Send Beit Din case status update."""
    logger.info(f"[EMAIL] Beit Din update to {email}: {case_title} -> {new_status}")
    return True
