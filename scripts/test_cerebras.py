import os
from cerebras.cloud.sdk import Cerebras

# Secure API Key handling
api_key = os.environ.get("CEREBRAS_API_KEY")
if not api_key:
    print("CEREBRAS_API_KEY environment variable not found.")
    api_key = input("Please enter your Cerebras API key: ").strip()
    if not api_key:
        print("Error: API key required.")
        exit(1)
    os.environ["CEREBRAS_API_KEY"] = api_key

client = Cerebras()

try:
    response = client.chat.completions.create(
        model="gemma-4-31b",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("Connection successful!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Connection failed: {e}")