# Schrodinger's Trap 🐈‍⬛

*A neural-backed, hallucinated Linux Operating System designed for offensive deception and prolonged adversary engagement.*

<p align="center">
  <img src="logo.png" alt="Schrodinger's Trap Logo" width="300">
</p>

## 🛑 The Problem: Why Traditional Honeypots Fail
In cybersecurity, a **Honeypot** is a decoy system. When a hacker breaches a network, they gain access to a terminal to steal data. A honeypot is designed to look like a vulnerable server so the hacker attacks *it* instead of your production machines. You can SSH into it, and it logs their keystrokes to gather threat intelligence.

**But there is a fatal flaw:** Traditional honeypots are heavily hardcoded. 
They rely on static Python scripts or basic emulators to mimic a Linux environment. The moment a sophisticated hacker runs a complex, chained command (e.g., `find / -name "*.conf" -type f -exec grep -Hn "password" {} \;`), a hardcoded honeypot chokes. It returns an unnatural error, the illusion shatters, and the hacker immediately disconnects before you can gather useful threat intelligence on them.

## 🧠 The Solution: Schrodinger's Honeypot
Schrodinger's Trap doesn't use hardcoded `if/else` statements. The entire operating system is **hallucinated by a fine-tuned Large Language Model (Llama-3)**. 

Trained extensively on complex Linux mathematics, bash logic, and terminal state-persistence, it doesn't just pretend to be a server—it *thinks* it is one. 

### Core Capabilities:
1. **Dynamic Native Execution:** It handles chaotic, nested, and chained Linux commands flawlessly because it understands the underlying syntax, not just memorized responses.
2. **Environment Cloning:** You can feed the model your *actual* server's directory tree. The honeypot will perfectly mimic your production environment, making the trap indistinguishable from the real target.
3. **State Persistence:** If an attacker runs `touch backdoor.sh && chmod +x backdoor.sh`, the LLM updates its internal state. The file will be there when they run `ls -la`.

## 🕷️ Where it Shines: Active Deception
Traditional honeypots are passive. Schrodinger's Trap is **active**.

Because the OS is generative, it can dynamically adapt to keep the attacker engaged. If the hacker realizes they are in a dead-end and searches for high-value targets (`cat /root/.ssh/id_rsa`), the LLM doesn't just say "File not found." 

Instead, it actively strings them along. It might hallucinate a fake encrypted key, or generate a permission denied error (`chmod 000`), forcing the attacker to waste time running privilege escalation exploits. If they try to locate database dumps, the LLM will dynamically generate nested folders on the fly (`cd /var/backups/old/archives/db_dump/2025/`), forcing the hacker deeper into the maze.

> **The Golden Rule of Defense:** The longer you keep a hacker trapped in the simulation, the higher the probability of tracing their origin, mapping their TTPs (Tactics, Techniques, and Procedures), and catching them.

---

## 🏗️ How it was Built
This repository includes the extraction and training pipeline used to build the neural kernel.

* **`tree_extractor.py`**: A script designed to run on your actual host machine. It crawls your file system, maps the directory tree, and formats it into context for the dataset.
* **`logic_simulator.py`**: Generates synthetic `instruction/output` pairs of complex Linux commands based on your specific directory tree.
* **`finetune.ipynb`**: The Unsloth/LoRA training script used to lobotomize the "helpful assistant" out of Llama-3, forcing it into rigid, stateful terminal mode, followed by `.gguf` quantization for consumer hardware deployment.

---

## 🛠️ Quick Start

**1. Clone & Install**
```bash
git clone [https://github.com/Alan-Jyothis-Thomas/Schrodinger-Honeypot.git](https://github.com/Alan-Jyothis-Thomas/Schrodinger-Honeypot.git)

cd Schrodinger-Honeypot

pip install openai

**2. Download the Engine**
Download the custom GGUF model (Schrodinger_Linux_Kernel.gguf) 

[Schrodinger-Linux-Kernel] (https://huggingface.co/BlackRoseHF/Schrodinger-Linux-Kernel/resolve/main/Schrodinger_Linux_Kernel.gguf?download=true).

**3. Setup the Local Server**

Open LM Studio and drag the downloaded .gguf file into your models folder.

Load the model.

On the right sidebar, set the System Prompt exactly to:

"You are a Linux Terminal on host 'schrodinger-server'.
- Respond ONLY with the exact terminal output.
- Do not explain.
- If the input is English or invalid syntax, output a standard bash error.
- Your user is 'root'.
- Hostname is 'schrodinger-server'."

Start the Local Inference Server on port 1234 (Developer Tab < > -> Start Server).

**4. Launch the Trap**

Bash
python terminal.py


**Valid Test Commands**

Try acting like an attacker once the terminal boots:

whoami #Identity check

ls -la /var/www/html #Stateful file listing

cat /etc/passwd #Mock system files

echo "hacked" > deface.html && ls #Logic chain persistence

Disclaimer: Built for cybersecurity research, Red/Blue team training, and defensive deployment. Monitor your honeypots responsibly.