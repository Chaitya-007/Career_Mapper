# Install dependencies: pip install gradio requests python-dotenv
# Gradio chatbot for career advisor

import os
import gradio as gr
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY in your environment.")

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/devstral-small:free"

# Core function to call the AI
def get_career_advice(conversation: str):
    system_prompt = (
        "You are a career advisor assistant. Given a user conversation, perform these steps:\n"
        "1. Extract user interests and preferences.\n"
        "2. Map those interests to suitable career paths.\n"
        "3. Generate a short explanation for each recommended path.\n"
        "If no clear interests are found, ask a clarifying question.\n"
        "Respond only in JSON with keys 'interests', 'mapping', 'explanations', or with 'clarify'."
    )
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": conversation}
        ]
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(BASE_URL, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        return f"Error {response.status_code}: {response.text}"
    text = response.json()["choices"][0]["message"]["content"]
    return text

# Gradio chatbot interface
def chat_history(user_message, history):
    # Each message must be a dict with 'role' and 'content'
    history = history or []
    # Append user message
    history.append({"role": "user", "content": user_message})
    # Get assistant reply
    assistant_reply = get_career_advice(user_message)
    history.append({"role": "assistant", "content": assistant_reply})
    return history, history

with gr.Blocks() as demo:
    gr.Markdown("# Career Advisor Chatbot")
    chatbot = gr.Chatbot(type='messages')
    msg = gr.Textbox(placeholder="Enter your message here...", show_label=False)
    clear = gr.Button("Clear")

    msg.submit(chat_history, [msg, chatbot], [chatbot, chatbot])
    clear.click(lambda: [], None, chatbot)

if __name__ == "__main__":
    demo.launch()
