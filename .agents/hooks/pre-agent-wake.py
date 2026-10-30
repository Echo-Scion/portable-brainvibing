#!/usr/bin/env python
"""
pre-agent-wake.py
-----------------
Omni-Buffer Hook. This script is called synchronously by the IDE extension (PreInvocation hook)
before the AI agent starts processing. It drops the current state into a standardized
JSON file (context.json) so the agent has a single source of truth for context.
Self-contained single-file hook (no external modules/ dependency).
"""

import os
import json
import time
import argparse
import sys
import threading
import queue
import uuid
import re
from typing import List, Optional, Tuple

try:
    from core.db import atomic_write_text as _atomic_write_text, log_telemetry as _log_telemetry
except ImportError:
    _scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    from core.db import atomic_write_text as _atomic_write_text, log_telemetry as _log_telemetry

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception as _e:
        _log_telemetry(_e, "stdout_reconfigure")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
CONTEXT_DIR = os.path.join(BASE_DIR, '.orion', 'working')
CONTEXT_FILE = os.path.join(CONTEXT_DIR, 'context.json')
WORKSPACE_DIR = BASE_DIR

def _read_stdin_nonblocking(timeout: float = 0.15) -> dict:
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    if os.name == 'nt':
        try:
            import msvcrt
            import ctypes
            from ctypes import wintypes
            handle = msvcrt.get_osfhandle(sys.stdin.fileno())
            avail = wintypes.DWORD()
            deadline = time.time() + timeout
            accumulated = []
            while time.time() < deadline:
                success = ctypes.windll.kernel32.PeekNamedPipe(handle, None, 0, None, ctypes.byref(avail), None)
                if success and avail.value > 0:
                    chunk = os.read(sys.stdin.fileno(), avail.value)
                    accumulated.append(chunk)
                    # Check if accumulated text forms valid JSON (stripping UTF-8 BOM if emitted by PowerShell)
                    raw_try = b"".join(accumulated).decode('utf-8-sig', errors='replace').strip()
                    if raw_try.startswith(("{", "[")) and raw_try.endswith(("}", "]")):
                        try:
                            return json.loads(raw_try)
                        except Exception:
                            pass
                time.sleep(0.01)

            if accumulated:
                raw_str = b"".join(accumulated).decode('utf-8-sig', errors='replace').strip()
                return json.loads(raw_str) if raw_str else {}
            return {}
        except Exception as _pe:
            _log_telemetry(_pe, "stdin_peek_named_pipe")

    q = queue.Queue()
    def _worker():
        try:
            raw = sys.stdin.read().strip()
            if raw:
                q.put(raw)
        except Exception as _err:
            _log_telemetry(_err, "stdin_worker_read")
    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout)
    if not q.empty():
        raw_str = q.get_nowait()
        if raw_str:
            try:
                return json.loads(raw_str)
            except Exception as _err:
                _log_telemetry(_err, "stdin_json_loads")
    return {}

def _extract_top_lessons(learnings_content: str) -> list:
    lessons = []
    for line in learnings_content.split('\n'):
        line_s = line.strip()
        if (line_s.startswith('- ') or line_s.startswith('* ')) and len(line_s) > 10:
            lessons.append(line_s[2:].strip())
        elif line_s.startswith('**Self-Evolve Rule**:') and len(line_s) > 22:
            lessons.append(line_s.replace('**Self-Evolve Rule**:', '').strip())
        elif line_s.startswith('## 20') and ('—' in line_s or '-' in line_s):
            lessons.append(line_s.lstrip('#').strip())
    return lessons[:5]

