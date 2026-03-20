import os
import random
import datetime

ROOT = "Shotinger's Honeypot"
TODAY = datetime.date.today().strftime("%b %d")

# --- 1. THE NARRATIVE ---
# The story: A web server (Apache) that was hacked via a weak admin password.
# The user lands in /home/ubuntu and must find how the attacker got in.

# --- 2. FILE SYSTEM BLUEPRINT ---
file_system = {
    # === USER HOME (The Starting Point) ===
    "home/ubuntu/user.txt": "CTF{Level_1_User_Access_Verified}",
    "home/ubuntu/.bash_history": "ls\ncd /var/www/html\nsudo service apache2 restart\ncat /var/log/auth.log\nssh-keygen\n",
    "home/ubuntu/.bashrc": "# ~/.bashrc: executed by bash(1) for non-login shells.\nexport PATH=$PATH:/home/ubuntu/bin\nalias ll='ls -alF'",
    "home/ubuntu/notes.md": "# To-Do\n- [x] Install Apache\n- [ ] Update firewall rules (URGENT)\n- [ ] Rotate root password",

    # === WEB SERVER (The Distraction) ===
    "var/www/html/index.html": "<html>\n<head><title>Under Construction</title></head>\n<body><h1>Welcome to My Server</h1><p>Nothing to see here yet.</p></body>\n</html>",
    "var/www/html/robots.txt": "User-agent: *\nDisallow: /admin\nDisallow: /secrets",
    "var/www/html/admin/config.php": "<?php\n// TODO: Remove this before production\n$db_user = 'admin';\n$db_pass = 'SuperSecurePass2024!'; // Changed this after the incident\n?>",
    
    # === CONFIGURATION (The "Realism") ===
    "etc/hostname": "web-prod-01",
    "etc/timezone": "Etc/UTC",
    "etc/hosts": "127.0.0.1 localhost\n127.0.1.1 web-prod-01\n192.168.1.50 db-backup-internal",
    "etc/ssh/sshd_config": "# Package generated configuration file\nPermitRootLogin no\nPasswordAuthentication yes\nChallengeResponseAuthentication no\nUsePAM yes\n",
    "etc/passwd": (
        "root:x:0:0:root:/root:/bin/bash\n"
        "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
        "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n"
        "ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash\n"
        "hacker:x:1337:1337::/home/hacker:/bin/bash\n" # A subtle clue!
    ),
    "etc/shadow": "root:*:19777:0:99999:7:::\nubuntu:$6$hJ8...:19777:0:99999:7:::\n", # Permission denied simulation requires careful prompt handling later

    # === LOGS (The Clues) ===
    "var/log/syslog": f"{TODAY} 08:15:01 web-prod-01 systemd[1]: Started Apache2 Web Server.\n{TODAY} 08:16:22 web-prod-01 kernel: [ 1234.56] UFW BLOCK IN=eth0 OUT= MAC=... SRC=10.0.0.5 DST=192.168.1.5",
    "var/log/auth.log": (
        f"{TODAY} 10:00:01 web-prod-01 sshd[452]: Failed password for root from 203.0.113.42 port 44322 ssh2\n"
        f"{TODAY} 10:00:05 web-prod-01 sshd[452]: Failed password for root from 203.0.113.42 port 44322 ssh2\n"
        f"{TODAY} 10:02:11 web-prod-01 sshd[455]: Accepted password for hacker from 203.0.113.42 port 5566 ssh2\n" # The smoking gun
    ),

    # === ROOT (The Goal) ===
    "root/root.txt": "CTF{Congratulations_You_Found_The_Kernel_Secret}",
    "root/do_not_read.txt": "If you are reading this, you bypassed the sudo check. Good job.",
}

# === BINARIES (The "Fake" Executables) ===
# We create empty files for common commands so 'ls /bin' isn't empty.
# If they 'cat' these, the content simulates a binary file read.
bin_tools = ["ls", "cat", "grep", "sudo", "mkdir", "rm", "cp", "mv", "touch", "vi", "nano", "tar", "gzip", "ping", "python3"]
for tool in bin_tools:
    file_system[f"bin/{tool}"] = f"ELF 64-bit LSB pie executable... [BINARY DATA CANNOT BE DISPLAYED]"

# === TMP (The Noise) ===
# Random junk files
for i in range(5):
    file_system[f"tmp/sess_{random.randint(1000,9999)}"] = "session_data_garbage_value_x8237"

def build_world():
    print(f"🏗️  Constructing Versatile Honeypot in './{ROOT}'...")
    
    if os.path.exists(ROOT):
        print(f"⚠️  Note: updating existing '{ROOT}' folder.")

    for path, content in file_system.items():
        # Convert to Windows paths
        parts = path.split("/")
        full_path = os.path.join(ROOT, *parts)
        
        # Make directories
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write content
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing {path}: {e}")

    print("✅ System Ready.")
    print("   - Web Root: /var/www/html")
    print("   - Logs: /var/log")
    print("   - Binaries: /bin (Fake ELF files)")

if __name__ == "__main__":
    build_world()