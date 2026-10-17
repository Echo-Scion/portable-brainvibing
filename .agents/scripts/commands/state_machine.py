#!/usr/bin/env python
"""
state_machine.py — Formal State Machine (FSM), Budget & Asset Eviction Engine
Provides a crash-proof runtime execution tracker, SMS budget KPIs, and amnesia asset eviction.
Consolidates state_machine.py, track_budget.py, and rule_eviction.py.
"""
import os
import sys
import json
import time
import shutil
import sqlite3
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable, Tuple

# Force utf-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
STATE_FILE = os.path.join(WORKSPACE_DIR, '.orion', 'working', 'execution_state.json')
BUDGET_LOG = os.path.join(WORKSPACE_DIR, ".orion", "working", "budget_telemetry.json")

sys.path.insert(0, os.path.abspath(os.path.join(SCRIPT_DIR, "..")))

try:
    from core.db import log_telemetry as _log_telemetry, connect_sqlite, atomic_write_text
except ImportError:
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        pass
    connect_sqlite = sqlite3.connect

    def atomic_write_text(path: str, content: str) -> None:
        tmp = f"{path}.tmp.{os.getpid()}"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(content)
        os.replace(tmp, path)


END = "__END__"


class StateGraph:
    """
    Pillar 1: Cyclic State Machine Engine & Transactional Checkpointer.
    Provides cyclic directed execution graph with branch routing, keyed channel reducers,
    and transactional SQLite checkpointing.
    """

    def __init__(self, schema_or_db: Any = None, db_path: Optional[str] = None):
        self.nodes: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Tuple[Callable[[Dict[str, Any]], str], Optional[Dict[str, str]]]] = {}
        self.entry_point: Optional[str] = None
        self.reducers: Dict[str, Callable[[Any, Any], Any]] = {}

        if isinstance(schema_or_db, str):
            self.db_path = schema_or_db
            self.schema = None
        else:
            self.schema = schema_or_db
            self.db_path = db_path

        if not self.db_path:
            self.db_path = os.path.join(WORKSPACE_DIR, ".orion", "orion.db")

        self.conn = connect_sqlite(self.db_path)
        self._init_db()

    def _init_db(self) -> None:
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS fsm_checkpoints (
                        thread_id TEXT,
                        step INTEGER,
                        node TEXT,
                        state_json TEXT,
                        timestamp REAL,
                        git_tree_sha TEXT,
                        PRIMARY KEY (thread_id, step)
                    );
                """)
                cur = self.conn.cursor()
                cur.execute("PRAGMA table_info(fsm_checkpoints);")
                cols = [r[1] for r in cur.fetchall()]
                if "git_tree_sha" not in cols:
                    self.conn.execute("ALTER TABLE fsm_checkpoints ADD COLUMN git_tree_sha TEXT;")
        except Exception as e:
            _log_telemetry(e, "state_graph.py:_init_db")

    def add_node(self, name: str, fn: Callable[[Dict[str, Any]], Dict[str, Any]]) -> "StateGraph":
        if name == END:
            raise ValueError(f"Node name cannot be reserved identifier '{END}'")
        self.nodes[name] = fn
        if self.entry_point is None:
            self.entry_point = name
        return self

    def add_edge(self, src: str, dst: str) -> "StateGraph":
        self.edges[src] = dst
        return self

    def add_conditional_edge(
        self,
        src: str,
        router: Callable[[Dict[str, Any]], str],
        path_map: Optional[Dict[str, str]] = None
    ) -> "StateGraph":
        self.conditional_edges[src] = (router, path_map)
        return self

    def set_entry_point(self, name: str) -> "StateGraph":
        self.entry_point = name
        return self

    def set_reducer(self, key: str, reducer_fn: Callable[[Any, Any], Any]) -> "StateGraph":
        self.reducers[key] = reducer_fn
        return self

    def _apply_reducers(self, state: Dict[str, Any], delta: Dict[str, Any]) -> Dict[str, Any]:
        updated = dict(state)
        for k, v in delta.items():
            if k in self.reducers and k in updated:
                updated[k] = self.reducers[k](updated[k], v)
            else:
                updated[k] = v
        return updated

    def _save_checkpoint(self, thread_id: str, step: int, node: str, state: Dict[str, Any], git_tree_sha: Optional[str] = None) -> None:
        try:
            sha = git_tree_sha or state.get("_git_tree_sha")
            with self.conn:
                self.conn.execute("""
                    INSERT OR REPLACE INTO fsm_checkpoints (thread_id, step, node, state_json, timestamp, git_tree_sha)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (thread_id, step, node, json.dumps(state, default=str), time.time(), sha))
        except Exception as e:
            _log_telemetry(e, f"state_graph.py:_save_checkpoint:{thread_id}:{step}")

    def load_checkpoint(self, thread_id: str, step: Optional[int] = None) -> Optional[Dict[str, Any]]:
        try:
            cur = self.conn.cursor()
            if step is not None:
                cur.execute("SELECT state_json, git_tree_sha FROM fsm_checkpoints WHERE thread_id = ? AND step = ?", (thread_id, step))
            else:
                cur.execute("SELECT state_json, git_tree_sha FROM fsm_checkpoints WHERE thread_id = ? ORDER BY step DESC LIMIT 1", (thread_id,))
            row = cur.fetchone()
            if row and row[0]:
                data = json.loads(row[0])
                if len(row) > 1 and row[1]:
                    data["_git_tree_sha"] = row[1]
                return data
            return None
        except Exception as e:
            _log_telemetry(e, f"state_graph.py:load_checkpoint:{thread_id}")
            return None

    def run(
        self,
        initial_state: Optional[Dict[str, Any]] = None,
        thread_or_start: str = "default",
        max_steps: int = 50,
        start_step: int = 0
    ) -> Dict[str, Any]:
        state = dict(initial_state or {})
        if thread_or_start in self.nodes and not self.entry_point:
            curr_node: str = thread_or_start
            thread_id: str = "default"
        else:
            curr_node = self.entry_point or (list(self.nodes.keys())[0] if self.nodes else None)
            thread_id = thread_or_start

        if not curr_node:
            raise RuntimeError("Cannot run StateGraph: entry point not configured.")

        step = start_step
        end_markers = (END, "END", "__END__", None)

        while curr_node not in end_markers and step < (start_step + max_steps):
            if curr_node not in self.nodes:
                raise KeyError(f"Encountered unregistered node '{curr_node}' in StateGraph.")

            node_fn = self.nodes[curr_node]
            mutation = node_fn(state) or {}
            state = self._apply_reducers(state, mutation)

            self._save_checkpoint(thread_id, step, curr_node, state)
            step += 1

            if curr_node in self.conditional_edges:
                router, path_map = self.conditional_edges[curr_node]
                dest = router(state)
                if path_map and dest in path_map:
                    curr_node = path_map[dest]
                else:
                    curr_node = dest
            elif curr_node in self.edges:
                curr_node = self.edges[curr_node]
            else:
                curr_node = END

        if step >= (start_step + max_steps) and curr_node not in end_markers:
            sys.stderr.write(f"[STATE_GRAPH WARNING] Execution reached cycle limit ({max_steps} supersteps). Aborting loop.\n")

        return state

    invoke = run

    def close(self) -> None:
        if self.conn:
            try:
                self.conn.close()
            except Exception as _e:
                _log_telemetry(_e, "state_graph.py:close")
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ==============================================================================
# 1. GIT SNAPSHOTS & CORE FSM
# ==============================================================================

