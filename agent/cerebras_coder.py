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

client = Cerebras()

print("=== Cerebras Coder: Live File Writer & Editor ===")
print("Type 'exit' to quit.\n")

while True:
    try:
        # 1. Get target file path
        filepath = input("Enter target filename (e.g. math_utils.py or index.html): ").strip()
        if filepath.lower() == 'exit':
            break
        if not filepath:
            continue

        # 2. Get instructions
        instructions = input(f"What should I write/edit inside '{filepath}'?: ").strip()
        if instructions.lower() == 'exit':
            break
        if not instructions:
            continue

        # 3. Check if file already exists to handle editing
        current_content = ""
        is_edit = os.path.exists(filepath)
        
        if is_edit:
            print(f"Reading existing content of '{filepath}' for context...")
            with open(filepath, "r", encoding="utf-8") as f:
                current_content = f.read()

        # 4. Define AI Prompt context
        system_prompt = (
            "You are a local AI code-writing agent. Your task is to output the final, complete code "
            "that should be written into the file. Output ONLY the raw source code. "
            "Do NOT wrap the code in markdown formatting (do NOT use ```python or ```html blocks). "
            "Do NOT write introductions, notes, or explanations. Start printing code immediately."
        )

        user_content = f"Target File: {filepath}\n"
        if is_edit:
            user_content += f"--- Existing File Content ---\n{current_content}\n"
            user_content += f"--- Edit Instructions ---\n{instructions}\n"
        else:
            user_content += f"--- Generation Instructions ---\n{instructions}\n"

        print(f"\n[Cerebras Gemma 4] Compiling and writing code directly to '{filepath}'...\n")

        # 5. Call streaming completions
        stream = client.chat.completions.create(
            model="gemma-4-31b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            stream=True
        )

        # 6. Stream write content to the file in real-time
        # Create directories if they do not exist
        parent_dir = os.path.dirname(filepath)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        full_code = ""
        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    # Print to console so user can see it streaming
                    print(content, end="", flush=True)
                    # Write to file
                    f.write(content)
                    full_code += content

        print(f"\n\n✔ SUCCESS: Successfully compiled and wrote {len(full_code)} characters to '{filepath}'!\n")
        print("-" * 50 + "\n")

    except KeyboardInterrupt:
        print("\nSession interrupted. Goodbye!")
        break
    except Exception as e:
        print(f"\nAn error occurred: {e}\n")