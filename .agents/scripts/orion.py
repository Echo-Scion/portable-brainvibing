#!/usr/bin/env python
import sys
import os
import subprocess

# Force utf-8 encoding for standard output to avoid UnicodeEncodeError on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip()

load_env()

def print_help():
    print("========================================")
    print(" 🌌 ORION: The Unified Brain Engine CLI")
    print("========================================\n")
    print("Usage: python .agents/scripts/orion.py <command> [args...]\n")
    print("Available Commands:")
    print("  brain         - Neuro-Link Brain Engine (sync, page)")
    print("  viz           - Generate HTML visualization of Orion Graph")
    print("  verify        - Verify workspace integrity & AST drift")
    print("  orion_ops     - Orion Graph Operations (init, ingest)")
    print("  deploy        - Deploy Foundation to a target project")
    print("  scan          - Ghost Token Auditor & Code Mapper")
    print("  compress      - Compress episodic memory to Caveman")
    print("  nano          - Nano LLM local compressor")
    print("  swarm         - Micro-Fix Swarm Delegation")
    print("  amnesia       - Rule Eviction & Token Bloat Control")
    print("  scaffold      - SaaS Scaffolder")
    print("  preflight     - Self-Healing Routing Diagnostic")
    print("  budget        - Track budget and tier telemetry")
    print("  compile       - Compile rules into static output")
    print("  context-lint  - Validate context/ naming conventions")
    print("  linkify       - Auto-inject Wiki-links into Markdown")
    print("  adversarial   - Enforce Adversarial Twin Protocol (TDD wrapper)")
    print("  consolidate   - Temporal Pulse: session/milestone/epoch knowledge synthesis")
    print("  contradict    - Contradiction Resolution Engine")
    print("  fsm           - Formal State Machine Engine\n")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print_help()
        sys.exit(0 if len(sys.argv) >= 2 else 1)

    cmd_map = {
        "brain": ["commands", "brain.py"],
        "verify": ["commands", "verify_agents.py"],
        "verify_agents": ["commands", "verify_agents.py"],
        "orion_ops": ["commands", "orion_ops.py"],
        "orion": ["commands", "orion_ops.py"],
        "evolve": ["commands", "evolve.py"],
        "deploy": ["commands", "foundation.py"],
        "push-upstream": ["commands", "foundation.py"],
        "foundation": ["commands", "foundation.py"],
        "scan": ["core", "scanner.py"],
        "scanner": ["core", "scanner.py"],
        "compress": ["commands", "compress_memory.py"],
        "compress_memory": ["commands", "compress_memory.py"],
        "nano": ["commands", "nano_compressor.py"],
        "nano_compressor": ["commands", "nano_compressor.py"],
        "swarm": ["commands", "auto_delegate.py"],
        "auto_delegate": ["commands", "auto_delegate.py"],
        "amnesia": ["commands", "rule_eviction.py"],
        "rule_eviction": ["commands", "rule_eviction.py"],
        "preflight": ["commands", "preflight_check.py"],
        "preflight_check": ["commands", "preflight_check.py"],
        "scaffold": ["commands", "scaffold_saas.py"],
        "scaffold_saas": ["commands", "scaffold_saas.py"],
        "budget": ["commands", "track_budget.py"],
        "track_budget": ["commands", "track_budget.py"],
        "compile": ["commands", "compile_rules.py"],
        "compile_rules": ["commands", "compile_rules.py"],
        "context-lint": ["commands", "context_naming_lint.py"],
        "context_naming_lint": ["commands", "context_naming_lint.py"],
        "linkify": ["commands", "linkify.py"],
        "matrix": ["commands", "matrix_query.py"],
        "rtk": ["core", "rtk_proxy.py"],
        "rtk_proxy": ["core", "rtk_proxy.py"],
        "adversarial": ["commands", "adversarial.py"],
        "viz": ["commands", "viz.py"],
        "raw_ingest": ["commands", "raw_ingest.py"],
        "consolidate": ["commands", "consolidate.py"],
        "contradict": ["commands", "contradict.py"],
        "fsm": ["commands", "state_machine.py"]
    }

    cmd = sys.argv[1]

    if cmd in cmd_map:
        rel_path = cmd_map[cmd]
        target_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), *rel_path)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    # For 'deploy' and 'push-upstream', pass them explicitly since foundation.py expects them as sys.argv[1]
    if cmd == "deploy" or cmd == "push-upstream":
        args = [cmd] + sys.argv[2:]
    else:
        args = sys.argv[2:]
        
    python_exec = sys.executable or "python"
    
    try:
        max_retries = 3
        import time
        for attempt in range(max_retries):
            result = subprocess.run([python_exec, target_script] + args)
            
            # If success, or if it's an interactive/expected failure command, exit immediately
            if result.returncode == 0 or cmd in ["rtk", "rtk_proxy", "preflight", "budget", "verify"]:
                sys.exit(result.returncode)
                
            print(f"[ORION AUTO-RETRY] Command failed with exit code {result.returncode}. Attempt {attempt+1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(1)
        
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)

if __name__ == "__main__":
    main()