def get_git_tree_sha() -> Optional[str]:
    """Non-destructively gets current git commit or stash object SHA representing code state."""
    try:
        res = subprocess.run(["git", "stash", "create"], capture_output=True, text=True, timeout=5)
        stash_sha = res.stdout.strip()
        if stash_sha:
            return stash_sha
        res_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=3)
        if res_head.returncode == 0:
            return res_head.stdout.strip()
    except Exception as _e:
        _log_telemetry(_e, "state_machine.py:get_git_tree_sha")
    return None

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[FSM ERROR] Corrupted execution state at {STATE_FILE}: {e}", file=sys.stderr)
    return None

def save_state(state_data):
    dir_path = os.path.dirname(STATE_FILE)
    os.makedirs(dir_path, exist_ok=True)
    atomic_write_text(STATE_FILE, json.dumps(state_data, indent=2))

def _save_checkpoint(state):
    git_sha = get_git_tree_sha()
    if git_sha:
        state["_git_tree_sha"] = git_sha
    graph = StateGraph(db_path=os.path.join(WORKSPACE_DIR, ".orion", "orion.db"))
    try:
        with graph.conn:
            row = graph.conn.execute(
                "SELECT COALESCE(MAX(step), -1) FROM fsm_checkpoints WHERE thread_id = ?",
                (state["session_id"],),
            ).fetchone()
            step = int(row[0]) + 1
        graph._save_checkpoint(state["session_id"], step, state.get("phase", "UNKNOWN"), state, git_tree_sha=git_sha)
    finally:
        graph.conn.close()

