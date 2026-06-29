import os
import subprocess
import json
import sys
from cerebras.cloud.sdk import Cerebras

# Console ANSI Colors (Standard macOS/Linux terminal compatible, no external packages needed)
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

# 1. Secure API Key handling for open source
api_key = os.environ.get("CEREBRAS_API_KEY")

if not api_key:
    print(f"{COLOR_YELLOW}CEREBRAS_API_KEY environment variable not found.{COLOR_RESET}")
    user_key = input("Enter your Cerebras API key (starts with csk-): ").strip()
    if not user_key:
        print(f"{COLOR_RED}Error: API key is required to run the agent. Exiting.{COLOR_RESET}")
        sys.exit(1)
    os.environ["CEREBRAS_API_KEY"] = user_key
    api_key = user_key

try:
    client = Cerebras()
except Exception as e:
    print(f"{COLOR_RED}Failed to initialize Cerebras SDK: {e}{COLOR_RESET}")
    sys.exit(1)

# Define System Prompt
SYSTEM_PROMPT = """You are an autonomous AI coding agent operating in the user's workspace.
You can execute files, create/edit code, and run shell commands by outputting JSON tool calls.

Available Tools:
1. {"tool": "write_file", "path": "file_path", "content": "file_content"}
   Create or overwrite a file with contents.
2. {"tool": "read_file", "path": "file_path"}
   Read the contents of an existing file.
3. {"tool": "run_command", "command": "shell_command", "background": true/false}
   Execute a terminal command. Set "background" to true for long-running services (like http.server, web servers, or watchers) so they do not block the agent loop thread.
4. {"tool": "reply", "message": "response_to_user"}
   Send a message or explanation back to the user when your task is complete.

Rules:
1. Respond ONLY with a single JSON object. Do NOT wrap the JSON in markdown code blocks (do NOT use ```json).
2. Do NOT output any text, descriptions, or explanations outside the JSON.
3. You can execute multiple tool calls sequentially. For example, run a command, inspect the error output, modify a file, and run it again. When finished, call the "reply" tool.
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

print(f"{COLOR_CYAN}{COLOR_BOLD}====================================================")
print("   ⚡ CerebrasCoder: Autonomous Developer Agent ⚡")
print(f"===================================================={COLOR_RESET}")
print(f"Powered by {COLOR_BOLD}gemma-4-31b{COLOR_RESET} on Cerebras CS-3 (1,500+ tok/s).")
print("Ask the agent to write files, run tests, or execute terminal commands.")
print("Type 'exit' to quit.\n")

while True:
    try:
        user_input = input(f"{COLOR_BOLD}You:{COLOR_RESET} ").strip()
        if user_input.lower() in ['exit', 'quit']:
            print(f"\n{COLOR_BLUE}Exiting agent. Goodbye!{COLOR_RESET}")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # Agent thinking & execution loop
        while True:
            # Dynamically scan directory to keep the context active in system prompt
            try:
                files = [f for f in os.listdir('.') if os.path.isfile(f) and not f.startswith('.')]
                folders = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.') and d != '__pycache__']
                dir_context = f"\n\n[Active Workspace Contents]:\nFiles: {', '.join(files)}\nSubdirectories: {', '.join(folders)}"
            except Exception:
                dir_context = ""

            messages[0]["content"] = SYSTEM_PROMPT + dir_context

            # Call Cerebras API (non-streamed to get full valid JSON block)
            response = client.chat.completions.create(
                model="gemma-4-31b",
                messages=messages,
                stream=False
            )
            
            raw_response = response.choices[0].message.content.strip()
            
            # Clean response of markdown wraps if AI included them by mistake
            if raw_response.startswith("```"):
                lines = raw_response.split("\n")
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    raw_response = "\n".join(lines[1:-1]).strip()

            try:
                action = json.loads(raw_response)
            except Exception as e:
                # Feed parsing error back to LLM to correct itself
                err_msg = f"Error: Output was not valid JSON. You must respond only with a single JSON tool call. Parse error: {e}. Raw content: {raw_response}"
                messages.append({"role": "user", "content": err_msg})
                continue

            tool_name = action.get("tool")

            # Handle Reply Tool
            if tool_name == "reply":
                print(f"\n{COLOR_GREEN}{COLOR_BOLD}Agent:{COLOR_RESET} {action.get('message')}\n")
                messages.append({"role": "assistant", "content": raw_response})
                break

            # Handle Write File Tool
            elif tool_name == "write_file":
                filepath = action.get("path")
                content = action.get("content")
                
                print(f"\n{COLOR_BLUE}[Agent Action]:{COLOR_RESET} Writing file '{filepath}'...")
                
                parent_dir = os.path.dirname(filepath)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": f"Tool output: File '{filepath}' written successfully."})

            # Handle Read File Tool
            elif tool_name == "read_file":
                filepath = action.get("path")
                print(f"\n{COLOR_BLUE}[Agent Action]:{COLOR_RESET} Reading file '{filepath}'...")
                
                if not os.path.exists(filepath):
                    result = f"Tool output: File '{filepath}' does not exist."
                else:
                    with open(filepath, "r", encoding="utf-8") as f:
                        file_data = f.read()
                    result = f"Tool output: File '{filepath}' contents:\n{file_data}"
                
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": result})

            # Handle Run Command Tool
            elif tool_name == "run_command":
                cmd = action.get("command")
                is_bg = action.get("background") in [True, "true", "True"]
                
                if is_bg:
                    print(f"\n{COLOR_BLUE}[Agent Action - Run Background Command]:{COLOR_RESET} Starting '{cmd}' in background...")
                    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    output = f"Tool output: Started background process for command '{cmd}' (PID: {proc.pid})."
                    print(f"{COLOR_GREEN}Background Process Started! (PID: {proc.pid}){COLOR_RESET}")
                else:
                    print(f"\n{COLOR_BLUE}[Agent Action - Run Command]:{COLOR_RESET} Executing '{cmd}'...")
                    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    output = f"Tool output: Stdout:\n{res.stdout}\nStderr:\n{res.stderr}"
                    
                    if res.stdout:
                        print(f"{COLOR_GREEN}Command Output (Stdout):{COLOR_RESET}\n{res.stdout}")
                    if res.stderr:
                        print(f"{COLOR_RED}Command Output (Stderr):{COLOR_RESET}\n{res.stderr}")
                
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": output})
            
            else:
                err_msg = f"Tool output: Unknown tool name '{tool_name}'."
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": err_msg})

    except KeyboardInterrupt:
        print(f"\n\n{COLOR_YELLOW}Session interrupted. Goodbye!{COLOR_RESET}")
        break
    except Exception as e:
        print(f"\n{COLOR_RED}An error occurred: {e}{COLOR_RESET}\n")
