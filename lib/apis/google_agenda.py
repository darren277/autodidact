# google_agenda.py
from __future__ import print_function
import datetime as _dt
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


# ── CONFIG ──────────────────────────────────────────────────────────────
CLIENT_SECRET_FILE = Path(__file__).with_name("google-credentials.json")
TOKEN_FILE         = Path(__file__).with_name("token.json")
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",   # read/write Calendar
    "https://www.googleapis.com/auth/tasks",            # read/write Tasks
]

# ── AUTH ────────────────────────────────────────────────────────────────
def _get_credentials() -> Credentials:
    creds: Optional[Credentials] = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # Refresh or run OAuth2 flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=5055)
        TOKEN_FILE.write_text(creds.to_json())  # cache for next time
    return creds

# ── SERVICE BUILDERS ────────────────────────────────────────────────────
def calendar_service():
    return build("calendar", "v3", credentials=_get_credentials(), cache_discovery=False)

def tasks_service():
    return build("tasks", "v1", credentials=_get_credentials(), cache_discovery=False)

# ── CALENDAR HELPERS ────────────────────────────────────────────────────
def add_event(
    summary: str,
    start: _dt.datetime,
    end: _dt.datetime,
    calendar_id: str = "primary",
    description: str = "",
    timezone: str = "UTC",
    **extra_fields: Any,
) -> Dict[str, Any]:
    """Create a Calendar event and return the API response."""
    service = calendar_service()
    body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": timezone},
        "end":   {"dateTime": end.isoformat(),   "timeZone": timezone},
        **extra_fields,
    }
    return service.events().insert(calendarId=calendar_id, body=body).execute()

def upcoming_events(max_results: int = 10, calendar_id: str = "primary") -> List[Dict[str, Any]]:
    """Return the next *n* upcoming events."""
    service = calendar_service()
    now = _dt.datetime.utcnow().isoformat() + "Z"
    resp = (
        service.events()
        .list(calendarId=calendar_id, timeMin=now, maxResults=max_results, singleEvents=True, orderBy="startTime")
        .execute()
    )
    return resp.get("items", [])

# ── TASKS HELPERS ───────────────────────────────────────────────────────
def add_task(
    title: str,
    due: Optional[_dt.datetime] = None,
    notes: str = "",
    tasklist_id: str = "@default",
    **extra_fields: Any,
) -> Dict[str, Any]:
    """Create a task in the specified task‑list."""
    service = tasks_service()
    body = {"title": title, "notes": notes}
    if due:
        body["due"] = due.isoformat() + "Z"  # must be RFC3339
    body.update(extra_fields)
    return service.tasks().insert(tasklist=tasklist_id, body=body).execute()

def list_tasks(tasklist_id: str = "@default", show_completed: bool = False) -> List[Dict[str, Any]]:
    """Fetch tasks (optionally hiding completed ones)."""
    service = tasks_service()
    resp = service.tasks().list(tasklist=tasklist_id, showCompleted=show_completed).execute()
    return resp.get("items", [])




import datetime as dt

def add_event(summary: str, description: str, start: _dt.datetime, end: _dt.datetime, timezone: str = "UTC"):
    # Add a Calendar event for tomorrow, 1‑hour long
    tomorrow = dt.datetime.utcnow() + dt.timedelta(days=1)
    event = add_event(
        summary="Project sync-up",
        description="Initial roadmap discussion",
        start=tomorrow.replace(hour=16, minute=0, second=0, microsecond=0),
        end=tomorrow.replace(hour=17, minute=0, second=0, microsecond=0),
        timezone="America/Vancouver",
    )
    print(f"Created event → {event['htmlLink']}")

    # Show next five events
    for e in upcoming_events(5):
        when = e['start'].get('dateTime', e['start'].get('date'))
        print(f"{when} | {e['summary']}")


def list_task_lists():
    """List all task lists."""
    service = tasks_service()
    resp = service.tasklists().list().execute()
    return resp.get("items", [])




def create_task(title: str, description: str = "", due: _dt.datetime = None, tasklist_id: str = "@default"):
    # Add a task due in three days
    #task = add_task(
    #    title="Finish API integration",
    #    notes="Remember to add retry logic",
    #    due=dt.datetime.utcnow() + dt.timedelta(days=3)
    #)
    due = _dt.datetime.utcnow() + _dt.timedelta(days=3) if not due else due
    task = add_task(
        title=title,
        notes=description,
        due=due,
        tasklist_id=tasklist_id,
        status="needsAction",
        priority=1,
    )
    print(f"Created task → {task['id']}")


def list_task_lists():
    for t in list_task_lists():
        # status = "✓" if t.get("status") == "completed" else "⏳"
        print(f"{t['id']} | {t['title']} | {t['due']} | {t['status']}")
    return list_task_lists()


def get_or_create_app_calendar(service=None, calendar_name="Autodidact Events"):
    """
    Find a Google Calendar with the given name, or create it if it doesn't exist.
    Returns the calendar ID.
    """
    if service is None:
        service = calendar_service()
    # List calendars
    calendars = service.calendarList().list().execute().get('items', [])
    for cal in calendars:
        if cal.get('summary') == calendar_name:
            return cal['id']
    # Not found, create it
    new_cal = service.calendars().insert(body={
        'summary': calendar_name,
        'timeZone': 'UTC'
    }).execute()
    return new_cal['id']
