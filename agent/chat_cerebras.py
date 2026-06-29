import os
from cerebras.cloud.sdk import Cerebras

# Ensure API Key is active via environment variable
api_key = os.environ.get("CEREBRAS_API_KEY")

if not api_key:
    print("CEREBRAS_API_KEY environment variable not found.")
    api_key = input("Please enter your Cerebras API key (starts with csk-): ").strip()
    if not api_key:
        print("Error: API key is required to run this script.")
        exit(1)
    os.environ["CEREBRAS_API_KEY"] = api_key

# 1. Initialize client
client = Cerebras()

# 2. Setup the message history list
messages = [
    {
        "role": "system", 
        "content": "You are a helpful AI assistant. Keep responses short and conversational."
    }
]

print("=== Starting Cerebras Chat (gemma-4-31b) ===")
print("Type 'exit' or 'quit' to end the chat.\n")

while True:
    try:
        # Get user message
        user_input = input("You: ").strip()
        
        # Check exit conditions
        if user_input.lower() in ['exit', 'quit']:
            print("\nEnding chat session. Goodbye!")
            break
            
        if not user_input:
            continue
            
        # Append user message to history
        messages.append({"role": "user", "content": user_input})
        
        print("\nAssistant: ", end="", flush=True)
        
        # Call streaming chat API with message history
        stream = client.chat.completions.create(
            model="gemma-4-31b",
            messages=messages,
            stream=True
        )
        
        # Stream response chunks to terminal and collect full reply
        full_reply = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
                full_reply += content
        print("\n")
        
        # Append assistant's response to history so they remember it next turn
        messages.append({"role": "assistant", "content": full_reply})
        
    except KeyboardInterrupt:
        print("\n\nSession interrupted. Goodbye!")
        break
    except Exception as e:
        print(f"\nAn error occurred: {e}\n")