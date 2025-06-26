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
You're a smart meeting scheduler. Extract details from the user's input.

📌 Context:
- Today's date is **{datetime.now().strftime('%Y-%m-%d')}** (Asia/Kolkata).
- Assume **Asia/Kolkata** timezone.
- Do **NOT hallucinate** extra fields or adjust logic yourself.
- "Tomorrow" means { (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d') }

🎯 Respond ONLY in raw JSON with:
- start_time: ISO 8601 datetime (e.g., 2025-06-27T10:00:00+05:30)
- duration: integer (in minutes, default to 30)
- summary: short description (optional)

User input: "{user_input}"
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
            ist = pytz.timezone("Asia/Kolkata")

            start = isoparse(meeting_info["start_time"])
            start = start.replace(tzinfo=None)  
            start = ist.localize(start)         

            duration = meeting_info.get("duration", 30)
            end = start + timedelta(minutes=duration)

            now = datetime.now(ist)

            if start < now:
                return "❌ Cannot schedule in the past. Please choose a future time."

            conflict_msg = check_availability(start.isoformat(), end.isoformat())
            if "❌" in conflict_msg:
                return conflict_msg

            print("🕒 Requested start:", start.isoformat())
            print("🕒 Current time:", now.isoformat())

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

