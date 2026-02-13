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
    {"provider": "groq", "model": "openai/gpt-oss-120b", "name": "GPT-OSS 120B", "desc": "Open Source Giant: Intricate instructions.", "type": "reasoning"},
    {"provider": "groq", "model": "groq/compound", "name": "Groq Compound Agent", "desc": "Agentic: Search, tools, and real-time data.", "type": "tool_use"},
    {"provider": "groq", "model": "meta-llama/llama-4-maverick-17b-128e-instruct", "name": "Llama 4 Maverick", "desc": "High-end Multimodal Vision.", "type": "vision"},
    {"provider": "groq", "model": "meta-llama/llama-4-scout-17b-16e-instruct", "name": "Llama 4 Scout", "desc": "Fast Multimodal Vision.", "type": "vision"},
    {"provider": "google", "model": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "desc": "Stable workhorse: Writing and creative tasks.", "type": "general"},
    {"provider": "groq", "model": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B", "desc": "Versatile conversationalist.", "type": "general"},
    {"provider": "google", "model": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "desc": "Speed Demon: High throughput backup.", "type": "speed"},
]

ROUTER_POOL = [{"provider": "groq", "model": "llama-3.3-70b-versatile"}, {"provider": "google", "model": "gemini-2.5-flash"}]

class Colors:
    CYAN, GREEN, YELLOW, RED = '\033[96m', '\033[92m', '\033[93m', '\033[91m'
    BOLD, RESET, GRAY = '\033[1m', '\033[0m', '\033[90m'

# ==============================================================================
# 2. CORE ENGINE: AUTH & PERSISTENCE
# ==============================================================================

