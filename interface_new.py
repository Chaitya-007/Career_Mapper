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
        # Treat plain-text replies as clarification prompts
        return {"clarify": content.strip()}  

# Streamlit UI
st.title("Career Advisor")
st.write("Enter your conversation below to get career suggestions.")

# Initialize session state
for var, default in [
    ('conversation_input', ''),
    ('clarify_question', None),
    ('clarification_response', ''),
    ('final_result', None),
    ('error_message', None)
]:
    if var not in st.session_state:
        st.session_state[var] = default

# --- Conversation Form ---
with st.form('conversation_form'):
    convo = st.text_area('Conversation:', value=st.session_state.conversation_input)
    submit_conv = st.form_submit_button('Submit Conversation')
    if submit_conv:
        # Call AI with initial conversation
        st.session_state.conversation_input = convo
        st.session_state.error_message = None
        st.session_state.final_result = None
        result = get_career_advice(convo)
        if 'error' in result:
            st.session_state.error_message = result['error']
            st.session_state.clarify_question = None
        elif 'clarify' in result:
            st.session_state.clarify_question = result['clarify']
            st.session_state.clarification_response = ''
        else:
            st.session_state.final_result = result
            st.session_state.clarify_question = None
            st.session_state.clarification_response = ''

# --- Clarification Form ---
if st.session_state.clarify_question:
    st.write(f"**Assistant:** {st.session_state.clarify_question}")
    with st.form('clarify_form'):
        resp = st.text_input('Your response:', value=st.session_state.clarification_response)
        submit_clar = st.form_submit_button('Submit Clarification')
        if submit_clar:
            st.session_state.clarification_response = resp
            # Call AI with clarification
            st.session_state.error_message = None
            result = get_career_advice(resp)
            if 'error' in result:
                st.session_state.error_message = result['error']
            elif 'clarify' in result:
                st.session_state.clarify_question = result['clarify']
                st.session_state.clarification_response = ''
            else:
                st.session_state.final_result = result
                st.session_state.clarify_question = None
                st.session_state.clarification_response = ''

# Display errors
if st.session_state.error_message:
    st.error(st.session_state.error_message)

# Display final results
if st.session_state.final_result:
    res = st.session_state.final_result
    st.subheader("Extracted Interests")
    st.write(res.get("interests"))
    st.subheader("Career Path Mapping")
    st.json(res.get("mapping"))
    st.subheader("Explanations")
    st.json(res.get("explanations"))