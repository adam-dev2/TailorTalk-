import google.generativeai as genai
from calendar_utils import check_availability, book_meeting
from datetime import datetime, timedelta
import json
from dateutil.parser import isoparse
import pytz

genai.configure(api_key="AIzaSyArE6QBL7q8-4CcJ1hVDXH_h9qlYkMSkLA")

model = genai.GenerativeModel("gemini-1.5-flash")  

def extract_meeting_info(user_input):
    prompt = f"""
Extract meeting details from this input. Reply ONLY in JSON with these fields:
- start_time: ISO 8601 datetime
- duration: integer (minutes, default to 30)
- summary: short text (optional)

Input: "{user_input}"
"""

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()

        if content.startswith("```json"):
            content = content.removeprefix("```json").removesuffix("```").strip()

        return json.loads(content)

    except Exception as e:
        print("[Gemini error]", e)
        return None


def run_agent(user_input):
    user_input_lower = user_input.lower()

    if "availability" in user_input_lower or "free" in user_input_lower:
        return "❓ Please specify a time range so I can check availability."

    elif "book" in user_input_lower or "schedule" in user_input_lower:
        meeting_info = extract_meeting_info(user_input)

        if not meeting_info or "start_time" not in meeting_info:
            return "❌ I couldn’t understand the meeting time. Can you rephrase it?"

        try:
            
            start = isoparse(meeting_info["start_time"]).astimezone(pytz.timezone("Asia/Kolkata"))
            duration = meeting_info.get("duration", 30)
            end = start + timedelta(minutes=duration)

            start_str = start.isoformat()
            end_str = end.isoformat()

            # ✅ CHECK FOR CONFLICTING EVENTS BEFORE BOOKING
            conflict_msg = check_availability(start.isoformat(), end.isoformat())
            if "❌" in conflict_msg:
                return conflict_msg

            # ✅ Slot is free, proceed to book
            return book_meeting(
                start.isoformat(),
                end.isoformat(),
                summary=meeting_info.get("summary", "TailorTalk Meeting")
            )

        except Exception as e:
            print("[Agent Error]", e)
            return "❌ Something went wrong. Please check your input and try again."

    else:
        return "🤖 Please tell me when you'd like the meeting or check availability."