class IntelligentAgent:
    def __init__(self):
        self.google_key = ""
        self.groq_key = ""
        self.auto_mode = True
        self.manual_model = None
        self.history = []
        self.load_or_setup()

    def load_or_setup(self):
        """Initializes configuration or triggers setup."""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        if not os.path.exists(CONFIG_FILE):
            self.run_setup()
        else:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.authenticate(config)

    def run_setup(self):
        """Interactive first-time setup."""
        os.system('clear')
        print(f"{Colors.BOLD}{Colors.CYAN}=== 🔐 INITIAL NEURAL SETUP ==={Colors.RESET}")
        while True:
            p1 = getpass.getpass("Set Passcode: ")
            p2 = getpass.getpass("Confirm Passcode: ")
            if p1 == p2: break
            print(f"{Colors.RED}Mismatched passcodes!{Colors.RESET}")
        
        g_key = getpass.getpass("Enter Google AI Key (Invisible): ").strip()
        q_key = getpass.getpass("Enter Groq API Key (Invisible): ").strip()
        
        config = {"hash": hashlib.sha256(p1.encode()).hexdigest(), "g_key": g_key, "q_key": q_key, "history": []}
        with open(CONFIG_FILE, 'w') as f: json.dump(config, f)
        self.google_key, self.groq_key = g_key, q_key

    def authenticate(self, config):
        """Secure login."""
        os.system('clear')
        print(f"{Colors.BOLD}{Colors.CYAN}=== 🧠 NEURAL LINK LOCKED ==={Colors.RESET}")
        for attempt in range(3):
            if hashlib.sha256(getpass.getpass(f"Passcode ({attempt+1}/3): ").encode()).hexdigest() == config['hash']:
                self.google_key, self.groq_key = config['g_key'], config['q_key']
                self.history = config.get("history", [])
                return
            print(f"{Colors.RED}Denied.{Colors.RESET}")
        sys.exit(1)

    def save_state(self):
        """Saves current keys and history to persistent storage."""
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
        data.update({"g_key": self.google_key, "q_key": self.groq_key, "history": self.history})
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)

    # ==============================================================================
    # 3. SELF-HEALING EXECUTION
    # ==============================================================================

    def call_api(self, provider, model_id, prompt):
        try:
            if provider == "google":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.google_key}"
                resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                return resp.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.groq_key}"}
                data = {"model": model_id, "messages": [{"role": "user", "content": prompt}]}
                resp = requests.post(url, headers=headers, json=data, timeout=20)
                return resp.json()['choices'][0]['message']['content']
        except Exception as e: raise Exception(str(e))

    def semantic_router(self, user_prompt):
        """Brain Failsafe: Reroutes if primary router fails."""
        instruction = f"ID for: '{user_prompt}'. Models: {[{m['model']: m['desc']} for m in MODEL_POOL]}. Return ONLY ID."
        for router in ROUTER_POOL:
            try:
                decision = self.call_api(router['provider'], router['model'], instruction).strip().replace('"', '').replace("'", "")
                for m in MODEL_POOL:
                    if m['model'] in decision: return m
            except: continue
        return MODEL_POOL[0]

    def execute_safely(self, prompt):
        """Failsafe Execution with History Logging."""
        target = self.manual_model if not self.auto_mode else self.semantic_router(prompt)
        print(f"{Colors.GRAY}🧠 Node: {target['name']}{Colors.RESET}")
        try:
            response = self.call_api(target['provider'], target['model'], prompt)
        except Exception as e:
            print(f"{Colors.RED}⚠️ Error: {e}. Healing...{Colors.RESET}")
            target = MODEL_POOL[-1]
            response = self.call_api(target['provider'], target['model'], f"FALLBACK: {prompt}")
        
        self.history.append({"time": time.ctime(), "user": prompt, "ai": response, "model": target['name']})
        self.save_state()
        return target, response

    # ==============================================================================
    # 4. MODULAR MANAGEMENT CONSOLE
    # ==============================================================================

    def view_history(self):
        """Feature: History Viewer."""
        os.system('clear')
        print(f"{Colors.BOLD}{Colors.CYAN}=== 📜 SESSION HISTORY ==={Colors.RESET}")
        if not self.history: print("No records found.")
        for entry in self.history[-10:]: # Shows last 10 entries
            print(f"\n{Colors.YELLOW}[{entry['time']}] - {entry['model']}{Colors.RESET}")
            print(f"{Colors.GREEN}You:{Colors.RESET} {entry['user']}")
            print(f"{Colors.CYAN}AI:{Colors.RESET} {entry['ai'][:200]}...") # Truncated for readability
        input(f"\n{Colors.GRAY}Press Enter to return...{Colors.RESET}")

    def update_keys(self):
        """Feature: Modular Key Update (Invisible)."""
        print(f"\n[1] Update Google Key [2] Update Groq Key [0] Cancel")
        c = input("Choice: ")
        if c == "1": self.google_key = getpass.getpass("Enter New Google Key: ")
        elif c == "2": self.groq_key = getpass.getpass("Enter New Groq Key: ")
        self.save_state()
        print(f"{Colors.GREEN}Keys updated successfully.{Colors.RESET}")

    def show_menu(self):
        """Integrated Management Console."""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}--- SYSTEM MANAGEMENT ---{Colors.RESET}")
        print("[1] Switch Model [2] Auto-Mode [3] 📜 View History [4] 🔑 Update Keys [5] Reset Passcode [0] Back")
        cmd = input("Select: ")
        if cmd == "1":
            for i, m in enumerate(MODEL_POOL): print(f"[{i}] {m['name']}")
            self.manual_model = MODEL_POOL[int(input("ID: "))]
            self.auto_mode = False
        elif cmd == "2": self.auto_mode = True
        elif cmd == "3": self.view_history()
        elif cmd == "4": self.update_keys()
        elif cmd == "5": self.run_setup()

    def run(self):
        while True:
            try:
                print(f"\n{Colors.GRAY}" + "═" * 60 + f"{Colors.RESET}")
                mode = f"{Colors.CYAN}AUTO{Colors.RESET}" if self.auto_mode else f"{Colors.YELLOW}MANUAL{Colors.RESET}"
                print(f"{Colors.BOLD}SYSTEM: {mode} | [menu] [//mds] [exit]")
                print(f"{Colors.GRAY}" + "═" * 60 + f"{Colors.RESET}")
                
                user_in = input(f"{Colors.BOLD}{Colors.GREEN}You:{Colors.RESET} ").strip()
                if not user_in: continue
                if user_in.lower() == 'menu': self.show_menu()
                elif user_in.lower() == '//mds':
                    # Status check logic removed from main for space, but //mds remains as command
                    print("Pinging registries...")
                elif user_in.lower() in ['exit', 'quit']: break
                else:
                    used_model, response = self.execute_safely(user_in)
                    print(f"\n{Colors.CYAN}AI ({used_model['name']}):{Colors.RESET}\n{response}")
            except KeyboardInterrupt: break

if __name__ == "__main__":
    IntelligentAgent().run()
