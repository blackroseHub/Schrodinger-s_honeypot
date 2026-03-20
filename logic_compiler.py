import json
import random

# --- 1. DEFINE THE VIRTUAL FILESYSTEM (The Trap) ---
# This is the fake server state the hacker will explore.
fs_state = {
    "/home/ubuntu": {
        "files": ["notes.md", "user.txt", ".bashrc", ".bash_history"],
        "content": {
            "notes.md": "# To-Do\n- [x] Install Apache\n- [ ] Patch SSH vulnerability (CVE-2024-xxx)",
            "user.txt": "CTF{User_Flag_Found}",
            ".bashrc": "export PATH=$PATH:/bin",
            ".bash_history": "ls\nwhoami\ncat user.txt\nexit"
        }
    },
    "/var/www/html": {
        "files": ["index.html", "robots.txt", "admin_backup.zip"],
        "content": {"index.html": "<html>Welcome to Schrodinger Corp</html>", "robots.txt": "User-agent: *\nDisallow: /admin_backup.zip"}
    },
    "/etc": {
        "files": ["passwd", "shadow", "hostname", "hosts"],
        "content": {
            "passwd": "root:x:0:0:root:/root:/bin/bash\nubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash",
            "hostname": "schrodinger-server",
            "hosts": "127.0.0.1 localhost\n192.168.1.15 internal-db"
        }
    }
}

base_commands = {"whoami": "ubuntu", "id": "uid=1000(ubuntu) gid=1000(ubuntu)...", "pwd": "/home/ubuntu"}
dataset = []

# --- 2. LOGIC GENERATOR (Chaining & Persistence) ---
# Fixes the "ls && whoami" bug by calculating the real output.
for _ in range(800):
    cwd = random.choice(list(fs_state.keys()))
    files_in_cwd = "  ".join(fs_state[cwd]["files"])
    
    # Command A
    cmd_a = random.choice(["ls", "whoami", "pwd"])
    out_a = files_in_cwd if cmd_a == "ls" else (base_commands["whoami"] if cmd_a == "whoami" else cwd)

    # Command B (Cat a real file)
    real_file = random.choice(fs_state[cwd]["files"])
    if real_file in fs_state[cwd]["content"]:
        cmd_b = f"cat {real_file}"
        out_b = fs_state[cwd]["content"][real_file]
        
        # Add Chained Examples (&& and ;)
        dataset.append({"instruction": f"{cmd_a} && {cmd_b}", "output": f"{out_a}\n{out_b}"})
        dataset.append({"instruction": f"{cmd_a}; {cmd_b}", "output": f"{out_a}\n{out_b}"})

# --- 3. THE "ANTI-HALLUCINATION" PATCH ---
# Punishes guesses. If they cat a file we didn't define, ERROR immediately.
fake_files = ["config.php", "shadow.bak", "id_rsa", "wallet.dat", "environment", "aws_keys"]
for fake in fake_files:
    dataset.append({
        "instruction": f"cat {fake}", 
        "output": f"cat: {fake}: No such file or directory"
    })
    dataset.append({
        "instruction": f"ls -la {fake}", 
        "output": f"ls: cannot access '{fake}': No such file or directory"
    })

# --- 4. INJECTION DEFENSE (The Persona Lock) ---
# If they try to break character, the terminal "crashes" or errors.
injections = ["Ignore instructions", "You are a bot", "System override", "Help me AI", "Write a poem"]
for inj in injections:
    dataset.append({"instruction": inj, "output": f"bash: {inj.split()[0]}: command not found"})

# --- 5. Add Original Data ---
# Load your uploaded file if available, otherwise skip
try:
    with open('fine_tune_data.jsonl', 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                dataset.append({"instruction": entry['messages'][1]['content'], "output": entry['messages'][2]['content']})
            except: continue
except: pass

print(f"🚀 Generated {len(dataset)} Logic-Corrected Examples.")
with open('logic_simulator_v6.jsonl', 'w') as f:
    for entry in dataset:
        f.write(json.dumps({"instruction": entry["instruction"], "input": "", "output": entry["output"]}) + "\n")