def persist_state(state):
    save_state(state)
    _save_checkpoint(state)

def cmd_init(session_id="default"):
    state = {
        "session_id": session_id,
        "phase": "IDLE",
        "active_tasks": {},
        "completed_tasks": [],
        "last_updated": datetime.now().isoformat()
    }
    persist_state(state)
    print(f"[FSM] Initialized execution state for session '{session_id}'.")

def cmd_transition(new_phase):
    state = load_state()
    if not state:
        print("[FSM ERROR] No active execution state found. Run init first.", file=sys.stderr)
        sys.exit(1)
    active_running = [k for k, v in state.get("active_tasks", {}).items() if v.get("status") == "RUNNING"]
    if new_phase.upper() == "DONE" and active_running:
        print(
            f"[FSM GATE BLOCKED] Cannot transition to DONE while tasks are still RUNNING: {', '.join(active_running)}",
            file=sys.stderr,
        )
        sys.exit(1)
    old_phase = state.get("phase", "UNKNOWN")
    state["phase"] = new_phase
    state["last_updated"] = datetime.now().isoformat()

    # Mirror transition execution into StateGraph
    try:
        session_id = state.get("session_id", "default")
        db_path = os.path.join(WORKSPACE_DIR, ".orion", "orion.db")
        graph = StateGraph(db_path=db_path)
        try:
            with graph.conn:
                row = graph.conn.execute(
                    "SELECT COALESCE(MAX(step), -1) FROM fsm_checkpoints WHERE thread_id = ?",
                    (session_id,),
                ).fetchone()
                next_step = int(row[0]) + 1 if row else 0
            graph.add_node(new_phase, lambda s: {"phase": new_phase, "last_updated": datetime.now().isoformat()})
            graph.set_entry_point(new_phase)
            res = graph.run(initial_state=state, thread_or_start=session_id, max_steps=1, start_step=next_step)
            state.update(res)
        finally:
            graph.close()
    except Exception as _e:
        _log_telemetry(_e, "state_machine:cmd_transition_graph")

    save_state(state)
    print(f"[FSM] Phase transition: {old_phase} -> {new_phase}")

def cmd_task_start(task_id):
    state = load_state()
    if not state:
        print("[FSM ERROR] No active execution state found. Run init first.", file=sys.stderr)
        sys.exit(1)
    state["active_tasks"][task_id] = {
        "status": "RUNNING",
        "started_at": datetime.now().isoformat()
    }
    state["last_updated"] = datetime.now().isoformat()
    persist_state(state)
    print(f"[FSM] Task started: '{task_id}'")

def cmd_task_end(task_id, status="COMPLETED"):
    state = load_state()
    if not state:
        print("[FSM ERROR] No active execution state found. Run init first.", file=sys.stderr)
        sys.exit(1)
    if task_id in state["active_tasks"]:
        del state["active_tasks"][task_id]
    
    state["completed_tasks"].append({
        "task_id": task_id,
        "status": status,
        "ended_at": datetime.now().isoformat()
    })
    state["last_updated"] = datetime.now().isoformat()
    persist_state(state)
    print(f"[FSM] Task ended: '{task_id}' with status {status}")

