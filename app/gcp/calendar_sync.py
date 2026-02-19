from datetime import datetime

from app.config import settings


def create_calendar_event(
    title: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    location: str = "",
    attendee_email: str = "",
) -> str:
    """Create a Google Calendar event. Returns event ID."""
    if not settings.firebase_credentials_path:
        # Development mode
        return f"dev-calendar-event-{title}"

    from googleapiclient.discovery import build
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_file(
        settings.firebase_credentials_path,
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    service = build("calendar", "v3", credentials=creds)

    event_body = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "America/New_York"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "America/New_York"},
        "location": location,
    }

    if attendee_email:
        event_body["attendees"] = [{"email": attendee_email}]

    event = service.events().insert(calendarId="primary", body=event_body).execute()
    return event.get("id", "")
