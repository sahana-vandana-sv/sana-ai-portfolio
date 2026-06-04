import os
from datetime import datetime, timedelta, timezone

import structlog
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

log = structlog.get_logger()

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _get_service():
    creds = None
    token_path = "token.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


async def create_event(title: str, start_datetime: str | None = None) -> dict:
    service = _get_service()

    if start_datetime:
        start = datetime.fromisoformat(start_datetime)
    else:
        start = datetime.now(timezone.utc) + timedelta(hours=1)

    end = start + timedelta(hours=1)

    event_body = {
        "summary": title,
        "start": {"dateTime": start.isoformat(), "timeZone": "Europe/London"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Europe/London"},
    }

    event = service.events().insert(calendarId="primary", body=event_body).execute()
    log.info("google_event_created", event_id=event["id"], title=title)
    return {"id": event["id"], "title": title, "start": start.isoformat()}


async def list_events(max_results: int = 10) -> list[dict]:
    service = _get_service()
    now = datetime.now(timezone.utc).isoformat()
    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = result.get("items", [])
    return [
        {
            "id": e["id"],
            "title": e.get("summary", ""),
            "start": e["start"].get("dateTime", e["start"].get("date")),
        }
        for e in events
    ]


async def delete_event(event_id: str) -> dict:
    service = _get_service()
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return {"deleted": event_id}
