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
You're a smart AI assistant helping schedule meetings.

👤 Users speak casually and like a friend (e.g., "set something up tomorrow at like 5", "yo book call next Mon").

🎯 Your job:
1. Parse their intent — even if informal, broken, or slang.
2. Assume IST (Asia/Kolkata timezone).
3. Treat today as {datetime.now().strftime('%Y-%m-%d')}.
4. "Tomorrow" means {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}.
5. If time is vague like "evening" or "afternoon", make a **reasonable guess** (e.g., evening → 6:00 PM).

🚫 DO NOT:
- Explain anything
- Say "I'm not sure"
- Add markdown
- Hallucinate keys

✅ Respond ONLY in raw JSON with:
- start_time (ISO 8601 datetime)
- duration (minutes, default to 30)
- summary (optional)

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


