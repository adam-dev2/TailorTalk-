import streamlit as st
import requests

st.set_page_config(page_title="TailorTalk AI", page_icon="🧵")
st.title("🧵 TailorTalk AI – Meeting Scheduler")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Say something...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    response = requests.post(
        "https://tailortalk-qbst.onrender.com/chat", json={"user_input": user_input}
    )

    agent_reply = response.json().get("reply")
    st.session_state.chat_history.append(("bot", agent_reply))

for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)
