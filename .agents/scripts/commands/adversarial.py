#!/usr/bin/env python
import sys
import os
import subprocess
import json
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
ORION_DIR = os.path.join(BASE_DIR, '.orion', 'working')
STATE_FILE = os.path.join(ORION_DIR, 'adversarial.json')

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_state(state):
    if not os.path.exists(ORION_DIR):
        os.makedirs(ORION_DIR)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def print_banner(msg, color=""):
    print(f"\n========================================")
    print(f" {msg}")
    print(f"========================================\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python orion.py adversarial <run|verify> <test_command...>")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    cmd = sys.argv[2:]
    
    if action not in ["run", "verify"]:
        print("Invalid action. Use 'run' or 'verify'.")
        sys.exit(1)
        
    print(f"[ADVERSARIAL] Executing: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd)
        exit_code = result.returncode
    except Exception as e:
        print(f"[ADVERSARIAL] Command failed to execute: {e}")
        exit_code = 1
        
    state = load_state()
    
    if action == "run":
        if exit_code == 0:
            print_banner("[!] ADVERSARIAL PROTOCOL VIOLATION [!]")
            print("ERROR: Test PASSED (Exit Code 0).")
            print("The Adversarial Twin Protocol requires you to write a FAILING test BEFORE implementation.")
            print("Either your test is flawed, or the feature is already implemented.")
            print("Status: AUTHORIZATION DENIED.")
            sys.exit(1)
        else:
            print_banner("[+] ADVERSARIAL SUCCESS [+]")
            print(f"Test FAILED as expected (Exit Code {exit_code}).")
            print("Status: AUTHORIZATION GRANTED to write implementation.")
            state["test_failed_at"] = time.time()
            state["command"] = " ".join(cmd)
            save_state(state)
            sys.exit(0)
            
    elif action == "verify":
        if "test_failed_at" not in state:
            print_banner("[!] ADVERSARIAL PROTOCOL VIOLATION [!]")
            print("ERROR: No failing test was recorded.")
            print("You must first run: `python .agents/scripts/orion.py adversarial run <test_cmd>` and prove it fails.")
            sys.exit(1)
            
        if exit_code > 0:
            print_banner("[-] ADVERSARIAL FAILURE [-]")
            print(f"ERROR: Test is still FAILING (Exit Code {exit_code}).")
            print("Your implementation did not fix the problem. Try again.")
            sys.exit(1)
        else:
            print_banner("[+] ADVERSARIAL VERIFIED [+]")
            print("Test PASSED (Exit Code 0). Implementation successful.")
            print("Status: TASK COMPLETE.")
            # Clear state after success
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)
            sys.exit(0)

if __name__ == "__main__":
    main()