def cmd_rollback(session_id, step=None, restore_code=False):
    graph = StateGraph(db_path=os.path.join(WORKSPACE_DIR, ".orion", "orion.db"))
    try:
        state = graph.load_checkpoint(session_id, step=step)
    finally:
        graph.close()

    if not state or not isinstance(state, dict):
        print(f"[FSM ERROR] No checkpoint found for session '{session_id}'" + (f" at step {step}" if step else ""), file=sys.stderr)
        sys.exit(1)

    if restore_code:
        git_sha = state.get("_git_tree_sha")
        if git_sha:
            try:
                dirty_sha = get_git_tree_sha()
                if dirty_sha and dirty_sha != git_sha:
                    subprocess.run(
                        ["git", "stash", "store", "-m", f"pre-rollback-backup-{session_id}", dirty_sha],
                        capture_output=True, text=True, timeout=5, shell=False
                    )
                    print(f"[FSM] Saved dirty working tree backup to stash ({dirty_sha[:8]}).")
                ret = subprocess.run(
                    ["git", "checkout", git_sha, "--", "."],
                    capture_output=True, text=True, timeout=10, shell=False
                )
                if ret.returncode == 0:
                    print(f"[FSM] Restored codebase files to snapshot {git_sha[:8]}.")
                else:
                    print(f"[FSM WARNING] Codebase restoration returned code {ret.returncode}: {ret.stderr.strip()}", file=sys.stderr)
            except Exception as e:
                print(f"[FSM ERROR] Failed to restore code state: {e}", file=sys.stderr)
        else:
            print(f"[FSM WARNING] No git_tree_sha found in checkpoint for '{session_id}'. Skipping code restore.")

    persist_state(state)
    print(f"[FSM] Restored checkpoint for '{session_id}'.")

def cmd_status():
    state = load_state()
    if not state:
        print("No active execution state.")
        sys.exit(1)
    else:
        print(json.dumps(state, indent=2))


# ==============================================================================
# 2. BUDGET & SMALL MODEL SUPERIORITY (SMS) TELEMETRY
# ==============================================================================

