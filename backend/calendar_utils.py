import datetime
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = None
    token_path = "token.pickle"

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "backend/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)

        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)

def check_availability(start_time, end_time):
    service = get_calendar_service()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    if events:
        return f"❌ You're busy during that time. {len(events)} event(s) already scheduled."
    else:
        return "✅ You're free during that time!"




def book_meeting(start_time, end_time, summary="TailorTalk Meeting"):
    try:
        service = get_calendar_service()

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
