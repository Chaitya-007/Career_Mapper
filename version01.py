# interface.py

# Streamlit-based frontend for career advisor
import os
import streamlit as st
import requests
import json
from dotenv import load_dotenv
load_dotenv()

# Load API key
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    st.error("Set the OPENROUTER_API_KEY environment variable with your API key.")
    st.stop()

# Function to call the AI and get JSON response
def get_career_advice(conversation):
    system_prompt = (
        "You are a career advisor assistant. "
        "Given a user conversation, perform these steps:\n"
        "1. Extract user interests and preferences.\n"
        "2. Map those interests to suitable career paths based on the interests provided.\n"
        "3. For each recommended path, generate a short explanation why it suits the user.\n"
        "If no clear interests are found, ask a clarifying question.\n"
        "Respond only in JSON with one of the following structures:\n"
        "- {\"interests\": [...], \"mapping\": {...}, \"explanations\": {...}}\n"
        "- {\"clarify\": \"<question>\"}\n"
    )
    user_prompt = f"Conversation: {conversation}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload)
    )
    if response.status_code != 200:
        return {"error": f"Request failed ({response.status_code})"}
    content = response.json()["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}

# Streamlit UI
st.title("Career Advisor")
st.write("Enter your conversation below to get career suggestions.")

# Initialize session state for looping clarification
if 'clarify_question' not in st.session_state:
    st.session_state.clarify_question = None
if 'conversation' not in st.session_state:
    st.session_state.conversation = ''

# Input area: show clarification prompt if needed, then input box
if st.session_state.clarify_question:
    st.info(f"Assistant: {st.session_state.clarify_question}")
prompt_label = st.session_state.clarify_question or "Conversation"
st.session_state.conversation = st.text_area(prompt_label, value=st.session_state.conversation)

# When user clicks, call AI
if st.button("Get Advice"):
    result = get_career_advice(st.session_state.conversation)
    # Handle API or parsing errors first
    if "error" in result:
        st.error(result["error"])
    # If assistant asks for clarification, update prompt and loop
    elif "clarify" in result:
        # Store clarification question and loop
        st.session_state.clarify_question = result['clarify']
    else:
        # Clear clarify state and display final results
        st.session_state.clarify_question = None
        st.subheader("Extracted Interests")
        st.write(result["interests"])
        st.subheader("Career Path Mapping")
        st.json(result["mapping"])
        st.subheader("Explanations")
        st.json(result["explanations"])