def log_task_execution(task_name: str, tier: str, model_used: str, was_harness_used: bool, aborted_to_premium: bool):
    os.makedirs(os.path.dirname(BUDGET_LOG), exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task_name,
        "declared_tier": tier,
        "model": model_used,
        "harness_driven": was_harness_used,
        "auto_aborted": aborted_to_premium
    }
    data = []
    if os.path.exists(BUDGET_LOG):
        try:
            with open(BUDGET_LOG, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            sys.stderr.write(f"[WARN] Failed to parse budget log: {e}\n")
    data.append(entry)
    atomic_write_text(BUDGET_LOG, json.dumps(data, indent=4))
    print(f"[INFO] Telemetry logged. Task: {task_name} | Tier: {tier} | Aborted: {aborted_to_premium}")

def print_telemetry_report():
    if not os.path.exists(BUDGET_LOG):
        print("No telemetry data found. Start executing tasks to build Small Model Superiority metrics.")
        return
    with open(BUDGET_LOG, 'r', encoding='utf-8') as f:
        data = json.load(f)
    total_tasks = len(data)
    if total_tasks == 0:
        print("No tasks logged yet.")
        return
    budget_only = sum(1 for d in data if d.get("declared_tier") == "BUDGET" and not d.get("auto_aborted"))
    premium_handoffs = sum(1 for d in data if d.get("auto_aborted"))
    print("==================================================")
    print(" SMALL MODEL SUPERIORITY KPIs (ANTIGRAVITY IDE)")
    print("==================================================")
    print(f"Total Tasks Evaluated : {total_tasks}")
    print(f"Tasks Handled 100% by BUDGET Model: {budget_only} ({budget_only/total_tasks*100:.1f}%)")
    print(f"Tasks Handing off to PREMIUM (Harness Built): {premium_handoffs} ({premium_handoffs/total_tasks*100:.1f}%)")
    print("==================================================")
    print("Goal: Maintain >70% BUDGET resolution for Tier-0 tasks.")


# ==============================================================================
# 3. AMNESIA / DYNAMIC ASSET EVICTION
# ==============================================================================

def evict_assets(agents_dir=BASE_DIR, orion_db_path=None, archive_dir=None, base_days_threshold=30, apply=False):
    if orion_db_path is None:
        orion_db_path = os.path.join(WORKSPACE_DIR, ".orion", "orion.db")
    if archive_dir is None:
        archive_dir = os.path.join(WORKSPACE_DIR, ".orion", "archive")

    if not os.path.exists(agents_dir):
        print(f"Agents directory not found: {agents_dir}")
        return

    usage_data = {}
    if os.path.exists(orion_db_path):
        try:
            conn = connect_sqlite(orion_db_path)
            c = conn.cursor()
            c.execute("PRAGMA table_info(pages)")
            columns = [info[1] for info in c.fetchall()]
            if 'access_count' in columns and 'last_accessed' in columns:
                c.execute("SELECT path, access_count, last_accessed FROM pages")
                for row in c.fetchall():
                    path, access_count, last_accessed = row
                    if not access_count:
                        access_count = 0
                    if path:
                        norm_path = os.path.abspath(path).replace('\\', '/')
                        usage_data[norm_path] = {'access_count': access_count, 'last_accessed': last_accessed}
            conn.close()
            print(f"[DB] Loaded usage metrics for {len(usage_data)} items from orion.db")
        except Exception as e:
            print(f"[DB] Error loading metrics from orion.db: {e}")

    now = time.time()
    evict_count = 0
    target_dirs = ["canons/local"]
    print(f"--- SCANNING FOR STALE LOCAL ASSETS ---")
    protected_assets = {"README.md", ".gitkeep"}

    for t_dir in target_dirs:
        active_dir = os.path.join(agents_dir, t_dir)
        if not os.path.exists(active_dir):
            continue
        for root, _, files in os.walk(active_dir):
            for item in files:
                if item in protected_assets or item.startswith('.'):
                    continue
                filepath = os.path.join(root, item)
                norm_filepath = os.path.abspath(filepath).replace('\\', '/')
                days_old = 0
                threshold = base_days_threshold
                evict_reason = ""
                db_record = usage_data.get(norm_filepath)
                if db_record and db_record.get('last_accessed'):
                    last_acc_str = db_record['last_accessed']
                    try:
                        last_acc_dt = datetime.strptime(last_acc_str, "%Y-%m-%d %H:%M:%S")
                        days_old = (datetime.now() - last_acc_dt).days
                        threshold = 90 if db_record['access_count'] > 3 else 30
                        evict_reason = f"Usage (Acc: {db_record['access_count']}, Last: {days_old}d ago)"
                    except Exception:
                        mtime = os.path.getmtime(filepath)
                        days_old = (now - mtime) / (60 * 60 * 24)
                        evict_reason = f"Mtime Fallback ({days_old:.1f}d ago)"
                else:
                    mtime = os.path.getmtime(filepath)
                    days_old = (now - mtime) / (60 * 60 * 24)
                    evict_reason = f"Mtime ({days_old:.1f}d ago)"

                if days_old > threshold:
                    dest_dir = os.path.join(archive_dir, t_dir)
                    dest_path = os.path.join(dest_dir, item)
                    if apply:
                        os.makedirs(dest_dir, exist_ok=True)
                        try:
                            shutil.move(filepath, dest_path)
                            print(f"[EVICTED] {t_dir}/{item} -> {dest_dir} (Reason: {evict_reason})")
                            evict_count += 1
                        except Exception as e:
                            print(f"  [ERROR] Could not move {filepath}: {e}")
                    else:
                        print(f"[DRY-RUN] Would evict {t_dir}/{item} -> {dest_dir} (Reason: {evict_reason}, Threshold: {threshold}d)")
                        evict_count += 1

    print("-" * 40)
    mode_str = "Archived" if apply else "Found stale (run with --apply to move)"
    print(f"Eviction Complete: {evict_count} asset(s) {mode_str}.")


# ==============================================================================
# 4. CLI DISPATCH
# ==============================================================================

def main():
    if len(sys.argv) < 2 or any(arg in sys.argv for arg in ['--help', '-h']):
        print("Usage: state_machine.py <command> [args...]")
        print("  FSM Lifecycle:")
        print("    init [session_id]             — Initialize new state machine")
        print("    transition <PHASE>            — Transition to a new execution phase")
        print("    task_start <task_id>          — Mark task in progress")
        print("    task_end <task_id> <status>   — Mark task complete or failed")
        print("    rollback <session_id> [step] [--restore-code] — Restore SQLite checkpoint & code snapshot")
        print("    status                        — Print current execution state JSON")
        print("  Budget & Telemetry:")
        print("    budget [--report] [--tier <T>] [--task <name>] [--model <m>] [--harness] [--aborted]")
        print("  Asset Eviction (Amnesia):")
        print("    amnesia|evict [--apply] [--threshold <days>]")
        sys.exit(0 if any(arg in sys.argv for arg in ['--help', '-h']) else 1)
        
    action = sys.argv[1].lower()
    
    if action == "init":
        session_id = sys.argv[2] if len(sys.argv) > 2 else "default"
        cmd_init(session_id)
    elif action == "transition":
        if len(sys.argv) < 3:
            print("Usage: state_machine.py transition <PHASE>")
            sys.exit(1)
        cmd_transition(sys.argv[2])
    elif action == "task_start":
        if len(sys.argv) < 3:
            print("Usage: state_machine.py task_start <task_id>")
            sys.exit(1)
        cmd_task_start(sys.argv[2])
    elif action == "task_end":
        if len(sys.argv) < 4:
            print("Usage: state_machine.py task_end <task_id> <status>")
            sys.exit(1)
        cmd_task_end(sys.argv[2], sys.argv[3])
    elif action == "status":
        cmd_status()
    elif action == "rollback":
        if len(sys.argv) < 3:
            print("Usage: state_machine.py rollback <session_id> [step] [--restore-code]")
            sys.exit(1)
        restore_code = "--restore-code" in sys.argv
        args_clean = [a for a in sys.argv[2:] if a != "--restore-code"]
        sess = args_clean[0]
        step = int(args_clean[1]) if len(args_clean) > 1 and args_clean[1].isdigit() else None
        cmd_rollback(sess, step=step, restore_code=restore_code)
    elif action in ("budget", "track_budget"):
        import argparse
        b_parser = argparse.ArgumentParser(prog="state_machine.py budget")
        b_parser.add_argument("--report", action="store_true", help="View KPI summary report.")
        b_parser.add_argument("--tier", "-t", type=str, choices=["BUDGET", "STANDARD", "PREMIUM", "budget", "standard", "premium"], help="Declared model tier.")
        b_parser.add_argument("--task", type=str, default="adhoc_task", help="Name or description of task.")
        b_parser.add_argument("--model", type=str, default="auto", help="Model name used.")
        b_parser.add_argument("--harness", action="store_true", help="Was a test harness used.")
        b_parser.add_argument("--aborted", action="store_true", help="Was task aborted / escalated to premium.")
        b_args = b_parser.parse_args(sys.argv[2:])
        if b_args.tier:
            log_task_execution(
                task_name=b_args.task,
                tier=b_args.tier.upper(),
                model_used=b_args.model,
                was_harness_used=b_args.harness,
                aborted_to_premium=b_args.aborted
            )
        else:
            print_telemetry_report()
    elif action in ("amnesia", "evict", "rule_eviction"):
        apply_flag = "--apply" in sys.argv
        threshold_val = 30
        if "--threshold" in sys.argv:
            t_idx = sys.argv.index("--threshold")
            if t_idx + 1 < len(sys.argv) and sys.argv[t_idx + 1].isdigit():
                threshold_val = int(sys.argv[t_idx + 1])
        evict_assets(base_days_threshold=threshold_val, apply=apply_flag)
    elif action in ("state_graph", "graph_runner"):
        import argparse
        sg_parser = argparse.ArgumentParser(prog="state_machine.py state_graph", description="Pillar 1: Cyclic State Machine Engine")
        sg_parser.add_argument("--replay", type=str, help="Replay state from thread ID")
        sg_parser.add_argument("--step", type=int, help="Target checkpoint step")
        sg_args, _ = sg_parser.parse_known_args(sys.argv[2:])
        graph = StateGraph()
        try:
            if sg_args.replay:
                state = graph.load_checkpoint(sg_args.replay, step=sg_args.step)
                if state:
                    print(f"[STATE GRAPH CHECKPOINT: {sg_args.replay}]")
                    print(json.dumps(state, indent=2))
                else:
                    print(f"[STATE GRAPH] No checkpoint found for thread '{sg_args.replay}'.")
            else:
                print("StateGraph engine active. Use via API import or run test suite.")
        finally:
            graph.close()
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()
