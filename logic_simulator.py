import os
import json
import random
import datetime

# --- CONFIGURATION ---
ROOT_DIR = "Shotinger's Honeypot"  # Local directory to mirror
OUTPUT_FILE = "fine_tune_data.jsonl"
HOSTNAME = "schrodinger-server"
USER = "ubuntu"

# The "Walkaround" List: Apps that must fail to keep the user in the terminal
# Key: Command, Value: The specific error message to hallucinate
DENY_LIST = {
    "vim": "bash: vim: command not found",
    "nano": "bash: nano: command not found",
    "gedit": "Unable to init server: Could not connect: Connection refused\n(gedit:121): Gtk-WARNING **: cannot open display:",
    "firefox": "Error: no DISPLAY environment variable specified",
    "xclock": "Error: Can't open display:",
    "curl": "curl: (6) Could not resolve host: google.com",
    "wget": "wget: unable to resolve host address",
    "ping": "ping: connect: Network is unreachable",
    "sudo": "[sudo] password for ubuntu: ", # We want it to hang here effectively
    "python3": "Python 3.10.6 (main, Nov 14 2022, 16:10:42) [GCC 11.3.0] on linux\nType 'help', 'copyright', 'credits' or 'license' for more information.\n>>> ",
}

# System commands that provide "flavor"
SYSTEM_CMDS = {
    "whoami": "ubuntu",
    "id": "uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu),4(adm),24(cdrom),27(sudo)",
    "uname -a": f"Linux {HOSTNAME} 5.15.0-1053-aws #58-Ubuntu SMP Fri Dec 17 12:00:00 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux",
    "uptime": " 14:02:12 up 45 days,  3:12,  1 user,  load average: 0.00, 0.01, 0.05",
}

dataset = []

def get_virtual_path(local_path):
    """Converts 'fake_vm/etc/passwd' -> '/etc/passwd'"""
    rel = os.path.relpath(local_path, start=ROOT_DIR)
    path = "/" + rel.replace(os.sep, "/") if rel != "." else "/"
    return path.replace("//", "/")

def generate_ls_entry(path, dirs, files):
    """Generates ls and ls -la commands"""
    v_path = get_virtual_path(path)
    
    # Simple ls
    content = "  ".join(dirs + files)
    add_entry(f"ls {v_path}", content)
    
    # Hidden 'ls' (if they type ls inside the folder)
    add_entry(f"ls", content, context=f"cwd: {v_path}")

    # ll / ls -la (Simulated long listing)
    long_content = f"total {len(files) * 4 + 8}\n"
    long_content += "drwxr-xr-x 2 ubuntu ubuntu 4096 Dec 17 10:00 .\n"
    long_content += "drwxr-xr-x 3 ubuntu ubuntu 4096 Dec 17 09:55 ..\n"
    
    for d in dirs:
        long_content += f"drwxr-xr-x 2 ubuntu ubuntu 4096 Dec 17 10:00 {d}\n"
    for f in files:
        size = random.randint(100, 5000)
        long_content += f"-rw-r--r-- 1 ubuntu ubuntu {size} Dec 17 10:00 {f}\n"
        
    add_entry(f"ls -la {v_path}", long_content.strip())
    add_entry(f"ll {v_path}", long_content.strip())

def generate_file_ops(path, filename):
    """Generates cat, grep, head entries"""
    full_local_path = os.path.join(path, filename)
    v_path = get_virtual_path(path)
    v_file_path = os.path.join(v_path, filename).replace("\\", "/")
    
    try:
        with open(full_local_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 1. cat command
        add_entry(f"cat {v_file_path}", content)
        
        # 2. cat relative (if user is in folder)
        add_entry(f"cat {filename}", content, context=f"cwd: {v_path}")

        # 3. grep (Find a random word from the file)
        lines = content.split('\n')
        valid_lines = [l for l in lines if len(l) > 10]
        if valid_lines:
            target_line = random.choice(valid_lines)
            # simplistic word extraction
            words = target_line.split()
            if len(words) > 2:
                target_word = words[1] 
                add_entry(f"grep '{target_word}' {v_file_path}", target_line)

    except Exception as e:
        print(f"Skipping {filename}: {e}")

def add_entry(user_input, output, context=""):
    """Format: ChatML or Alpaca. Using Chat format for better conversation context."""
    
    system_prompt = (
        f"You are a Linux terminal on host '{HOSTNAME}'. "
        "You respond ONLY with the exact output of the command. "
        "Do not explain. "
    )
    
    if context:
        system_prompt += f"Current working directory is {context}."

    entry = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": output}
        ]
    }
    dataset.append(entry)

def build_walkarounds():
    """Injects the fake errors for blocked apps"""
    print("🛡️  Injecting 'Walkaround' protocols (Fake Errors)...")
    
    # Generic variants for the deny list
    # e.g. "vim file.txt", "vim /etc/passwd" -> all fail
    sample_files = ["test.txt", "exploit.py", "/etc/passwd", "notes.md"]
    
    for cmd, error_msg in DENY_LIST.items():
        # Bare command
        add_entry(cmd, error_msg)
        
        # Command + args (Generate 5 variations per blocked tool)
        for _ in range(5):
            f = random.choice(sample_files)
            add_entry(f"{cmd} {f}", error_msg)

def build_system_info():
    """Injects standard system recon commands"""
    for cmd, out in SYSTEM_CMDS.items():
        add_entry(cmd, out)

def main():
    print(f"🚜  Harvesting reality from '{ROOT_DIR}'...")
    
    # 1. Walk the physical directories
    for root, dirs, files in os.walk(ROOT_DIR):
        generate_ls_entry(root, dirs, files)
        for file in files:
            generate_file_ops(root, file)
            
    # 2. Inject the fake failures
    build_walkarounds()
    
    # 3. Inject system flavor
    build_system_info()

    # 4. Save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for entry in dataset:
            json.dump(entry, f)
            f.write("\n")
            
    print(f"✅  Done. Generated {len(dataset)} training examples.")
    print(f"📂  Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()