import os
import subprocess
import sys

def check_and_sync(base_agents_dir, base_dir):
    manifest_path = os.path.join(base_dir, '.orion', '_manifest.json')
    needs_sync = False
    try:
        rules_dir = os.path.join(base_agents_dir, 'rules')
        if os.path.exists(rules_dir) and os.path.exists(manifest_path):
            manifest_mtime = os.path.getmtime(manifest_path)
            latest_rule_mtime = 0
            for root, _, files in os.walk(rules_dir):
                for f in files:
                    if f.endswith('.md'):
                        f_mtime = os.path.getmtime(os.path.join(root, f))
                        if f_mtime > latest_rule_mtime:
                            latest_rule_mtime = f_mtime
            
            if latest_rule_mtime > manifest_mtime:
                needs_sync = True
        elif not os.path.exists(manifest_path) and os.path.exists(rules_dir):
            needs_sync = True
            
        if needs_sync:
            print("[AUTO-SYNC] Ecosystem drift detected. Triggering background graph sync...")
            orion_script = os.path.join(base_agents_dir, 'scripts', 'orion.py')
            print("[AUTO-SYNC] Running synchronous ingest to prevent race conditions...")
            ingest_paths = [
                os.path.join(base_agents_dir, 'rules'),
                os.path.join(base_agents_dir, 'skills'),
                os.path.join(base_agents_dir, 'canons'),
                os.path.join(base_agents_dir, 'workflows'),
            ]
            existing_paths = [p for p in ingest_paths if os.path.isdir(p)]
            result = subprocess.run(
                [sys.executable, orion_script, 'orion_ops', 'ingest'] + existing_paths, 
                stdout=sys.stdout, stderr=sys.stderr,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode != 0:
                print(f"[AUTO-SYNC] WARNING: Ingest exited with code {result.returncode}. Graph may be stale.")
    except Exception as e:
        print(f"[AUTO-SYNC] Failed to run sync: {e}")
