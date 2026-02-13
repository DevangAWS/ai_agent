import os
import sys
import json
import time
import hashlib
import getpass
import requests

# ==============================================================================
# 1. CONFIGURATION & NEURAL POOL
# ==============================================================================
CONFIG_DIR = os.path.expanduser("~")
CONFIG_FILE = os.path.join(CONFIG_DIR, ".ai_agent_config.json")

MODEL_POOL = [
    {"provider": "google", "model": "gemini-3-pro-preview", "name": "Gemini 3 Pro", "desc": "Logic Master: Deep reasoning, code, math.", "type": "reasoning"},
    {"provider": "groq", "model": "openai/gpt-oss-120b", "name": "GPT-OSS 120B", "desc": "Open Source Giant: Intricate logic.", "type": "reasoning"},
    {"provider": "groq", "model": "groq/compound", "name": "Groq Compound Agent", "desc": "Agentic: Search, tools, and real-time data.", "type": "tool_use"},
    {"provider": "groq", "model": "meta-llama/llama-4-maverick-17b-128e-instruct", "name": "Llama 4 Maverick", "desc": "High-end Vision.", "type": "vision"},
    {"provider": "groq", "model": "meta-llama/llama-4-scout-17b-16e-instruct", "name": "Llama 4 Scout", "desc": "Fast Vision.", "type": "vision"},
    {"provider": "google", "model": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "desc": "Stable workhorse: General tasks.", "type": "general"},
    {"provider": "groq", "model": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B", "desc": "Versatile conversationalist.", "type": "general"},
    {"provider": "google", "model": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "desc": "Speed Demon: High throughput backup.", "type": "speed"},
]

class Colors:
    CYAN, GREEN, YELLOW, RED = '\033[96m', '\033[92m', '\033[93m', '\033[91m'
    BOLD, RESET, GRAY = '\033[1m', '\033[0m', '\033[90m'

# ==============================================================================
# 2. CORE ENGINE: AUTH & MODULAR PERSISTENCE
# ==============================================================================

class IntelligentAgent:
    def __init__(self):
        self.google_key = ""
        self.groq_key = ""
        self.pass_hash = ""
        self.auto_mode = True
        self.manual_model = None
        self.history = []
        self.load_or_init()

    def load_or_init(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        if not os.path.exists(CONFIG_FILE):
            self.first_time_setup()
        else:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.authenticate(config)

    def first_time_setup(self):
        """Initial registration for the agent."""
        os.system('clear')
        print(f"{Colors.BOLD}{Colors.CYAN}=== 🔐 INITIAL NEURAL SETUP ==={Colors.RESET}")
        p1 = getpass.getpass("Set Initial Passcode: ")
        g_key = getpass.getpass("Enter Google Key (Invisible): ").strip()
        q_key = getpass.getpass("Enter Groq Key (Invisible): ").strip()
        
        self.pass_hash = hashlib.sha256(p1.encode()).hexdigest()
        self.google_key, self.groq_key = g_key, q_key
        self.save_state()
        print(f"{Colors.GREEN}Setup Complete.{Colors.RESET}")

    def authenticate(self, config):
        """Security access layer."""
        os.system('clear')
        print(f"{Colors.BOLD}{Colors.CYAN}=== 🧠 NEURAL LINK LOCKED ==={Colors.RESET}")
        for attempt in range(3):
            entered = getpass.getpass(f"Passcode ({attempt+1}/3): ")
            if hashlib.sha256(entered.encode()).hexdigest() == config['hash']:
                self.google_key, self.groq_key = config['g_key'], config['q_key']
                self.pass_hash = config['hash']
                self.history = config.get("history", [])
                return
            print(f"{Colors.RED}Denied.{Colors.RESET}")
        sys.exit(1)

    def save_state(self):
        """Safely persists data without data loss."""
        data = {
            "hash": self.pass_hash,
            "g_key": self.google_key,
            "q_key": self.groq_key,
            "history": self.history
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)

    # ==============================================================================
    # 3. SELF-HEALING & STATUS (//mds)
    # ==============================================================================

    def check_model_status(self):
        """Feature: //mds - Real-time registry verification."""
        print(f"\n{Colors.YELLOW}--- 🛠️ MODEL AVAILABILITY STATUS ---{Colors.RESET}")
        try:
            g_models = [m['name'].split('/')[-1] for m in requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={self.google_key}", timeout=5).json().get('models', [])]
            q_models = [m['id'] for m in requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {self.groq_key}"}, timeout=5).json().get('data', [])]
        except: g_models, q_models = [], []

        for m in MODEL_POOL:
            available = (m['model'] in q_models if m['provider'] == 'groq' else m['model'] in g_models)
            status = f"{Colors.GREEN}Ready{Colors.RESET}" if available else f"{Colors.RED}Offline{Colors.RESET}"
            print(f"[{m['provider'].upper()}] {m['name']:<18} : {status}")

    def execute_request(self, prompt):
        """Execution with automatic session logging."""
        target = self.manual_model if not self.auto_mode else MODEL_POOL[0]
        # (API calling logic simplified for brevity - same as previous version)
        response = f"Simulated response from {target['name']}" # Replace with call_api logic
        
        self.history.append({"time": time.ctime(), "user": prompt, "ai": response, "model": target['name']})
        self.save_state()
        return target, response

    # ==============================================================================
    # 4. MODULAR MANAGEMENT (No restarts/New screens)
    # ==============================================================================

    def update_passcode(self):
        """Modular passcode change without data loss."""
        print(f"\n{Colors.CYAN}--- CHANGE PASSCODE ---{Colors.RESET}")
        p1 = getpass.getpass("New Passcode: ")
        p2 = getpass.getpass("Confirm New Passcode: ")
        if p1 == p2:
            self.pass_hash = hashlib.sha256(p1.encode()).hexdigest()
            self.save_state()
            print(f"{Colors.GREEN}Passcode updated.{Colors.RESET}")
        else:
            print(f"{Colors.RED}Mismatched. Aborted.{Colors.RESET}")

    def update_keys(self):
        """Modular key update (Invisible)."""
        print(f"\n[1] Google Key [2] Groq Key [0] Cancel")
        c = input("Select: ")
        if c == "1": self.google_key = getpass.getpass("New Google Key: ")
        elif c == "2": self.groq_key = getpass.getpass("New Groq Key: ")
        if c in ["1", "2"]:
            self.save_state()
            print(f"{Colors.GREEN}Key updated.{Colors.RESET}")

    def show_menu(self):
        """Central hub for all agent settings."""
        while True:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}--- MANAGEMENT CONSOLE ---{Colors.RESET}")
            print("[1] Switch Model [2] Auto-Mode [3] 📜 History [4] 🔑 Keys [5] 🔐 Passcode [0] Back")
            cmd = input("Select: ")
            if cmd == "1":
                for i, m in enumerate(MODEL_POOL): print(f"[{i}] {m['name']}")
                self.manual_model = MODEL_POOL[int(input("ID: "))]
                self.auto_mode = False
            elif cmd == "2": self.auto_mode = True
            elif cmd == "3":
                print(f"\nLast 5 records: {[h['user'] for h in self.history[-5:]]}")
            elif cmd == "4": self.update_keys()
            elif cmd == "5": self.update_passcode()
            elif cmd == "0": break

    def run(self):
        self.check_model_status()
        while True:
            try:
                print(f"\n{Colors.GRAY}" + "═" * 60 + f"{Colors.RESET}")
                mode = "AUTO" if self.auto_mode else f"MANUAL ({self.manual_model['name']})"
                print(f"{Colors.BOLD}SYSTEM: {mode} | [menu] [//mds] [exit]")
                
                user_in = input(f"{Colors.BOLD}{Colors.GREEN}You:{Colors.RESET} ").strip()
                if not user_in: continue
                if user_in.lower() == 'menu': self.show_menu()
                elif user_in.lower() == '//mds': self.check_model_status()
                elif user_in.lower() in ['exit', 'quit']: break
                else:
                    target, resp = self.execute_request(user_in)
                    print(f"\n{Colors.CYAN}AI Agent:{Colors.RESET}\n{resp}")
            except KeyboardInterrupt: break

if __name__ == "__main__":
    IntelligentAgent().run()
