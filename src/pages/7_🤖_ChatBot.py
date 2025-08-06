import requests
import streamlit as st
import os
from dotenv import load_dotenv
from utils.db import DataBaseManagement

load_dotenv()
PROXY_URL = os.getenv("CF_WORKER_URL")
st.set_page_config(page_title="ChatBot", page_icon=":bot:")

def chatbot():
    """
    A Streamlit-based Gemini chatbot interface.

    Features:
    - Displays an interactive chat UI with persistent chat history using Streamlit session state.
    - Requires user authentication before enabling the chatbot.
    - Allows users to clear chat history with a single button.
    - Accepts user input via a chat input field and displays messages for both user and assistant.
    - Sends user prompts to the Gemini API via a proxy URL and retrieves responses.
    - Handles API errors gracefully by showing an error message to the user.
    - Guides unauthenticated users to complete their profile before using the chatbot.
"""
    st.title("💬 Gemini Chatbot")
    st.caption("🚀 A Streamlit chatbot powered by Gemini")
    if "user_email" in st.session_state:
        if user_authentication(st.session_state.user_id, st.session_state.user_email):
                if st.button("🗑️ Clear Chat History"):
                    st.session_state["messages"] = [{"role": "assistant", 
                                                    "content": "Chat history cleared! How can I help you now?"}]
                if "messages" not in st.session_state:
                    st.session_state["messages"] = [{"role": "assistant",
                                                    "content": "Hi! I'm Gemini . Ask me anything!"}]

                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

                # Chat input
                if prompt := st.chat_input("Type your message here..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.write(prompt)

                    with st.spinner("Gemini is thinking..."):
                        payload = {"contents": [{"parts": [{"text": prompt}]}]}
                        try:
                            res = requests.post(PROXY_URL, json=payload, timeout=30)
                            data = res.json()
                            response = data["candidates"][0]["content"]["parts"][0]["text"]
                        except Exception as e:
                            response = f"❌ Error: {e}"

                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.write(response)
    else:
        st.warning("Please fill user profile form in 'User Profile' page first.")
        st.markdown("[Go to User Profile page](User_Profile_SignIn)")


def user_authentication(user_id, user_email):
    """Checks if the user with the given user_id and user_email exists and is authorized.
    Args:
        user_id (int): Unique identifier for the user.
        user_email (str): Email address of the user.
    Returns:
        bool: True if the user is authorized, False otherwise.
    """
    db = DataBaseManagement()
    profile = db.get_user_profile(user_id=user_id, email=user_email)
    return bool(profile)


if __name__ == "__main__":
    chatbot()
