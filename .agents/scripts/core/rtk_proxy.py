import sys
import subprocess
import os
import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: python rtk_proxy.py <command>")
        sys.exit(1)
        
    cmd = sys.argv[1:]
    agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    learnings_path = os.path.join(agents_dir, "LEARNINGS.md")
    
    print(f" [RTK PROXY] Executing: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            print(f"\n[DARWINIAN HOOK] Command failed with exit code {result.returncode}. Intercepting stderr...")
            
            error_log = f"\n## [Darwinian Hook] Auto-intercepted Failure at {datetime.datetime.now().isoformat()}\n"
            error_log += f"**Command**: `{' '.join(cmd)}`\n"
            error_log += f"**Exit Code**: {result.returncode}\n"
            error_log += f"**Stderr**:\n```\n{result.stderr.strip()[:1000]}\n```\n"
            
            with open(learnings_path, "a", encoding="utf-8") as f:
                f.write(error_log)
                
            print(f"[DARWINIAN HOOK] Failure appended to {os.path.relpath(learnings_path, os.getcwd())}.")
            print(f"[SYSTEM DIRECTIVE] Agent must trigger `.agents/workflows/self-evolve.md` to patch this failure mode.")
            sys.exit(result.returncode)
            
    except Exception as e:
        print(f"[RTK PROXY ERROR] Failed to execute wrapper: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
