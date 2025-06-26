import datetime
import pytz
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service(token: dict):
    creds = Credentials(
        token=token["token"],
        refresh_token=token["refresh_token"],
        token_uri=token["token_uri"],
        client_id=token["client_id"],
        client_secret=token["client_secret"],
        scopes=token["scopes"],
    )

    return build("calendar", "v3", credentials=creds)



def check_availability(start_time, end_time, token):
    try:
        service = get_calendar_service(token)   

        tz = pytz.timezone("Asia/Kolkata")
        start_dt = datetime.datetime.fromisoformat(start_time).astimezone(tz)
        end_dt = datetime.datetime.fromisoformat(end_time).astimezone(tz)

        if start_dt >= end_dt:
            return "❌ Invalid time range. Start time must be before end time."

        now = datetime.datetime.now(tz)
        if start_dt < now:
            return "❌ Cannot schedule in the past. Please choose a future time."

        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()

        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_iso,
            timeMax=end_iso,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])

        if events:
            conflict_titles = [e.get("summary", "No title") for e in events]
            conflicts = "\n".join(f"- {t}" for t in conflict_titles)
            return f"❌ You're busy during that time. Event(s) already scheduled:\n{conflicts}"
        else:
            return "✅ You're free during that time!"

    except Exception as e:
        print("❌ [Availability Error]", e)
        return "❌ Internal error while checking availability."



def book_meeting(start_time, end_time, summary="TailorTalk Meeting", token=None):
    try:
        service = get_calendar_service(token)

        calendar_list = service.calendarList().get(calendarId='primary').execute()
        print("📆 Booking on calendar:", calendar_list.get('summary'))

        print("📅 Start time:", start_time)
        print("📅 End time:", end_time)

        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print("✅ Event created:", created_event)

        return f"✅ Meeting booked successfully!\n📅 [View in Calendar]({created_event.get('htmlLink')})"

    except Exception as e:
        print("❌ Error:", e)
        return "❌ Failed to schedule the meeting."
