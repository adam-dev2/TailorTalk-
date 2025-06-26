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
You are a helpful assistant that extracts meeting details from casual, human input.

📅 Context:
- Assume the user is in the **Asia/Kolkata** timezone.
- Today's date is **{datetime.now().strftime('%Y-%m-%d')}**
- Interpret phrases like "tomorrow", "next Friday", "10 am" etc., relative to today.
- DO NOT make up values or hallucinate.

🎯 Your job:
Understand the user's intent and return ONLY valid JSON with these fields:
- **start_time**: Full ISO 8601 datetime string (e.g., "2025-06-27T10:00:00+05:30")
- **duration**: Integer in minutes (optional, default to 30)
- **summary**: Short description (optional)

Example user input: "{user_input}"

🔁 Respond ONLY with JSON. No explanations, markdown, or formatting.
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





def run_agent(user_input, token):
    user_input_lower = user_input.lower()

    if "availability" in user_input_lower or "free" in user_input_lower:
        return "❓ Please specify a time range so I can check availability."

    elif "book" in user_input_lower or "schedule" in user_input_lower:
        meeting_info = extract_meeting_info(user_input)

        if not meeting_info or "start_time" not in meeting_info:
            return "❌ I couldn’t understand the meeting time. Can you rephrase it?"

        try:
            ist = pytz.timezone("Asia/Kolkata")

            start = isoparse(meeting_info["start_time"])
            start = start.replace(tzinfo=None)
            start = ist.localize(start)

            duration = meeting_info.get("duration", 30)
            end = start + timedelta(minutes=duration)
            now = datetime.now(ist)

            if start < now:
                return "❌ Cannot schedule in the past. Please choose a future time."

            conflict_msg = check_availability(start.isoformat(), end.isoformat(), token)
            if "❌" in conflict_msg:
                return conflict_msg

            return book_meeting(
                start.isoformat(),
                end.isoformat(),
                summary=meeting_info.get("summary", "TailorTalk Meeting"),
                token=token
            )

        except Exception as e:
            print("[Agent Error]", e)
            return "❌ Something went wrong. Please check your input and try again."

    else:
        return "🤖 Please tell me when you'd like the meeting or check availability."


