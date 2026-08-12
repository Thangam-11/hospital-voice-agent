"""
Minimal Streamlit demo for testing the hospital voice agent's /chat endpoint.

Run with:
    streamlit run streamlit_demo.py

Requires your FastAPI server running separately:
    uvicorn src.api_service.main:app --reload
"""

import uuid

import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Hospital Voice Agent — Demo", page_icon="🏥")
st.title("🏥 Hospital Voice Agent — Chat Demo")
st.caption("Text-based testing of the LangGraph agent before Twilio is wired up.")

# --- Session state: one conversation_id per browser session, persists ---
# --- across turns so the agent's memory (checkpointer) actually works. ---
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": str}

# --- Sidebar: conversation controls ---
with st.sidebar:
    st.subheader("Session")
    st.code(st.session_state.conversation_id, language=None)

    if st.button("🔄 New conversation"):
        st.session_state.conversation_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption(f"API: {API_BASE_URL}")

# --- Render chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Handle new input ---
if prompt := st.chat_input("Type as if you're a patient calling..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={
                        "message": prompt,
                        "conversation_id": st.session_state.conversation_id,
                    },
                    timeout=500,
                )
                response.raise_for_status()
                reply = response.json()["reply"]
            except requests.exceptions.RequestException as e:
                reply = f"⚠️ Couldn't reach the agent: {e}"

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})