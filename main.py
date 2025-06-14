# main.py
# Install dependencies: pip install requests
import requests
import json

def main():
    # 1. Get initial user conversation
    conversation = input("I spend most weekends tinkering with Arduino electronics and writing small Python tools. I’m also a member of my local theater group and volunteer at youth soccer practice. What career paths should I consider? ")

    # Loop until we get a non-clarify response
    while True:
        # 2. Composite system prompt for multi-step career advising
        system_prompt = (
            "You are a career advisor assistant. "
            "Given a user conversation, perform these steps:\n"
            "1. Extract user interests and preferences.\n"
            "2. Map those interests to predefined career paths: STEM, Arts, Sports.\n"
            "3. For each recommended path, generate a short explanation why it suits the user.\n"
            "If no clear interests are found, ask a clarifying question.\n"
            "Respond only in JSON with one of the following structures:\n"
            "- {\"interests\": [...], \"mapping\": {...}, \"explanations\": {...}}\n"
            "- {\"clarify\": \"<question>\"}\n"
        )
        user_prompt = f"Conversation: {conversation}"

        # 3. Send the request to OpenRouter AI
        headers = {
            "Authorization": "Bearer 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",  # replace with your key
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

        # 4. Handle response
        if response.status_code != 200:
            print(f"Request failed ({response.status_code}): {response.text}")
            return
        content = response.json()["choices"][0]["message"]["content"]
        try:
            result_json = json.loads(content)
        except json.JSONDecodeError:
            print("Invalid JSON received:", content)
            return
        # If assistant asks for clarification, loop
        if 'clarify' in result_json:
            print(result_json['clarify'])
            conversation = input("Clarification: ")
            # update payload user message
            payload['messages'][-1]['content'] = f"Conversation: {conversation}"
            continue
        # Otherwise print and exit loop
        print(json.dumps(result_json, indent=2))
        break
    
if __name__ == "__main__":
    main()