def _check_passive_orion_gc(base_dir: str) -> None:
    """
    Passively checks if .orion garbage collection is overdue (>7 days).
    Spawns background GC detached process without blocking agent wakeup.
    """
    last_gc_file = os.path.join(base_dir, ".orion", "working", ".last_gc")
    now = time.time()
    needs_gc = False

    if not os.path.exists(last_gc_file):
        try:
            os.makedirs(os.path.dirname(last_gc_file), exist_ok=True)
            _atomic_write_text(last_gc_file, str(now))
        except Exception as _ce:
            _log_telemetry(_ce, "pre-agent-wake:init_last_gc")
        return

    try:
        with open(last_gc_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                last_time = float(content)
                if now - last_time > 7 * 86400:
                    needs_gc = True
    except Exception as _re:
        _log_telemetry(_re, "pre-agent-wake:read_last_gc")
        needs_gc = True

    if needs_gc:
        try:
            _atomic_write_text(last_gc_file, str(now))
        except Exception as _we:
            _log_telemetry(_we, "pre-agent-wake:write_last_gc")

        orion_script = os.path.join(base_dir, ".agents", "scripts", "orion.py")
        if os.path.exists(orion_script):
            try:
                import subprocess
                flags = 0
                if os.name == 'nt':
                    flags = getattr(subprocess, 'DETACHED_PROCESS', 0x00000008) | getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
                subprocess.Popen(
                    [sys.executable, orion_script, "gc"],
                    cwd=base_dir,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=flags
                )
            except Exception as e:
                _log_telemetry(e, "pre-agent-wake:passive_gc")

def _bootstrap_identity(identity_path: str, base_agents_dir: str, learnings_path: str, workspace_dir: str):
    identity_exists = os.path.exists(identity_path)
    top_lessons = []
    
    if not identity_exists:
        template_path = os.path.join(base_agents_dir, 'templates', 'agent-identity-template.md')
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                
                if os.path.exists(learnings_path):
                    with open(learnings_path, 'r', encoding='utf-8') as f:
                        learnings_content = f.read()
                    top_lessons = _extract_top_lessons(learnings_content)
                
                lessons_str = '\n'.join(f"{i+1}. {l}" for i, l in enumerate(top_lessons)) if top_lessons else "_(no lessons recorded yet)_"
                
                identity_content = template.replace('{{project_name}}', os.path.basename(workspace_dir))
                identity_content = identity_content.replace('{{framework}}', 'detected at runtime')
                identity_content = identity_content.replace('{{user_name}}', '_(set during onboarding)_')
                identity_content = identity_content.replace('{{user_role}}', '_(set during onboarding)_')
                identity_content = identity_content.replace('{{timezone}}', time.strftime('%Z'))
                identity_content = identity_content.replace('{{primary_stack}}', '_(extracted from BLUEPRINT.md)_')
                identity_content = identity_content.replace('{{top_lessons}}', lessons_str)
                identity_content = identity_content.replace('{{anti_goals}}', '- Do NOT re-initialize .orion.db repeatedly\n- Do NOT destroy handoff.md during brain sync\n- Do NOT use sed/awk for file modifications')
                identity_content = identity_content.replace('{{timestamp}}', time.strftime('%Y-%m-%d'))
                
                context_dir_path = os.path.dirname(identity_path)
                os.makedirs(context_dir_path, exist_ok=True)
                _atomic_write_text(identity_path, identity_content)
                identity_exists = True
            except Exception as e:
                _log_telemetry(e, "identity_bootstrap_generate")
    else:
        if os.path.exists(learnings_path):
            try:
                with open(learnings_path, 'r', encoding='utf-8') as f:
                    learnings_content = f.read()
                top_lessons = _extract_top_lessons(learnings_content)
                
                with open(identity_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
                identity_content = old_content
                    
                if top_lessons:
                    import re
                    lessons_str = '\n'.join(f"{i+1}. {l}" for i, l in enumerate(top_lessons))
                    identity_content = re.sub(
                        r'(## Active Lessons \(Top 5\)).*?(?=## |$)', 
                        lambda m: f"{m.group(1)}\n\n{lessons_str}\n\n", 
                        identity_content, flags=re.DOTALL)
                
                genome_path = os.path.join(base_agents_dir, ".genome.json")
                if os.path.exists(genome_path):
                    with open(genome_path, 'r', encoding='utf-8') as gf:
                        genome = json.load(gf)
                    
                    traits = []
                    if genome.get("evolved_skills"):
                        traits.append("- **Evolved Skills**: " + ", ".join(genome["evolved_skills"]))
                    if genome.get("evolved_rules"):
                        traits.append("- **Evolved Rules**: " + ", ".join(genome["evolved_rules"]))
                    if genome.get("pruned_assets"):
                        traits.append("- **Pruned Assets**: " + ", ".join(genome["pruned_assets"]))
                    
                    traits_str = '\n'.join(traits) if traits else "_(no mutations yet)_"
                    if "## Evolutionary Traits" not in identity_content:
                        identity_content = identity_content.replace(
                            "## Anti-Goals", 
                            f"## Evolutionary Traits\n\n{traits_str}\n\n## Anti-Goals"
                        )
                    else:
                        identity_content = re.sub(
                            r'(## Evolutionary Traits).*?(?=## |$)', 
                            lambda m: f"{m.group(1)}\n\n{traits_str}\n\n", 
                            identity_content, flags=re.DOTALL)
                
                if identity_content != old_content:
                    _atomic_write_text(identity_path, identity_content)
            except Exception as e:
                _log_telemetry(e, "identity_bootstrap_sync")
                    
    return identity_exists, top_lessons

def _check_heartbeat(learnings_path: str, base_agents_dir: str) -> Tuple[bool, int]:
    evolution_overdue = False
    unprocessed_learnings = 0
    import re
    if os.path.exists(learnings_path):
        try:
            with open(learnings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            non_template_lines = [
                l for l in content.splitlines() 
                if not l.strip().startswith('#') and 'template' not in l.lower()
            ]
            hook_count = sum(1 for l in non_template_lines if "[Darwinian Hook]" in l and "[Processed]" not in l)
            entries = re.findall(r'^##\s+(?:20\d\d-\d\d-\d\d|\d+\.)\s*.*?(?=^##|\Z)', content, re.MULTILINE | re.DOTALL)
            real_entries = [
                e for e in entries 
                if not re.search(r'template|example|format|log template|block 0', e, re.IGNORECASE)
                and '[Processed]' not in e
                and len(e.strip()) > 50
            ]
            unprocessed_learnings = max(hook_count, len(real_entries))
        except Exception as _e:
            _log_telemetry(_e, "heartbeat_learnings")

    workspace_dir = os.path.dirname(base_agents_dir)
    failures_log = os.path.normpath(os.path.join(workspace_dir, ".orion", "working", "failures.log"))
    if os.path.exists(failures_log):
        try:
            with open(failures_log, 'r', encoding='utf-8') as f:
                f_content = f.read()
            fail_entries = re.findall(r'## \[Darwinian Hook\] Auto-intercepted Failure', f_content)
            succ_entries = re.findall(r'## \[Darwinian Hook\] (?:Command Succeeded|Reflexion)', f_content)
            unprocessed_failures = max(0, len(fail_entries) - len(succ_entries))
            unprocessed_learnings += unprocessed_failures
        except OSError:
            pass
    
    if unprocessed_learnings >= 3:
        evolution_overdue = True

    return evolution_overdue, unprocessed_learnings

def _check_fsm(fsm_state_path: str) -> str:
    recovery_instruction = ""
    working_dir = os.path.dirname(fsm_state_path)

    if os.path.exists(fsm_state_path):
        try:
            with open(fsm_state_path, 'r', encoding='utf-8') as f:
                fsm_state = json.load(f)

            phase = fsm_state.get("phase", "IDLE")
            git_sha = fsm_state.get("_git_tree_sha")
            if phase not in ("IDLE", "DONE"):
                active_tasks = fsm_state.get("active_tasks", {})
                tasks_info = ", ".join([f"{k} ({v.get('status')})" for k, v in active_tasks.items()])
                sha_info = f" [Snapshot: {git_sha[:8]}]" if git_sha else ""
                recovery_instruction = (
                    f"CRITICAL RECOVERY STATE: You were interrupted during phase '{phase}'{sha_info}. "
                    f"Active tasks pending: {tasks_info if tasks_info else 'None'}. "
                    "Resume your exact task immediately and do NOT restart from scratch."
                )
        except Exception as e:
            _log_telemetry(e, "fsm_recovery_parse")

    trajectory_path = os.path.join(working_dir, "trajectory.jsonl")
    if os.path.exists(trajectory_path):
        try:
            scripts_dir = os.path.abspath(os.path.join(working_dir, "..", "..", ".agents", "scripts"))
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            from core.db import ActionObservationStream

            stream = ActionObservationStream(trajectory_path)
            if stream.detect_stuck_loop(window_size=3):
                last_act = stream.get_last_action()
                act_info = f"'{last_act.action_type}'" if last_act else "repeated commands"
                recovery_instruction += (
                    f"\n[CIRCUIT BREAKER DETECTED]: 3 cyclical or identical actions occurred on {act_info}. "
                    "Root-cause: Repetitive execution cycle. Do not repeat the same action; use alternative approach."
                )
            paging_file = stream.detect_sequential_paging(consecutive_threshold=2)
            if paging_file:
                recovery_instruction += (
                    f"\n[SEQUENTIAL PAGING DETECTED]: Consecutive file chunk reads detected on '{os.path.basename(paging_file)}'. "
                    "Root-cause: Paging violation. Run 'python .agents/scripts/orion.py scan map <file>' and read target span in single turn."
                )
        except Exception as e:
            _log_telemetry(e, "trajectory_inspection")

    failures_log = os.path.join(working_dir, "failures.log")
    if os.path.exists(failures_log):
        try:
            with open(failures_log, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            import re
            entries = re.findall(r'## \[Darwinian Hook\] (Auto-intercepted Failure|Command Succeeded|Reflexion)', content)
            fail_streak = 0
            for entry in reversed(entries):
                if entry == "Auto-intercepted Failure":
                    fail_streak += 1
                else:
                    break
            if fail_streak >= 3:
                recovery_instruction += (
                    f"\n[CLI CIRCUIT BREAKER]: {fail_streak} consecutive command failures detected in failures.log. "
                    "Review error diagnostics and execute reflexion before retrying terminal commands."
                )
        except Exception as e:
            _log_telemetry(e, "failures_log_inspection")

    return recovery_instruction

def _is_pid_alive(pid: Optional[int]) -> bool:
    if not pid or pid <= 0:
        return False
    if os.name == 'nt':
        try:
            import ctypes
            SYNCHRONIZE = 0x00100000
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                return False
            STILL_ACTIVE = 259
            exit_code = ctypes.c_ulong()
            success = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
            ctypes.windll.kernel32.CloseHandle(handle)
            if not success:
                return False
            return exit_code.value == STILL_ACTIVE
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False


def _check_and_sync(base_agents_dir: str, base_dir: str) -> None:
    import subprocess
    manifest_path = os.path.join(base_dir, '.orion', '_manifest.json')
    now = time.time()
    
    # Throttle directory walk: skip if checked within last 30 seconds
    last_walk_file = os.path.join(base_dir, '.orion', 'working', '.last_sync_walk')
    if os.path.exists(last_walk_file):
        try:
            with open(last_walk_file, 'r', encoding='utf-8') as wf:
                last_walk = float(wf.read().strip())
            if now - last_walk < 30.0:
                return
        except Exception:
            pass
    try:
        os.makedirs(os.path.dirname(last_walk_file), exist_ok=True)
        _atomic_write_text(last_walk_file, str(now))
    except Exception:
        pass

    needs_sync = False
    try:
        watch_dirs = [
            os.path.join(base_agents_dir, 'rules'),
            os.path.join(base_agents_dir, 'skills'),
            os.path.join(base_agents_dir, 'canons'),
            os.path.join(base_dir, 'context'),
        ]
        existing_watch = [d for d in watch_dirs if os.path.isdir(d)]
        if existing_watch and os.path.exists(manifest_path):
            manifest_mtime = os.path.getmtime(manifest_path)
            latest_mtime = 0
            for wdir in existing_watch:
                for root, _, files in os.walk(wdir):
                    for f in files:
                        if f.endswith('.md'):
                            f_mtime = os.path.getmtime(os.path.join(root, f))
                            if f_mtime > latest_mtime:
                                latest_mtime = f_mtime
            if latest_mtime > manifest_mtime:
                needs_sync = True
        elif not os.path.exists(manifest_path) and existing_watch:
            needs_sync = True
            
        if needs_sync:
            lock_file = os.path.join(base_dir, '.orion', 'working', '.auto_sync_lock')
            now = time.time()
            if os.path.exists(lock_file):
                try:
                    with open(lock_file, 'r', encoding='utf-8') as lf:
                        content = lf.read().strip()
                    parts = content.split(':')
                    last_ts = float(parts[0])
                    pid = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
                    if pid == 0 and (now - last_ts < 300):
                        needs_sync = False
                    elif pid and _is_pid_alive(pid) and (now - last_ts < 300):
                        needs_sync = False
                    else:
                        try:
                            os.remove(lock_file)
                        except OSError as _e:
                            _log_telemetry(_e, "auto_sync_stale_lock_remove")
                except Exception as _e:
                    _log_telemetry(_e, "auto_sync_lock")

        if needs_sync:
            # Claim lock immediately with current pid to close TOCTOU window
            try:
                _atomic_write_text(lock_file, f"{now}:{os.getpid()}")
            except Exception as _e:
                _log_telemetry(_e, "auto_sync_lock_claim")

            orion_script = os.path.join(base_agents_dir, 'scripts', 'orion.py')
            try:
                subprocess.run(
                    [sys.executable, orion_script, 'compile'],
                    cwd=base_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
            except Exception as _e:
                _log_telemetry(_e, "auto_sync_compile")

            ingest_paths = [
                os.path.join(base_agents_dir, 'rules'),
                os.path.join(base_agents_dir, 'skills'),
                os.path.join(base_agents_dir, 'canons'),
                os.path.join(base_dir, 'context'),
            ]
            existing_paths = [p for p in ingest_paths if os.path.isdir(p)]
            log_dir = os.path.join(base_dir, '.orion', 'working')
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, 'auto_sync_ingest.log')
            with open(log_path, 'a', encoding='utf-8') as log_file:
                proc = subprocess.Popen(
                    [sys.executable, orion_script, 'orion_ops', 'ingest'] + existing_paths, 
                    stdin=subprocess.DEVNULL,
                    stdout=log_file,
                    stderr=log_file,
                    cwd=base_dir,
                    close_fds=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                try:
                    _atomic_write_text(lock_file, f"{now}:{proc.pid}")
                except Exception as _e:
                    _log_telemetry(_e, "auto_sync_lock_write")
    except Exception as e:
        _log_telemetry(e, "auto_sync_run")

def _check_drift(active_file: str, base_dir: str) -> list:
    drift_warnings = []
    if active_file:
        active_base = os.path.basename(active_file)
        active_stem = os.path.splitext(active_base)[0]
        if active_base and active_base != "unknown":
            try:
                db_path = os.path.join(base_dir, '.orion', 'orion.db')
                if os.path.exists(db_path):
                    import sqlite3
                    with sqlite3.connect(db_path, timeout=5.0) as conn:
                        conn.execute("PRAGMA busy_timeout=5000;")
                        c = conn.cursor()
                        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relations'")
                        if c.fetchone():
                            c.execute(
                                "SELECT subject_id, predicate FROM relations WHERE object_id LIKE ? OR object_id = ? OR object_id LIKE ? LIMIT 5",
                                (f"%{active_base}%", active_stem, f"%.{active_stem}"),
                            )
                            rows = c.fetchall()
                        else:
                            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='edges'")
                            if c.fetchone():
                                c.execute(
                                    "SELECT source_id, relation FROM edges WHERE target_id LIKE ? OR target_id = ? OR target_id LIKE ? LIMIT 5",
                                    (f"%{active_base}%", active_stem, f"%.{active_stem}"),
                                )
                                rows = c.fetchall()
                            else:
                                rows = []
                        for source_id, relation in rows:
                            source_base = os.path.basename(source_id)
                            if source_base != active_base:
                                safe_rel = re.sub(r'[^A-Za-z0-9_\-\s]', '', str(relation))[:32].strip() or "relates to"
                                safe_src = re.sub(r'[^A-Za-z0-9_.\-]', '', str(source_base))[:64]
                                drift_warnings.append(f"CRITICAL DRIFT RISK: `{safe_src}` {safe_rel} this active file. If you modify `{active_base}`, you MUST verify if `{safe_src}` needs updating!")
            except Exception as e:
                _log_telemetry(e, "drift_detector_query")
    return drift_warnings

def enforce_bento_and_tdd_gates(workspace_dir: str, model_name: str, context_dir: str) -> List[str]:
    import subprocess
    warnings = []
    try:
        # Cache check: if git index mtime unchanged and checked within 10s, reuse cached status
        git_index = os.path.join(workspace_dir, ".git", "index")
        cache_file = os.path.join(context_dir, ".git_status_cache.json")
        now = time.time()
        cached_lines = None
        index_mtime = os.path.getmtime(git_index) if os.path.exists(git_index) else 0

        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as cf:
                    cdata = json.load(cf)
                if cdata.get("index_mtime") == index_mtime and (now - float(cdata.get("ts", 0))) < 10.0:
                    cached_lines = cdata.get("lines", [])
            except Exception:
                pass

        if cached_lines is None:
            res = subprocess.run(["git", "status", "--porcelain"], cwd=workspace_dir, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3)
            if res.returncode == 0:
                cached_lines = res.stdout.splitlines()
                try:
                    with open(cache_file, "w", encoding="utf-8") as cf:
                        json.dump({"index_mtime": index_mtime, "ts": now, "lines": cached_lines}, cf)
                except Exception:
                    pass
            else:
                cached_lines = []

        modified_files = []
        for line in cached_lines:
            if not line.strip() or len(line) < 4:
                continue
            status = line[:2]
            path_part = line[3:].strip()
            # Skip deleted files from active code modification counting
            if "D" in status:
                continue
            # For renamed files (R  old -> new), inspect the destination path
            if "->" in path_part:
                path_part = path_part.split("->")[-1].strip()
            modified_files.append(path_part)
            code_files = [f for f in modified_files if f.endswith((".py", ".dart", ".ts", ".tsx", ".js", ".rs", ".go", ".kt"))]
            test_files = [f for f in code_files if "test" in f.lower() or "spec" in f.lower()]
            prod_files = [f for f in code_files if f not in test_files and not f.startswith(".agents")]

            if model_name and any(m in model_name.lower() for m in ("flash", "haiku", "mini", "nano")):
                if len(prod_files) > 3:
                    warnings.append(
                        f"BENTO-BOX HARD GATE VIOLATION: Active model '{model_name}' is BUDGET tier "
                        f"but {len(prod_files)} production files are modified simultaneously ({', '.join(prod_files[:4])}). "
                        "Commit or revert excess files before editing further."
                    )

            fsm_file = os.path.join(context_dir, "execution_state.json")
            adv_file = os.path.join(context_dir, "adversarial.json")
            adv_active = False
            if os.path.exists(adv_file):
                try:
                    with open(adv_file, "r", encoding="utf-8") as _af:
                        adv_data = json.load(_af)
                    ts = float(adv_data.get("timestamp", 0)) or os.path.getmtime(adv_file)
                    if time.time() - ts <= 600:
                        adv_active = True
                except Exception:
                    pass

            if os.path.exists(fsm_file) and prod_files and not test_files and not adv_active:
                try:
                    with open(fsm_file, "r", encoding="utf-8") as f:
                        fsm = json.load(f)
                    if fsm.get("phase") == "TDD_RED":
                        warnings.append(
                            "STRICT TDD GATE VIOLATION: Production files were modified during TDD_RED phase "
                            f"({', '.join(prod_files[:4])}) without a corresponding test file change. "
                            "Write and run a failing test (Exit Code > 0) before modifying production code."
                        )
                except Exception as _fsm_err:
                    _log_telemetry(_fsm_err, "tdd_rollback")
    except Exception as _e:
        _log_telemetry(_e, "bento_tdd_gates")
    return warnings

def main():
    parser = argparse.ArgumentParser(description="Pre-Agent Wake Omni-Buffer Hook")
    parser.add_argument("--active-file", type=str, default="", help="Currently open file in IDE")
    parser.add_argument("--terminal-error", type=str, default="", help="Last terminal output or error")
    parser.add_argument("--ide-source", type=str, default="unknown", help="Caller IDE (antigravity, cursor, etc)")
    parser.add_argument("--user-intent", type=str, default="", help="Extracted intent from latest user prompt")
    parser.add_argument("--conversation-id", type=str, default="", help="Active conversation or session ID")
    parser.add_argument("--hook", action="store_true", help="Run in hook mode outputting valid JSON payload")
    
    args = parser.parse_args()

    # 0. Debounce & hook payload extraction (Self-healing auto-pipe detection)
    hook_payload = _read_stdin_nonblocking() or {}
    is_hook_mode = args.hook or bool(hook_payload)
    conversation_id = hook_payload.get("conversationId") or hook_payload.get("conversation_id")
    transcript_path = hook_payload.get("transcriptPath") or hook_payload.get("transcript_path")
    artifact_directory_path = hook_payload.get("artifactDirectoryPath") or hook_payload.get("artifact_directory_path")
    model_name = hook_payload.get("modelName") or hook_payload.get("model_name")
    invocation_num = hook_payload.get("invocationNum") or hook_payload.get("invocation_num")
    workspace_paths = hook_payload.get("workspacePaths", []) or hook_payload.get("workspace_paths", [])

    active_file = (
        hook_payload.get("activeFile")
        or hook_payload.get("active_file")
        or hook_payload.get("filePath")
        or args.active_file
        or ""
    )
    user_intent = (
        hook_payload.get("userIntent")
        or hook_payload.get("user_intent")
        or hook_payload.get("lastUserInput")
        or hook_payload.get("last_user_input")
        or hook_payload.get("prompt")
        or hook_payload.get("query")
        or args.user_intent
        or ""
    )
    terminal_error = (
        hook_payload.get("terminalError")
        or hook_payload.get("terminal_error")
        or hook_payload.get("error")
        or args.terminal_error
        or ""
    )

    if not user_intent and transcript_path and os.path.isfile(transcript_path):
        try:
            with open(transcript_path, "rb") as _tf:
                _tf.seek(0, os.SEEK_END)
                _size = _tf.tell()
                _seek_pos = max(0, _size - 8192)
                _tf.seek(_seek_pos)
                _tail_lines = _tf.read().decode("utf-8", errors="replace").splitlines()
                for _line in reversed(_tail_lines):
                    _line_s = _line.strip()
                    if not _line_s:
                        continue
                    try:
                        _step = json.loads(_line_s)
                        if _step.get("type") == "USER_INPUT" and _step.get("content"):
                            user_intent = str(_step.get("content"))
                            break
                    except Exception:
                        continue
        except Exception as _t_err:
            _log_telemetry(_t_err, "pre_agent_wake:read_transcript_tail")

    if not os.path.exists(CONTEXT_DIR):
        os.makedirs(CONTEXT_DIR, exist_ok=True)

    # Cold-Start Grounding & Priming Check (Evaluated before debounce)
    current_session_id = conversation_id or args.conversation_id or "default_session"
    now_ts = time.time()
    is_cold_start = False

    inv_num_int = None
    if invocation_num is not None:
        try:
            inv_num_int = int(invocation_num)
        except (ValueError, TypeError):
            pass

    active_sessions_file = os.path.join(CONTEXT_DIR, '.active_sessions.json')
    sessions_map = {}
    if os.path.exists(active_sessions_file):
        try:
            with open(active_sessions_file, 'r', encoding='utf-8') as asf:
                sessions_map = json.load(asf)
        except Exception:
            sessions_map = {}

    sess_entry = sessions_map.get(current_session_id, {})
    last_seen = float(sess_entry.get("last_seen", 0))
    already_cold_started = bool(sess_entry.get("cold_started", False))

    # A session must trigger cold-start on its very first wake turn, or if idle > 1h
    if not already_cold_started or (now_ts - last_seen > 3600):
        is_cold_start = True
    else:
        is_cold_start = False

    # If context.json is fresh (<15s), .git/index is unchanged, and NOT a cold start, fast-exit in <5ms.
    if (args.hook or is_hook_mode) and not is_cold_start and os.path.exists(CONTEXT_FILE):
        try:
            now = time.time()
            ctx_mtime = os.path.getmtime(CONTEXT_FILE)
            if (now - ctx_mtime) < 15.0 and not active_file and not terminal_error and not user_intent:
                git_index = os.path.join(WORKSPACE_DIR, ".git", "index")
                index_mtime = os.path.getmtime(git_index) if os.path.exists(git_index) else 0
                if index_mtime <= ctx_mtime:
                    print("{}")
                    return
        except Exception as _deb_err:
            _log_telemetry(_deb_err, "debounce_fast_exit")

    if not os.path.exists(CONTEXT_DIR):
        os.makedirs(CONTEXT_DIR, exist_ok=True)
        
    base_agents_dir = os.path.dirname(SCRIPT_DIR)
    learnings_path = os.path.join(base_agents_dir, "LEARNINGS.md")
    identity_path = os.path.join(WORKSPACE_DIR, 'context', 'AGENT_IDENTITY.md')
    fsm_state_path = os.path.join(CONTEXT_DIR, 'execution_state.json')
    
    # 1. Heartbeat Cron Logic
    evolution_overdue, unprocessed_learnings = _check_heartbeat(learnings_path, base_agents_dir)

    # 2. Knowledge Base Auto-Sync (Drift Detection)
    _check_and_sync(base_agents_dir, BASE_DIR)

    # 3. Identity Layer Bootstrap
    identity_exists, top_lessons = _bootstrap_identity(identity_path, base_agents_dir, learnings_path, WORKSPACE_DIR)

    # 4. Formal State Machine (Recovery Hook)
    recovery_instruction = _check_fsm(fsm_state_path)

    # 5. Bento-Box & Strict TDD Mechanical Gates
    drift_warnings = enforce_bento_and_tdd_gates(WORKSPACE_DIR, model_name or "", CONTEXT_DIR)
    graph_drift = _check_drift(active_file, BASE_DIR)
    if graph_drift:
        drift_warnings.extend(graph_drift)

    # 6. Sovereign Harness Lifecycle & Skill Index Surfacing
    harness_index = ""
    harness_lifecycle = {}
    session_id = conversation_id or args.conversation_id or os.environ.get("ANTIGRAVITY_CONVERSATION_ID") or "default_session"
    scripts_dir = os.path.join(base_agents_dir, 'scripts')
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    try:
        from core.harness.engine import HarnessEngine
        harness = HarnessEngine()
        harness.increment_request_count()
        if not args.hook:
            harness.promote_pending_queue()
        harness_lifecycle = harness.evaluate_lifecycle(maturity=100, capacity=50, execute_archive=False)
        harness_index = harness.build_session_index(max_desc_chars=90)
    except Exception as _h_err:
        _log_telemetry(_h_err, "harness_lifecycle_pre_wake")

    # 7. Virtual Core Memory (Tier 0 - Persona & Human Invariants)
    core_memory_data = {}
    core_memory_prompt = ""
    try:
        from commands.brain import CoreMemoryManager
        core_mem_mgr = CoreMemoryManager()
        core_memory_data = core_mem_mgr.get_all()
        core_memory_prompt = core_mem_mgr.format_prompt_block()
    except Exception as _cm_err:
        _log_telemetry(_cm_err, "core_memory_pre_wake")

    # 7b. Multi-Layer Memory Facts (Tier 1 - Semantic Facts)
    multi_layer_facts = {}
    try:
        from core.memory import MultiLayerMemoryManager
        ml_mgr = MultiLayerMemoryManager()
        try:
            multi_layer_facts = ml_mgr.get_facts()
        finally:
            ml_mgr.close()
    except Exception as _ml_err:
        _log_telemetry(_ml_err, "multi_layer_memory_pre_wake")

    # 8. Session Quantum Telemetry
    session_telemetry = {}
    try:
        from core.harness.capture import ToolQuantumCapture
        harness_state_dir = os.path.join(WORKSPACE_DIR, '.orion', 'harness')
        capture = ToolQuantumCapture(state_dir=harness_state_dir)
        session_state = capture.load_session(session_id)
        session_telemetry = {
            "session_id": session_state.session_id,
            "tool_call_count": session_state.tool_call_count,
            "calls_since_last_reflection": session_state.tool_call_count - session_state.last_reflection_call,
            "quantum_threshold": capture.quantum_threshold,
            "active": session_state.active
        }
    except Exception as _st_err:
        _log_telemetry(_st_err, "session_telemetry_pre_wake")
            
    def sanitize_input(text):
        if not text: return text
        # Neutralize XML breakout and markdown formatting
        text = re.sub(r'</?[a-zA-Z0-9_\-]+[^>]*>', '', text)
        text = text.replace("```", "").replace("###", "").replace("##", "").replace("#", "")
        try:
            from core.security import INJECTION_HEURISTIC_PATTERNS
            for pattern, _desc in INJECTION_HEURISTIC_PATTERNS:
                text = pattern.sub("[REDACTED]", text)
        except Exception:
            overrides = ["ignore previous", "system prompt", "forget all", "disregard", "you are now"]
            for override in overrides:
                text = re.sub(f"(?i){override}", "[REDACTED]", text)
        return text.strip()

    # 8b. Record conversational turn into rolling recall memory
    if user_intent and user_intent.strip():
        try:
            from core.memory import RecallMemoryManager
            with RecallMemoryManager() as recall:
                recall.record_turn("user", sanitize_input(user_intent))
        except Exception as _rt_err:
            _log_telemetry(_rt_err, "pre_wake:record_turn")

    # 9. 2-Stage JIT Skill Router
    matched_skills = []
    skill_routes_path = os.path.join(WORKSPACE_DIR, '.orion', 'matrix', 'skill_routes.json')
    query_text = f"{sanitize_input(user_intent)} {active_file} {sanitize_input(terminal_error)}".lower()
    
    if os.path.exists(skill_routes_path) and query_text.strip():
        try:
            with open(skill_routes_path, 'r', encoding='utf-8') as f:
                routes = json.load(f)
            
            scored_matches = []
            for r in routes:
                score = 0
                name = r.get("name", "")
                triggers = r.get("triggers", [])
                for trig in triggers:
                    t_low = trig.lower().strip()
                    if not t_low:
                        continue
                    if " " in t_low:
                        if t_low in query_text:
                            score += 3 if t_low == name.lower() else 2
                    else:
                        if re.search(rf"\b{re.escape(t_low)}\b", query_text):
                            score += 3 if t_low == name.lower() else 1
                if re.search(rf"\b{re.escape(name.lower())}\b", query_text):
                    score += 4
                if score > 0:
                    scored_matches.append((score, r))
            
            scored_matches.sort(key=lambda x: x[0], reverse=True)
            for _, sk in scored_matches[:3]:
                matched_skills.append({
                    "name": sk.get("name"),
                    "skill_path": sk.get("skill_path"),
                    "description": sk.get("description"),
                    "references": sk.get("references", [])
                })
                try:
                    from core.harness.engine import HarnessEngine
                    HarnessEngine.record_skill_event(sk.get("name"), "view")
                except Exception as _rse:
                    _log_telemetry(_rse, "pre_wake:record_skill_event")
        except Exception as _sr_err:
            _log_telemetry(_sr_err, "skill_router_pre_wake")

    handoff_file = os.path.join(CONTEXT_DIR, "cloud_handoff_queue.json")
    pending_cloud_handoffs = []
    if os.path.exists(handoff_file):
        try:
            with open(handoff_file, "r", encoding="utf-8") as _hf:
                _hdata = json.load(_hf)
                _htasks = _hdata if isinstance(_hdata, list) else _hdata.get("tasks", [])
                pending_cloud_handoffs = [t for t in _htasks if t.get("status") == "pending"]
        except Exception as _he:
            _log_telemetry(_he, "pre_wake:cloud_handoff_queue")

    delegation_dirs = [
        os.path.join(BASE_DIR, ".agents", "working", "delegations"),
        os.path.join(BASE_DIR, ".orion", "working", "delegations"),
    ]
    delegation_deltas = []
    for d_dir in delegation_dirs:
        if os.path.exists(d_dir):
            try:
                for d_file in os.listdir(d_dir):
                    if d_file.startswith("result-") and (d_file.endswith(".md") or d_file.endswith(".jsonl")):
                        d_path = os.path.join(d_dir, d_file)
                        try:
                            with open(d_path, "r", encoding="utf-8", errors="ignore") as _df:
                                raw_lines = _df.readlines()
                            for line in raw_lines:
                                line_s = line.strip()
                                if line_s.startswith("{") and line_s.endswith("}") and "target_file" in line_s:
                                    try:
                                        delta_item = json.loads(line_s)
                                        if isinstance(delta_item, dict) and "target_file" in delta_item:
                                            delta_item["source_delegation"] = d_file
                                            delegation_deltas.append(delta_item)
                                    except Exception:
                                        pass
                            full_text = "".join(raw_lines)
                            fenced_blocks = re.findall(r'```(?:jsonl|json)\s*\n(.*?)\n```', full_text, flags=re.DOTALL)
                            for block in fenced_blocks:
                                for blk_line in block.splitlines():
                                    blk_s = blk_line.strip()
                                    if blk_s.startswith("{") and blk_s.endswith("}") and "target_file" in blk_s:
                                        try:
                                            item = json.loads(blk_s)
                                            if isinstance(item, dict) and "target_file" in item:
                                                if not any(d.get("target_file") == item.get("target_file") and d.get("ast_span") == item.get("ast_span") for d in delegation_deltas):
                                                    item["source_delegation"] = d_file
                                                    delegation_deltas.append(item)
                                        except Exception:
                                            pass
                        except Exception as _fe:
                            _log_telemetry(_fe, f"pre_wake:read_delegation:{d_file}")
            except Exception as _de:
                _log_telemetry(_de, "pre_wake:delegations_dir")
    delegation_deltas = delegation_deltas[:25]

    project_dna_data = None
    dna_file = os.path.join(WORKSPACE_DIR, ".agents", ".dna.json")
    if os.path.isfile(dna_file):
        try:
            with open(dna_file, "r", encoding="utf-8", errors="ignore") as df:
                raw_dna = json.load(df)
                ledger = raw_dna.get("mutation_ledger", {}) if isinstance(raw_dna.get("mutation_ledger"), dict) else {}
                viols = raw_dna.get("layer_violations") if "layer_violations" in raw_dna else ledger.get("layer_violations", [])
                comp_score = raw_dna.get("dna_compliance_score") if "dna_compliance_score" in raw_dna else ledger.get("dna_compliance_score", 100)
                project_dna_data = {
                    "schema_version": raw_dna.get("schema_version", "0.0.1"),
                    "dna_state": raw_dna.get("dna_state", "BORN"),
                    "archetype": raw_dna.get("archetype", "Software Repository"),
                    "ecosystem": raw_dna.get("ecosystem") or raw_dna.get("primary_framework") or raw_dna.get("framework", "generic"),
                    "stacks": raw_dna.get("stacks", []),
                    "compliance_score": comp_score,
                    "execution_spine": raw_dna.get("execution_spine", [])[:6],
                    "invariants": raw_dna.get("invariants", [])[:5],
                    "layer_violations_count": len(viols) if isinstance(viols, list) else 0,
                }
        except Exception as _de:
            _log_telemetry(_de, "pre-agent-wake:read_dna")

    obs_digest = None
    obs_broken_probe = False
    try:
        from commands.reflexion import ObservationLedger
        obs_ledger = ObservationLedger(
            active_path=os.path.join(base_agents_dir, "OBSERVATIONS.md"),
            archive_path=os.path.join(base_agents_dir, "OBSERVATIONS.archive.md")
        )
        obs_digest = obs_ledger.get_digest()
        if obs_digest == "OBSERVATION SCAN BROKEN":
            obs_broken_probe = True
    except Exception as _obs_err:
        _log_telemetry(_obs_err, "pre_wake:observation_ledger")

    active_bento_task_data = None
    bento_queue_file = os.path.join(CONTEXT_DIR, "bento_queue.json")
    if os.path.isfile(bento_queue_file):
        try:
            with open(bento_queue_file, "r", encoding="utf-8") as _bqf:
                _bqdata = json.load(_bqf)
            _bidx = int(_bqdata.get("current_index", 0))
            _btasks = _bqdata.get("tasks", [])
            if _bidx < len(_btasks):
                _bt = _btasks[_bidx]
                active_bento_task_data = {
                    "index": f"{_bidx + 1}/{len(_btasks)}",
                    "task_id": _bt.get("task_id"),
                    "title": _bt.get("title"),
                    "target_file": _bt.get("target_file"),
                    "lines": f"L{_bt.get('start_line')}-L{_bt.get('end_line')}",
                    "instruction": f"Read .orion/working/ACTIVE_TASK.md and execute ONLY Task {_bt.get('task_id')}.",
                }
        except Exception as _bqe:
            _log_telemetry(_bqe, "pre_wake:bento_queue")

    context_payload = {
        "timestamp_ms": int(time.time() * 1000),
        "active_file": active_file,
        "terminal_error": sanitize_input(terminal_error),
        "user_intent": sanitize_input(user_intent),
        "ide_source": args.ide_source if args.ide_source != "unknown" else ("antigravity" if hook_payload else "unknown"),
        "evolution_overdue": evolution_overdue,
        "unprocessed_learnings": unprocessed_learnings,
        "identity_path": os.path.relpath(identity_path, WORKSPACE_DIR).replace(os.sep, '/') if identity_exists else None,
        "top_lessons": top_lessons,
        "drift_warnings": drift_warnings,
        "pending_cloud_handoffs": pending_cloud_handoffs,
        "delegation_deltas": delegation_deltas,
        "core_memory": core_memory_data,
        "core_memory_prompt": core_memory_prompt,
        "multi_layer_facts": multi_layer_facts,
        "session_telemetry": session_telemetry,
        "matched_skills": matched_skills,
        "harness_skill_index": harness_index,
        "harness_lifecycle": {
            "retained_count": harness_lifecycle.get("retained_count", 0),
            "probation_count": harness_lifecycle.get("probation_count", 0),
            "archived_count": harness_lifecycle.get("archived_count", 0)
        } if harness_lifecycle else None,
        "project_dna": project_dna_data,
        "observation_digest": obs_digest,
        "active_bento_task": active_bento_task_data,
        "antigravity": {
            "conversation_id": conversation_id,
            "transcript_path": transcript_path,
            "artifact_directory_path": artifact_directory_path,
            "model_name": model_name,
            "invocation_num": invocation_num,
            "workspace_paths": workspace_paths
        } if hook_payload else None
    }
    
    if recovery_instruction:
        context_payload["recovery_instruction"] = recovery_instruction

    # Cache-Aware Idle Activation & Temporal Gap Marker
    DEFAULT_CACHE_TTL_MS = 5 * 60 * 1000  # 5 minutes prompt-cache TTL
    now_ms = context_payload["timestamp_ms"]
    skip_write = False

    if os.path.exists(CONTEXT_FILE):
        try:
            with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
                prev_ctx = json.load(f)
            prev_time_ms = int(prev_ctx.get("timestamp_ms", 0))

            # Temporal gap marker (>1 hour)
            if prev_time_ms > 0 and (now_ms - prev_time_ms) >= 3600 * 1000:
                elapsed_hrs = (now_ms - prev_time_ms) / (3600 * 1000)
                context_payload["temporal_gap_marker"] = f"⏳ Temporal Gap: {elapsed_hrs:.1f}h elapsed since previous agent turn."

            # Compute structural fingerprint (excluding volatile timestamp_ms)
            def _struct_hash(d: dict) -> str:
                import hashlib
                subset = {
                    "active_file": d.get("active_file"),
                    "terminal_error": d.get("terminal_error"),
                    "active_bento_task": d.get("active_bento_task"),
                    "recovery_instruction": d.get("recovery_instruction"),
                    "drift_warnings": d.get("drift_warnings"),
                    "observation_digest": d.get("observation_digest"),
                    "matched_skills": [s.get("name") for s in d.get("matched_skills", [])]
                }
                return hashlib.sha256(json.dumps(subset, sort_keys=True).encode("utf-8")).hexdigest()

            curr_hash = _struct_hash(context_payload)
            prev_hash = _struct_hash(prev_ctx)

            # Preserve cache prefix if structural state is identical and within TTL window (never skip on cold start)
            if curr_hash == prev_hash and (now_ms - prev_time_ms) < DEFAULT_CACHE_TTL_MS and not is_cold_start:
                skip_write = True
        except Exception as _ctx_err:
            _log_telemetry(_ctx_err, "pre_wake:ttl_check")

    if not skip_write:
        temp_file = f"{CONTEXT_FILE}.tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(context_payload, f, indent=2)
            os.replace(temp_file, CONTEXT_FILE)
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
        
    _check_passive_orion_gc(BASE_DIR)

    active_warnings = []

    # Persist session tracking in multi-session dictionary
    try:
        active_sessions_file = os.path.join(CONTEXT_DIR, '.active_sessions.json')
        sessions_map = {}
        if os.path.exists(active_sessions_file):
            try:
                with open(active_sessions_file, 'r', encoding='utf-8') as asf:
                    sessions_map = json.load(asf)
            except Exception:
                sessions_map = {}
        
        sessions_map[current_session_id] = {
            "last_seen": now_ts,
            "cold_started": True,
            "last_invocation": inv_num_int
        }
        
        # Clean up sessions older than 24 hours
        sessions_map = {
            sid: sdata for sid, sdata in sessions_map.items()
            if (now_ts - float(sdata.get("last_seen", 0))) < 86400
        }
        
        with open(active_sessions_file, 'w', encoding='utf-8') as asf:
            json.dump(sessions_map, asf, indent=2)
    except Exception:
        pass

    if is_cold_start:
        os_label = "Windows" if os.name == 'nt' else ("macOS" if sys.platform == 'darwin' else "Linux")
        shell_label = "PowerShell (LF line endings, UTF-8 mode, no '&&' separators)" if os.name == 'nt' else "POSIX (bash/zsh)"
        
        accel_info = "7/7 Active"
        try:
            from core.accelerators import get_active_accelerator_manifest
            accel_m = get_active_accelerator_manifest()
            accel_active = sum(1 for v in accel_m.values() if v.get("status") == "active")
            accel_info = f"{accel_active}/7 Active"
        except Exception:
            pass

        cold_start_lines = [
            "🌐 [FOUNDATION COGNITION: COLD-START INVARIANTS]",
            "• Architecture: Universal Agnostic | 100% Zero-Pip Floor Sovereignty | 4-Pillar Sovereign Mesh",
            f"• Host Environment: {os_label} [{shell_label}] | Python {sys.version.split()[0]} stdlib | Tier 2 Accel: {accel_info}",
            "• Ecosystem Scope: Multi-Project (Flutter, React, Android, Python, Systems) | Multi-OS | Multi-IDE (Antigravity, Cursor, Claude Code, VS Code)",
            "• Pillars: P1 (Py stdlib floor) | P2 (Rust rtk+ast-grep+difft+gl+jj) | P3 (Ollama Local AI) | P4 (Bun)",
            "• Constitutional North Star: VISION.md Immutable Lock | Anti-Enterprise-Bloat | YAGNI | Evidence Mandate (Exit Code 0) | Lessword Token Efficiency"
        ]

        handoff_path = os.path.join(CONTEXT_DIR, "handoff.md")
        if os.path.exists(handoff_path):
            try:
                with open(handoff_path, "r", encoding="utf-8") as hf:
                    h_text = hf.read()
                m = re.search(r'## 1\. Resume Point\s*\n(.*?)(?=\n## |\Z)', h_text, re.DOTALL)
                if m:
                    res_point = m.group(1).strip()
                    if res_point and not res_point.startswith("["):
                        cold_start_lines.append(f"📌 RESUME POINT (.orion/working/handoff.md):\n{res_point[:300]}")
            except Exception:
                pass

        # User-Configured Anchor Targets (Optional: from .cold_start.json or .dna.json)
        anchor_file = os.path.join(base_agents_dir, ".cold_start.json")
        if os.path.exists(anchor_file):
            try:
                with open(anchor_file, "r", encoding="utf-8") as af:
                    adata = json.load(af)
                anchors = adata.get("anchor_targets", [])
                if anchors:
                    cold_start_lines.append("🎯 USER ANCHOR TARGETS: " + ", ".join(anchors[:5]))
            except Exception:
                pass

        # Core Memory (Tier 0 - Persona & Human Invariants)
        if core_memory_prompt and core_memory_prompt.strip():
            cold_start_lines.append(core_memory_prompt.strip())

        # Anchor Triplets from orion.db (Tier 1 - Semantic Invariants)
        db_path = os.path.join(BASE_DIR, '.orion', 'orion.db')
        if os.path.exists(db_path):
            try:
                import sqlite3
                with sqlite3.connect(db_path, timeout=2.0) as conn:
                    preds = ('governs', 'enforces', 'mandates', 'calibrates', 'orchestrates')
                    c = conn.cursor()
                    c.execute("SELECT subject_id, predicate, object_id FROM relations WHERE predicate IN (?, ?, ?, ?, ?) LIMIT 6", preds)
                    triplets = c.fetchall()
                    if triplets:
                        triplet_str = " • " + "\n • ".join([f"({s} -> {p} -> {o})" for s, p, o in triplets])
                        cold_start_lines.append(f"🧬 [GRAPH ANCHOR TRIPLETS (orion.db)]:\n{triplet_str}")
            except Exception as _tr_err:
                _log_telemetry(_tr_err, "cold_start_triplets")

        active_warnings.append("\n".join(cold_start_lines))
    if active_bento_task_data:
        active_warnings.append(
            f"🎯 ACTIVE BENTO TASK ({active_bento_task_data['index']}): "
            f"Task {active_bento_task_data['task_id']} on `{active_bento_task_data['target_file']}` ({active_bento_task_data['lines']}). "
            "Execute ONLY this single task in .orion/working/ACTIVE_TASK.md before verifying."
        )
    if recovery_instruction:
        active_warnings.append(recovery_instruction)
    if drift_warnings:
        active_warnings.extend(drift_warnings)
    if pending_cloud_handoffs:
        active_warnings.append(
            f"⚡ PENDING CLOUD HANDOFFS ({len(pending_cloud_handoffs)}): " +
            ", ".join(f"{h.get('task_type')} ({h.get('reason')})" for h in pending_cloud_handoffs[:3])
        )
    if delegation_deltas:
        active_warnings.append(
            f"🧩 ACTIVE DELEGATION DELTAS ({len(delegation_deltas)}): " +
            ", ".join(f"{d.get('target_file')}:{d.get('ast_span', '')} ({d.get('action_recipe', '')[:35]})" for d in delegation_deltas[:3])
        )
    if project_dna_data and project_dna_data.get("layer_violations_count", 0) > 0:
        active_warnings.append(
            f"⚠️ DNA ARCHITECTURE VIOLATIONS ({project_dna_data['layer_violations_count']}): Run 'python .agents/scripts/orion.py dna audit' to inspect."
        )
    if obs_broken_probe:
        active_warnings.append(
            "🚨 OBSERVATION SCAN BROKEN: Raw observations present in .agents/OBSERVATIONS.md but parser returned 0 entries!"
        )
    elif obs_digest:
        active_warnings.append(f"👁️ OBSERVATION DIGEST: {obs_digest}")

    ephemeral_msg = "\n\n".join(active_warnings) if active_warnings else ""
        
    if is_hook_mode:
        if ephemeral_msg:
            step_payload = (
                {"systemMessage": {"systemMessage": ephemeral_msg}}
                if is_cold_start
                else {"ephemeralMessage": ephemeral_msg}
            )
            print(json.dumps({
                "injectSteps": [step_payload]
            }))
        else:
            print("{}")
    else:
        print(f"[OK] Omni-Buffer updated at {os.path.relpath(CONTEXT_FILE, WORKSPACE_DIR)}")

if __name__ == "__main__":
    main()
