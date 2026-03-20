import os
import sys
import datetime
from openai import OpenAI
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init()

# --- CONFIGURATION ---
# LM Studio Local Server Port (Default is 1234)
BASE_URL = "http://localhost:1234/v1" 
API_KEY = "lm-studio" # Not strictly checked by local LM Studio, but required by client

HOSTNAME = "schrodinger-server"
USER = "root"

# --- CLIENT SETUP ---
# We use the OpenAI client because LM Studio mimics the OpenAI API
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# Context history
# We enforce the "Linux Terminal" persona in the system prompt
history = [
    {
        "role": "system", 
        "content": "You are a Linux terminal. Output only the result of the command provided by the user. Do not explain. Do not use markdown blocks. Be concise."
    }
]

def get_prompt():
    """Returns the formatted prompt: root@hostname:~#"""
    # Fore.GREEN for user/host, Fore.BLUE for path (~), Reset for separators
    return f"{Fore.GREEN}{USER}@{HOSTNAME}{Style.RESET_ALL}:{Fore.BLUE}~{Style.RESET_ALL}# "

def get_formatted_date():
    return datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")

def main():
    # Clear screen on start (Linux/Mac 'clear', Windows 'cls')
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Standard Ubuntu-style login banner
    print("Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-91-generic x86_64)\n")
    print(" * Documentation:  https://help.ubuntu.com")
    print(" * Management:     https://landscape.canonical.com")
    print(" * Support:        https://ubuntu.com/advantage\n")
    print(f"System information as of {get_formatted_date()}\n")

    while True:
        try:
            # 1. Get User Input
            # We use 'input' which naturally pauses for the user
            user_input = input(get_prompt())

            # 2. Handle Empty Inputs
            if user_input.strip() == "":
                continue

            # 3. Handle Local "Meta" Commands (Exit, Clear)
            if user_input.strip().lower() in ['exit', 'quit', 'logout']:
                print("logout")
                break
            
            if user_input.strip().lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            # 4. Add to history
            history.append({"role": "user", "content": user_input})

            # 5. Fetch from LM Studio
            try:
                completion = client.chat.completions.create(
                    model="local-model", # ID doesn't matter for local LM Studio
                    messages=history,
                    temperature=0.1, # Low temperature = deterministic, computer-like responses
                    stream=False     # False = Instant output (Professional feel)
                )
                
                response_text = completion.choices[0].message.content
                
                # 6. Print Response Cleanly
                if response_text:
                    # Strip standard markdown code blocks if the model accidentally adds them
                    clean_text = response_text.replace("```bash", "").replace("```", "").strip()
                    print(clean_text)
                
                # 7. Update history so the model remembers context (e.g., 'cd' commands)
                history.append({"role": "assistant", "content": response_text})

            except Exception as api_error:
                # Mimic a bash error
                print(f"{Fore.RED}bash: connection refused: {api_error}{Style.RESET_ALL}")
                print(f"{Fore.RED}(Make sure LM Studio server is running on port 1234){Style.RESET_ALL}")

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully like a real terminal (New prompt line)
            print("\n")
            continue

if __name__ == "__main__":
    main()