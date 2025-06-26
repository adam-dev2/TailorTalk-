import streamlit as st
import requests
import json
import urllib.parse

st.set_page_config(page_title="TailorTalk AI", page_icon="🧵")
st.title("🧵 TailorTalk AI – Meeting Scheduler")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "token" not in st.session_state:
    params = st.query_params
    if "token" in params:
        try:
            decoded = urllib.parse.unquote(params["token"])
            st.session_state.token = json.loads(decoded)
            st.success("✅ Logged in with Google!")
        except Exception as e:
            st.error(f"❌ Failed to load token: {e}")
            st.stop()

if not st.session_state.get("token"):
    st.info("🔐 Please sign in with Google to book meetings in your calendar.")
    login_url = "https://tailortalk-qbst.onrender.com/login"
    st.markdown(f"[🔐 Sign in with Google]({login_url})", unsafe_allow_html=True)
    st.stop()

user_input = st.chat_input("Say something like: Book meeting at 10am tomorrow")

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    try:
        response = requests.post(
            "https://tailortalk-qbst.onrender.com/chat",
            json={
                "user_input": user_input,
                "token": st.session_state.token
            }
        )
        agent_reply = response.json().get("reply")
    except Exception as e:
        agent_reply = f"❌ Backend error: {str(e)}"

    st.session_state.chat_history.append(("bot", agent_reply))

for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)
