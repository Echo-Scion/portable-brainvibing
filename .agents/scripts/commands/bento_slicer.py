#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bento_slicer.py — Universal Orion FSM, Audit-Ledger & Bento Task Dispenser
Unifies .orion/ task management across all 19 AI platforms and model tiers (BUDGET / STANDARD / PREMIUM).

Bridges monolithic Audit Reports and implementation_plan.md files directly into:
  1. .orion/working/execution_state.json & SQLite fsm_checkpoints (StateGraph)
  2. .orion/working/audit/00-ledger.md & .orion/working/audit/AUDIT_STATE.md
  3. .orion/working/context.json (Omni-Buffer active_bento_task injection)
  4. .orion/working/ACTIVE_TASK.md (Zero-search, bottom-up sorted single-task card with live disk lines)
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

try:
    from core.paths import get_workspace_dir, get_orion_dir, atomic_write_text
    from core.db import log_telemetry as _log_telemetry
    from core.dna import classify_file_to_tier
    from core.scanner import _resolve_local_1hop_closure
except ImportError:
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        pass

    def get_workspace_dir() -> Path:
        return Path(os.getcwd()).resolve()

    def get_orion_dir() -> Path:
        return get_workspace_dir() / ".orion"

    def atomic_write_text(filepath: Any, content: str) -> None:
        abs_p = os.path.abspath(str(filepath))
        os.makedirs(os.path.dirname(abs_p), exist_ok=True)
        tmp_p = f"{abs_p}.tmp.{os.getpid()}"
        with open(tmp_p, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_p, abs_p)

    def classify_file_to_tier(rel_path: str, symbols: Optional[List[str]] = None, epigenetic_aliases: Optional[Dict[str, str]] = None) -> Tuple[str, int, str, str]:
        return ("2_domain", 5, "DOMAIN_LOGIC", "Domain Logic")

    def _resolve_local_1hop_closure(file_paths: List[str], root_dir: str = ".") -> Set[str]:
        return set(file_paths)


QUEUE_FILE = "bento_queue.json"
ACTIVE_TASK_FILE = "ACTIVE_TASK.md"
FSM_STATE_FILE = "execution_state.json"
CONTEXT_FILE = "context.json"

PHASE_HEADER_RE = re.compile(
    r"^#{1,3}\s+(?:Phase\s+([0-9]+(?:\.[0-9]+)?)|PHASE\s+([0-9]+))\s*[:\-—]\s*(.+)$",
    re.MULTILINE | re.IGNORECASE,
)
TASK_HEADER_RE = re.compile(
    r"^#{2,4}\s+(?:Task\s+([0-9]+(?:\.[0-9]+)?)|\[?([A-Z0-9_-]+)\]?)\s*[:\-—]\s*(.+)$",
    re.MULTILINE,
)
TARGET_FILE_RE = re.compile(
    r"-\s*\*\*Target File\*\*\s*:\s*`?([^`\n]+?)`?(?:\s*$|\s*\()", re.IGNORECASE | re.MULTILINE
)
TARGET_SPAN_RE = re.compile(
    r"-\s*\*\*Target Span(?:\s*/\s*Symbol)?\*\*\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE
)
ROOT_CAUSE_RE = re.compile(
    r"-\s*\*\*Root Cause\*\*\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE
)
LINE_RANGE_EXTRACT_RE = re.compile(r"(?:Lines?|L)\s*(\d+)(?:\s*[-–—]\s*L?(\d+))?", re.IGNORECASE)
SEARCH_REPLACE_SPLIT_RE = re.compile(
    r"<<<<+\s*SEARCH[^\n]*\n(.*?)\n====+\s*REPLACE[^\n]*\n(.*?)(?:\n>>>>+|$)",
    re.DOTALL,
)


def extract_fenced_code_blocks(text: str) -> List[Tuple[str, str]]:
    """
    Fence-length-aware parser supporting 3+ backticks or tildes (` ``` `, ` ```` `, `~~~`)
    so outer 4-backtick Markdown blocks containing inner 3-backtick blocks never truncate early.
    """
    blocks: List[Tuple[str, str]] = []
    lines = text.splitlines()
    in_fence = False
    fence_char = ""
    fence_len = 0
    lang = ""
    buf: List[str] = []

    for line in lines:
        stripped = line.lstrip()
        if not in_fence:
            m = re.match(r"^(`{3,}|~{3,})([a-zA-Z0-9_+-]*)\s*$", stripped)
            if m:
                in_fence = True
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                lang = m.group(2).strip()
                buf = []
        else:
            m_close = re.match(rf"^({re.escape(fence_char)}{{{fence_len},}})\s*$", stripped)
            if m_close:
                blocks.append((lang, "\n".join(buf)))
                in_fence = False
                fence_char = ""
                fence_len = 0
                lang = ""
                buf = []
            else:
                buf.append(line)
    return blocks


def _extract_line_bounds(span_text: str, target_file: str) -> Tuple[int, int]:
    """Extracts 1-indexed (start_line, end_line) from TargetFile#Lxx-Lyy or Target Span text."""
    for source in (target_file, span_text):
        match = LINE_RANGE_EXTRACT_RE.search(source)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start + 25
            return max(1, start), max(start, end)
    return (1, 60)


def _clean_target_path(raw_path: str) -> str:
    """Strips #Lxx-Lyy anchors and surrounding quotes/backticks from file path."""
    cleaned = raw_path.strip().strip("`").strip("'").strip('"')
    if "#L" in cleaned:
        cleaned = cleaned.split("#L", 1)[0]
    return cleaned.replace("\\", "/")


def _find_task_headers_outside_fences(markdown_text: str) -> List[re.Match]:
    """Finds ### Task X.Y headers only when outside fenced code blocks."""
    matches: List[re.Match] = []
    lines = markdown_text.splitlines(keepends=True)
    in_fence = False
    fence_char = ""
    fence_len = 0
    offset = 0

    for line in lines:
        stripped = line.lstrip()
        if not in_fence:
            m_open = re.match(r"^(`{3,}|~{3,})[a-zA-Z0-9_+-]*\s*$", stripped)
            if m_open:
                in_fence = True
                fence_char = m_open.group(1)[0]
                fence_len = len(m_open.group(1))
            else:
                for hm in TASK_HEADER_RE.finditer(line):
                    m_full = TASK_HEADER_RE.search(markdown_text, offset, offset + len(line))
                    if m_full:
                        matches.append(m_full)
        else:
            if re.match(rf"^({re.escape(fence_char)}{{{fence_len},}})\s*$", stripped):
                in_fence = False
                fence_char = ""
                fence_len = 0
        offset += len(line)
    return matches


def _find_phase_headers_outside_fences(markdown_text: str) -> List[Tuple[int, str, str]]:
    """Finds Phase X headers outside fenced code blocks, returning (offset, phase_id, phase_title)."""
    matches: List[Tuple[int, str, str]] = []
    lines = markdown_text.splitlines(keepends=True)
    in_fence = False
    fence_char = ""
    fence_len = 0
    offset = 0

    for line in lines:
        stripped = line.lstrip()
        if not in_fence:
            m_open = re.match(r"^(`{3,}|~{3,})[a-zA-Z0-9_+-]*\s*$", stripped)
            if m_open:
                in_fence = True
                fence_char = m_open.group(1)[0]
                fence_len = len(m_open.group(1))
            else:
                pm = PHASE_HEADER_RE.search(line)
                if pm:
                    p_id = pm.group(1) or pm.group(2) or "1"
                    p_title = pm.group(3).strip()
                    matches.append((offset + pm.start(), p_id, p_title))
        else:
            if re.match(rf"^({re.escape(fence_char)}{{{fence_len},}})\s*$", stripped):
                in_fence = False
                fence_char = ""
                fence_len = 0
        offset += len(line)
    return matches


def textwrap_dedent_preserve(text: str) -> str:
    """Dedent common 2-space markdown list indentation if all non-empty lines share it."""
    lines = text.rstrip().splitlines()
    if not lines:
        return ""
    non_empty = [ln for ln in lines if ln.strip()]
    if non_empty and all(ln.startswith("  ") for ln in non_empty):
        return "\n".join(ln[2:] if ln.startswith("  ") else ln for ln in lines)
    return "\n".join(lines)


def _partition_into_disjoint_tracks(
    tasks: List[Dict[str, Any]],
    workspace_root: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Computes Connected Components across task files using 1-hop dependency closures.
    If tasks are tightly coupled (Jaccard overlap > 0.05 or shared imports):
      labeled as execution_topology="SEQUENTIAL_CHAIN", track_id="CHAIN".
    If tasks form disjoint clusters with zero/near-zero overlap (J <= 0.05):
      labeled as execution_topology="PARALLEL_DISJOINT", track_id="TRACK-A", "TRACK-B", etc.
    """
    if not tasks:
        return tasks

    ws_str = str(workspace_root) if workspace_root else "."
    unique_files = list(dict.fromkeys(t["target_file"] for t in tasks if t.get("target_file")))
    if len(unique_files) <= 1:
        for t in tasks:
            t["execution_topology"] = "SEQUENTIAL_CHAIN"
            t["track_id"] = "CHAIN"
        return tasks

    # Resolve closures
    closures: Dict[str, Set[str]] = {}
    for f in unique_files:
        closures[f] = _resolve_local_1hop_closure([f], root_dir=ws_str)

    # Build adjacency list: edge if closures intersect with Jaccard > 0.05
    adj: Dict[str, Set[str]] = {f: set() for f in unique_files}
    for i, f1 in enumerate(unique_files):
        c1 = closures[f1]
        for j in range(i + 1, len(unique_files)):
            f2 = unique_files[j]
            c2 = closures[f2]
            intersection = c1.intersection(c2)
            union = c1.union(c2)
            jaccard = len(intersection) / len(union) if union else 0.0
            if jaccard > 0.05:
                adj[f1].add(f2)
                adj[f2].add(f1)

    # Connected components via BFS
    visited: Set[str] = set()
    components: List[List[str]] = []
    for f in unique_files:
        if f not in visited:
            comp: List[str] = []
            queue = [f]
            visited.add(f)
            while queue:
                curr = queue.pop(0)
                comp.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            components.append(comp)

    # If only 1 component, all are coupled
    if len(components) <= 1:
        for t in tasks:
            t["execution_topology"] = "SEQUENTIAL_CHAIN"
            t["track_id"] = "CHAIN"
    else:
        # Multiple disjoint components -> sort by minimum gravity so central components get TRACK-A
        components.sort(key=lambda comp: min(classify_file_to_tier(f)[1] for f in comp))
        track_labels = [f"TRACK-{chr(65 + k)}" for k in range(len(components))]
        file_to_track: Dict[str, str] = {}
        for k, comp in enumerate(components):
            t_label = track_labels[k] if k < len(track_labels) else f"TRACK-{k+1}"
            for f in comp:
                file_to_track[f] = t_label

        for t in tasks:
            t["execution_topology"] = "PARALLEL_DISJOINT"
            t["track_id"] = file_to_track.get(t["target_file"], "CHAIN")

    return tasks


def parse_action_cards(markdown_text: str, workspace_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Parses an Audit Report or implementation_plan.md into discrete, topological & blast-radius
    sorted task dicts, respecting Phase boundaries and Bottom-Up line editing within each file.
    Supports both separate Verbatim Search / Replacement code blocks and <<<< SEARCH / ==== REPLACE blocks.
    """
    phase_headers = _find_phase_headers_outside_fences(markdown_text)
    task_matches = _find_task_headers_outside_fences(markdown_text)
    raw_tasks: List[Dict[str, Any]] = []

    for idx, match in enumerate(task_matches):
        start_pos = match.start()
        end_pos = task_matches[idx + 1].start() if idx + 1 < len(task_matches) else len(markdown_text)
        section_body = markdown_text[start_pos:end_pos].strip()

        task_id = match.group(1) or match.group(2) or f"T-{idx + 1:02d}"
        title = match.group(3).strip()

        # Determine enclosing Phase
        assigned_phase_id = "1"
        assigned_phase_title = "Core Execution"
        for ph_off, ph_id, ph_title in phase_headers:
            if ph_off <= start_pos:
                assigned_phase_id = ph_id
                assigned_phase_title = ph_title
            else:
                break
        if not phase_headers:
            m_pid = re.match(r"^([0-9]+)\.", str(task_id))
            if m_pid:
                assigned_phase_id = m_pid.group(1)
                assigned_phase_title = f"Phase {assigned_phase_id}"

        file_match = TARGET_FILE_RE.search(section_body)
        raw_file = file_match.group(1).strip() if file_match else ""
        target_file = _clean_target_path(raw_file)

        span_match = TARGET_SPAN_RE.search(section_body)
        span_text = span_match.group(1).strip() if span_match else raw_file

        rc_match = ROOT_CAUSE_RE.search(section_body)
        root_cause = rc_match.group(1).strip() if rc_match else ""

        start_line, end_line = _extract_line_bounds(span_text, raw_file)

        code_blocks = extract_fenced_code_blocks(section_body)
        search_code = ""
        replacement_code = ""
        replacement_lang = "python"
        verification_cmd = "python .agents/scripts/orion.py verify --fast"

        verification_cmd = "python .agents/scripts/orion.py verify --fast"
        non_shell_blocks: List[Tuple[str, str]] = []
        for lang, code in code_blocks:
            lang_clean = lang.strip().lower()
            if lang_clean in ("bash", "sh", "pwsh", "powershell", "cmd") and "Verification Gate" in section_body:
                clean_cmds = [
                    ln.strip() for ln in code.splitlines()
                    if ln.strip() and not ln.strip().startswith("#")
                ]
                if clean_cmds and non_shell_blocks:
                    verification_cmd = "\n".join(clean_cmds)
                    continue
            non_shell_blocks.append((lang_clean or "text", textwrap_dedent_preserve(code)))

        pairs: List[Tuple[str, str, str]] = []
        if len(non_shell_blocks) >= 2 and len(non_shell_blocks) % 2 == 0:
            for b_idx in range(0, len(non_shell_blocks), 2):
                pairs.append((non_shell_blocks[b_idx][0], non_shell_blocks[b_idx][1], non_shell_blocks[b_idx + 1][1]))
        elif len(non_shell_blocks) >= 2:
            pairs.append((non_shell_blocks[0][0], non_shell_blocks[0][1], non_shell_blocks[1][1]))
        elif len(non_shell_blocks) == 1:
            raw_code = non_shell_blocks[0][1]
            sr_match = SEARCH_REPLACE_SPLIT_RE.search(raw_code)
            if sr_match:
                pairs.append((non_shell_blocks[0][0], sr_match.group(1).rstrip(), sr_match.group(2).rstrip()))
            else:
                pairs.append((non_shell_blocks[0][0], "", raw_code))
        else:
            pairs.append(("python", "", ""))

        tier_key, gravity, slug, tier_title = classify_file_to_tier(target_file)

        for p_idx, (p_lang, p_search, p_repl) in enumerate(pairs):
            sub_id = f"{task_id}{chr(97 + p_idx)}" if len(pairs) > 1 else str(task_id)
            sub_title = f"{title} (Part {p_idx + 1})" if len(pairs) > 1 else title
            if target_file or p_repl:
                raw_tasks.append({
                    "task_id": sub_id,
                    "title": sub_title,
                    "target_file": target_file,
                    "span_text": span_text,
                    "root_cause": root_cause,
                    "start_line": start_line,
                    "end_line": end_line,
                    "replacement_lang": p_lang or "python",
                    "search_code": p_search,
                    "replacement_code": p_repl,
                    "verification_cmd": verification_cmd,
                    "phase_id": str(assigned_phase_id),
                    "phase_title": assigned_phase_title,
                    "dna_tier": tier_key,
                    "gravity": gravity,
                    "tier_slug": slug,
                    "status": "OPEN",
                })

    # Group tasks strictly by Phase to preserve Topological Phase Ordering (Phase 1 unlocks Phase 2)
    phase_order: List[str] = []
    tasks_by_phase: Dict[str, List[Dict[str, Any]]] = {}
    for t in raw_tasks:
        pid = t["phase_id"]
        if pid not in tasks_by_phase:
            phase_order.append(pid)
            tasks_by_phase[pid] = []
        tasks_by_phase[pid].append(t)

    sorted_tasks: List[Dict[str, Any]] = []

    for pid in phase_order:
        phase_tasks = tasks_by_phase[pid]
        # Partition into Disjoint Parallel Tracks within this Phase
        phase_tasks = _partition_into_disjoint_tracks(phase_tasks, workspace_root)

        # Group by target_file within this phase
        files_in_phase: List[str] = []
        grouped_by_file: Dict[str, List[Dict[str, Any]]] = {}
        file_gravities: Dict[str, int] = {}

        for t in phase_tasks:
            tf = t["target_file"]
            if tf not in grouped_by_file:
                files_in_phase.append(tf)
                grouped_by_file[tf] = []
                file_gravities[tf] = t.get("gravity", 5)
            grouped_by_file[tf].append(t)

        # 1. Sort edits on the SAME file Bottom-Up (start_line descending)
        for tf in files_in_phase:
            if len(grouped_by_file[tf]) > 1:
                grouped_by_file[tf].sort(key=lambda item: item["start_line"], reverse=True)

        # 2. Sort files in this phase Topologically:
        # Lower Gravity (Hub/Contracts first) -> Track ID -> File path
        files_in_phase.sort(key=lambda tf: (
            file_gravities.get(tf, 5),
            grouped_by_file[tf][0].get("track_id", "CHAIN"),
            tf
        ))

        for tf in files_in_phase:
            sorted_tasks.extend(grouped_by_file[tf])

    return sorted_tasks


def read_live_target_window(
    workspace_root: Path,
    rel_path: str,
    start_line: int,
    end_line: int,
    search_code: str = "",
    context_pad: int = 6,
) -> Tuple[str, str, int, int]:
    """
    Reads the exact current lines from disk and dynamically recalibrates (start_line, end_line)
    if search_code is found on disk, eliminating line-shift drift completely.
    Returns (numbered_window, raw_unnumbered_window, actual_start_line, actual_end_line).
    """
    if not rel_path:
        msg = "# [Target file not specified in card]"
        return msg, msg, start_line, end_line
    full_path = workspace_root / rel_path
    if not full_path.is_file():
        msg = f"# [File does not exist on disk yet: {rel_path} — create file]"
        return msg, msg, start_line, end_line

    try:
        content = full_path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        total = len(lines)

        # Dynamic Live Anchor Recalibration: locate search_code on disk if present
        clean_search = search_code.strip()
        if clean_search and not clean_search.startswith("# [File does not exist"):
            search_lines = clean_search.splitlines()
            first_anchor = search_lines[0].strip()
            if first_anchor and len(search_lines) >= 1:
                for idx in range(total - len(search_lines) + 1):
                    if lines[idx].strip() == first_anchor:
                        if all(lines[idx + j].rstrip() == search_lines[j].rstrip() for j in range(len(search_lines))):
                            start_line = idx + 1
                            end_line = idx + len(search_lines)
                            break

        s_idx = max(0, start_line - 1 - context_pad)
        e_idx = min(total, end_line + context_pad)
        numbered = [
            f"{line_no:4d} | {lines[line_no - 1]}"
            for line_no in range(s_idx + 1, e_idx + 1)
        ]
        raw_slice = lines[max(0, start_line - 1):min(total, end_line)]
        return "\n".join(numbered), "\n".join(raw_slice), start_line, end_line
    except Exception as e:
        msg = f"# [Error reading {rel_path}: {e}]"
        return msg, msg, start_line, end_line


def sync_orion_infrastructure(
    workspace_root: Path,
    source_file: str,
    tasks: List[Dict[str, Any]],
    current_index: int,
) -> None:
    """
    Unifies all 4 .orion/ task management surfaces automatically:
      1. .orion/working/execution_state.json + SQLite fsm_checkpoints (via StateGraph)
      2. .orion/working/audit/00-ledger.md & AUDIT_STATE.md
      3. .orion/working/context.json (Omni-Buffer active_bento_task field)
      4. .orion/task.md (Lifecycle checklist)
    """
    orion_dir = get_orion_dir()
    working_dir = orion_dir / "working"
    audit_dir = working_dir / "audit"
    working_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    active_task = tasks[current_index] if current_index < len(tasks) else None
    phase = "EXECUTING" if active_task else "DONE"

    active_tasks_map = {}
    if active_task:
        active_tasks_map[active_task["task_id"]] = {
            "title": active_task["title"],
            "phase": f"Phase {active_task.get('phase_id', '1')} — {active_task.get('phase_title', 'Core Execution')}",
            "topology": active_task.get("execution_topology", "SEQUENTIAL_CHAIN"),
            "track": active_task.get("track_id", "CHAIN"),
            "dna_tier": active_task.get("dna_tier", "2_domain"),
            "target_file": active_task["target_file"],
            "lines": f"L{active_task['start_line']}-L{active_task['end_line']}",
            "status": "RUNNING",
            "updated_at": datetime.now().isoformat(),
        }
    completed_list = [
        {
            "task_id": t["task_id"],
            "title": t["title"],
            "phase_id": t.get("phase_id", "1"),
            "track_id": t.get("track_id", "CHAIN"),
            "target_file": t["target_file"],
            "status": "COMPLETED",
        }
        for t in tasks[:current_index]
    ]
    fsm_state = {
        "session_id": "bento_plan_session",
        "phase": phase,
        "source_plan": source_file,
        "progress": f"{min(current_index, len(tasks))}/{len(tasks)}",
        "active_tasks": active_tasks_map,
        "completed_tasks": completed_list,
        "last_updated": datetime.now().isoformat(),
    }
    atomic_write_text(working_dir / FSM_STATE_FILE, json.dumps(fsm_state, indent=2))

    try:
        from commands.state_machine import StateGraph
        with StateGraph(db_path=str(orion_dir / "orion.db")) as graph:
            graph._save_checkpoint(
                "bento_plan_session",
                current_index,
                phase,
                fsm_state,
            )
    except Exception as e:
        _log_telemetry(e, "bento_slicer:sync_state_graph")

    # 2. Sync .orion/working/audit/00-ledger.md & AUDIT_STATE.md (for /strict-tdd Fused Mode)
    ledger_lines = [
        "# 00-LEDGER (Auto-Synced by Orion Task Dispenser)",
        f"> **Source**: `{source_file}`",
        "",
        "## Remediation Queue [01]",
    ]
    for idx, t in enumerate(tasks):
        status_tag = "[FIXED]" if idx < current_index else ("[IMPLEMENTATION]" if idx == current_index else "[OPEN]")
        ledger_lines.append(
            f"- {t['task_id']} {status_tag}: `{t['target_file']}#L{t['start_line']}-L{t['end_line']}` — {t['title']}"
        )
    atomic_write_text(audit_dir / "00-ledger.md", "\n".join(ledger_lines) + "\n")

    if active_task:
        audit_state_md = (
            "# AUDIT STATE\n\n"
            f"**Current Phase:** Remediation Execution ({current_index + 1} of {len(tasks)})\n"
            f"**Current Focus:** `{active_task['target_file']}` (Lines {active_task['start_line']}–{active_task['end_line']})\n"
            f"**Active Finding ID:** `{active_task['task_id']}` — {active_task['title']}\n"
            f"**Next Action:** Read `.orion/working/{ACTIVE_TASK_FILE}`, apply the surgical replacement to `{active_task['target_file']}`, and run `{active_task['verification_cmd']}`.\n"
        )
    else:
        audit_state_md = (
            "# AUDIT STATE\n\n"
            f"**Current Phase:** DONE ({len(tasks)}/{len(tasks)} tasks verified)\n"
            "**Current Focus:** None\n"
            "**Next Action:** All remediation tasks are [FIXED]. Run `python .agents/scripts/orion.py verify`.\n"
        )
    atomic_write_text(audit_dir / "AUDIT_STATE.md", audit_state_md)

    # 3. Sync .orion/task.md (Lifecycle checklist)
    task_md_lines = [
        "# Active Execution Checklist (.orion/task.md)",
        f"> **Progress**: {min(current_index, len(tasks))}/{len(tasks)} completed",
        "",
    ]
    for idx, t in enumerate(tasks):
        box = "[x]" if idx < current_index else ("[/]" if idx == current_index else "[ ]")
        task_md_lines.append(
            f"- {box} **Task {t['task_id']}**: `{t['target_file']}` (L{t['start_line']}-L{t['end_line']}) — {t['title']}"
        )
    atomic_write_text(orion_dir / "task.md", "\n".join(task_md_lines) + "\n")

    # 4. Inject active_bento_task into .orion/working/context.json (Omni-Buffer)
    ctx_path = working_dir / CONTEXT_FILE
    ctx_data: Dict[str, Any] = {}
    if ctx_path.is_file():
        try:
            ctx_data = json.loads(ctx_path.read_text(encoding="utf-8"))
        except Exception:
            ctx_data = {}
    ctx_data["timestamp_ms"] = int(time.time() * 1000)
    if active_task:
        ctx_data["active_file"] = active_task["target_file"]
        ctx_data["active_bento_task"] = {
            "index": f"{current_index + 1}/{len(tasks)}",
            "task_id": active_task["task_id"],
            "phase": f"Phase {active_task.get('phase_id', '1')} — {active_task.get('phase_title', 'Core Execution')}",
            "topology": active_task.get("execution_topology", "SEQUENTIAL_CHAIN"),
            "track": active_task.get("track_id", "CHAIN"),
            "dna_tier": active_task.get("dna_tier", "2_domain"),
            "title": active_task["title"],
            "target_file": active_task["target_file"],
            "lines": f"L{active_task['start_line']}-L{active_task['end_line']}",
            "instruction": f"Read .orion/working/{ACTIVE_TASK_FILE} and execute ONLY Task {active_task['task_id']}.",
        }
    else:
        ctx_data["active_bento_task"] = None
    atomic_write_text(ctx_path, json.dumps(ctx_data, indent=2))


def _align_replacement_indentation(raw_window: str, search_code: str, replacement_code: str) -> str:
    """
    Adjusts the leading indentation of replacement_code by the exact delta between
    raw_window (on-disk) and search_code (from markdown).
    Guarantees 100% exact whitespace alignment for model tool calls.
    """
    if not raw_window or not search_code or not replacement_code:
        return replacement_code

    raw_lines = [ln for ln in raw_window.splitlines() if ln.strip()]
    search_lines = [ln for ln in search_code.splitlines() if ln.strip()]
    repl_lines = replacement_code.splitlines()

    if not raw_lines or not search_lines or not repl_lines:
        return replacement_code

    disk_indent = len(raw_lines[0]) - len(raw_lines[0].lstrip())
    md_indent = len(search_lines[0]) - len(search_lines[0].lstrip())
    delta = disk_indent - md_indent

    if delta == 0:
        return replacement_code
    elif delta > 0:
        pad = " " * delta
        return "\n".join(pad + ln if ln.strip() else ln for ln in repl_lines)
    else:
        abs_delta = abs(delta)
        adjusted = []
        for ln in repl_lines:
            leading = len(ln) - len(ln.lstrip())
            cut = min(leading, abs_delta)
            adjusted.append(ln[cut:])
        return "\n".join(adjusted)


def render_active_bento_markdown(
    task: Dict[str, Any],
    queue_index: int,
    total_tasks: int,
    workspace_root: Path,
) -> str:
    """
    Builds the universal, low-token ACTIVE_TASK.md card for BUDGET & STANDARD models
    across all 19 platforms.
    """
    numbered_window, raw_window, actual_start, actual_end = read_live_target_window(
        workspace_root,
        task["target_file"],
        task["start_line"],
        task["end_line"],
        search_code=task.get("search_code", ""),
    )
    task["start_line"] = actual_start
    task["end_line"] = actual_end
    search_anchor = raw_window if (raw_window and not raw_window.startswith("# [")) else (task.get("search_code") or raw_window)
    repl_code = _align_replacement_indentation(raw_window, task.get("search_code", ""), task.get("replacement_code", ""))
    root_cause_line = f"\n- **Root Cause**: {task['root_cause']}" if task.get("root_cause") else ""
    phase_meta = f"- **Phase**: Phase {task.get('phase_id', '1')} — **{task.get('phase_title', 'Core Execution')}**\n"
    dna_meta = f"- **DNA Stratum**: `{task.get('tier_slug', 'DOMAIN_CORE')}` (Gravity `{task.get('gravity', 5)}`)\n"
    topology_meta = f"- **Execution Topology**: `{task.get('execution_topology', 'SEQUENTIAL_CHAIN')}` [`{task.get('track_id', 'CHAIN')}`]\n"

    return f"""# 🎯 ACTIVE ORION BENTO TASK ({queue_index + 1} of {total_tasks})
> **UNIVERSAL BENTO-BOX MANDATE (`BUDGET` & `STANDARD` TIERS — ALL PLATFORMS)**:
> Execute **ONLY** this single task in this turn.
> - **DO NOT** read the full audit report or full `implementation_plan.md`.
> - **DO NOT** batch-edit other files or proceed to Task {queue_index + 2} until the Verification Gate below exits with `0`.

## 1. Target Coordinates
- **Task ID**: `{task['task_id']}` — **{task['title']}**
{phase_meta}{dna_meta}{topology_meta}- **Target File**: `{task['target_file']}`
- **Target Span**: `{task['span_text']}` (Live Lines `{actual_start}`–`{actual_end}`){root_cause_line}

## 2. Live Code Window Currently on Disk (`{task['target_file']}`)
*(Pre-extracted from disk with 1-indexed line numbers — zero `view_file` paging required)*:
````text
{numbered_window}
````

## 3. Verbatim SEARCH Block (Target Content to Replace)
````{task['replacement_lang']}
{search_anchor}
````

## 4. Exact Drop-In REPLACE Block (New Content)
````{task['replacement_lang']}
{repl_code}
````

## 5. Mandatory Verification & Queue Advance Gate
After applying the edit to `{task['target_file']}`, run this single command to verify (`Exit Code 0` required) and automatically dispense the next task:
```bash
python .agents/scripts/orion.py bento next --verify
```
"""


def check_finding_coverage(content: str, tasks: List[Dict[str, Any]]) -> List[str]:
    """Detects orphaned finding IDs from audit reports that lack corresponding Task cards."""
    finding_pattern = re.compile(r'\b(TTP-[A-Z0-9_-]+|FINDING-[A-Z0-9_-]+)\b')
    all_findings = set(finding_pattern.findall(content))
    if not all_findings:
        return []

    covered_findings = set()
    for t in tasks:
        task_str = f"{t.get('task_id', '')} {t.get('title', '')} {t.get('root_cause', '')} {t.get('span_text', '')}"
        for f_id in finding_pattern.findall(task_str):
            covered_findings.add(f_id)

    orphaned = sorted(all_findings - covered_findings)
    return orphaned


def cmd_init(plan_path: str) -> int:
    ws = get_workspace_dir()
    orion_working = get_orion_dir() / "working"
    orion_working.mkdir(parents=True, exist_ok=True)

    src = Path(plan_path).resolve()
    if not src.is_file():
        print(f"[ORION BENTO ERROR] Plan/Audit file not found: {plan_path}", file=sys.stderr)
        return 1

    content = src.read_text(encoding="utf-8", errors="replace")
    tasks = parse_action_cards(content, workspace_root=ws)
    if not tasks:
        print(f"[ORION BENTO ERROR] No structured Task cards found in {plan_path}.", file=sys.stderr)
        return 1

    orphaned = check_finding_coverage(content, tasks)
    if orphaned:
        print(f"⚠️  [BENTO COVERAGE WARNING] Found {len(orphaned)} audit finding(s) without dedicated Action Cards:")
        for o_id in orphaned:
            print(f"   - {o_id}")

    active_md = render_active_bento_markdown(tasks[0], 0, len(tasks), ws)
    active_path = orion_working / ACTIVE_TASK_FILE
    atomic_write_text(active_path, active_md)

    try:
        rel_src = src.relative_to(ws).as_posix()
    except ValueError:
        rel_src = src.name

    queue_data = {
        "source_file": rel_src,
        "current_index": 0,
        "tasks": tasks,
    }
    queue_path = orion_working / QUEUE_FILE
    atomic_write_text(queue_path, json.dumps(queue_data, indent=2))

    sync_orion_infrastructure(ws, queue_data["source_file"], tasks, 0)

    distinct_phases = list(dict.fromkeys(t.get("phase_id", "1") for t in tasks))
    distinct_tracks = list(dict.fromkeys(t.get("track_id", "CHAIN") for t in tasks if t.get("track_id") != "CHAIN"))
    print(f"[ORION BENTO INITIALIZED] Extracted {len(tasks)} atomic tasks across {len(distinct_phases)} topological phase(s).")
    if distinct_tracks:
        print(f"  ⚡ Disjoint Parallel Tracks: {len(distinct_tracks)} ({', '.join(distinct_tracks)}) — Multi-Agent Ready")
    else:
        print("  ⚡ Execution Flow: Sequential Chain (Coupled / Hub-First)")
    print("  ✓ Synced .orion/working/execution_state.json & SQLite fsm_checkpoints")
    print("  ✓ Synced .orion/working/audit/00-ledger.md & AUDIT_STATE.md")
    print("  ✓ Synced .orion/working/context.json & .orion/task.md")
    print(f"  ✓ Dispensed Task 1/{len(tasks)} -> .orion/working/{ACTIVE_TASK_FILE}")
    print("\n👉 Universal Prompt for ANY IDE / Model (BUDGET or STANDARD):")
    print('   "Read .orion/working/ACTIVE_TASK.md, apply the exact replacement, and run `python .agents/scripts/orion.py bento next --verify`."')
    return 0


def verify_patch_applied_on_disk(task: Dict[str, Any], workspace_root: Path) -> Tuple[bool, str]:
    """
    Zero-Escape Gate: Mechanically checks whether the target file actually underwent
    mutation before allowing 'bento next --verify' to run tests.
    Prevents Budget/Standard models from advancing empty (no-op) tasks when existing tests already pass.
    """
    rel_path = task.get("target_file", "").strip()
    if not rel_path:
        return True, ""
    full_path = workspace_root / rel_path
    if not full_path.is_file():
        return False, f"Target file does not exist on disk: {rel_path}"

    search_code = task.get("search_code", "").strip()
    repl_code = task.get("replacement_code", "").strip()

    if search_code.startswith("# [File does not exist"):
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            if content.strip():
                return True, ""
            return False, f"Target file was not created or is empty: {rel_path}"
        except Exception as e:
            return False, f"Error reading target file {rel_path}: {e}"

    if not search_code or not repl_code:
        return True, ""

    try:
        content = full_path.read_text(encoding="utf-8", errors="replace")
        disk_lines = [ln.strip() for ln in content.splitlines()]
        search_lines = [ln.strip() for ln in search_code.splitlines() if ln.strip()]
        repl_lines = [ln.strip() for ln in repl_code.splitlines() if ln.strip()]

        if repl_lines:
            first_repl = repl_lines[0]
            for idx in range(len(disk_lines) - len(repl_lines) + 1):
                if disk_lines[idx] == first_repl:
                    if all(disk_lines[idx + j] == repl_lines[j] for j in range(len(repl_lines))):
                        return True, ""

        if search_lines:
            first_search = search_lines[0]
            found_search = False
            for idx in range(len(disk_lines) - len(search_lines) + 1):
                if disk_lines[idx] == first_search:
                    if all(disk_lines[idx + j] == search_lines[j] for j in range(len(search_lines))):
                        found_search = True
                        break
            if found_search:
                return False, (
                    f"Target file '{rel_path}' still contains the exact unpatched SEARCH block!\n"
                    f"The replacement patch was not applied. Apply the edit before advancing."
                )

        return True, ""
    except Exception as e:
        return False, f"Failed to verify disk mutation on {rel_path}: {e}"


def _run_verification_command(v_cmd: str, cwd: Path) -> Tuple[int, str, str]:
    """Safely executes verification commands sequentially across Windows and POSIX without shell injection."""
    raw_cmds = [ln.strip() for ln in v_cmd.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not raw_cmds:
        raw_cmds = ["python .agents/scripts/orion.py verify --fast"]

    expanded_cmds: List[str] = []
    for c in raw_cmds:
        for sub in c.split("&&"):
            sub_clean = sub.strip()
            if sub_clean:
                expanded_cmds.append(sub_clean)

    combined_stdout: List[str] = []
    combined_stderr: List[str] = []

    for cmd_str in expanded_cmds:
        raw_parts = shlex.split(cmd_str, posix=(os.name != "nt"))
        cmd_parts = [p.strip('"').strip("'") if os.name == "nt" else p for p in raw_parts]
        proc = subprocess.run(
            cmd_parts,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
        )
        if proc.stdout:
            combined_stdout.append(proc.stdout.strip())
        if proc.stderr:
            combined_stderr.append(proc.stderr.strip())
        if proc.returncode != 0:
            return proc.returncode, "\n".join(combined_stdout), "\n".join(combined_stderr)

    return 0, "\n".join(combined_stdout), "\n".join(combined_stderr)


def cmd_next(run_verify: bool = False) -> int:
    ws = get_workspace_dir()
    orion_working = get_orion_dir() / "working"
    queue_path = orion_working / QUEUE_FILE
    active_path = orion_working / ACTIVE_TASK_FILE

    if not queue_path.is_file():
        print("[ORION BENTO ERROR] No active queue found. Run `init <plan.md>` first.", file=sys.stderr)
        return 1

    queue_data = json.loads(queue_path.read_text(encoding="utf-8"))
    tasks = queue_data.get("tasks", [])
    idx = int(queue_data.get("current_index", 0))

    if idx >= len(tasks):
        print("🏁 [ORION BENTO] All tasks in the queue are already completed.")
        return 0

    current_task = tasks[idx]

    if run_verify:
        applied_ok, err_msg = verify_patch_applied_on_disk(current_task, ws)
        if not applied_ok:
            print(
                f"\n❌ [BENTO NO-OP REJECTED] Mutation verification failed (Exit Code 2).\n"
                f"{err_msg}\n"
                f"Task {current_task['task_id']} remains OPEN. You MUST apply the patch to disk.",
                file=sys.stderr,
            )
            return 2

        v_cmd = current_task.get("verification_cmd", "python .agents/scripts/orion.py verify --fast")
        print(f"[ORION BENTO GATE] Running verification for Task {current_task['task_id']}: {v_cmd}")
        retcode, stdout, stderr = _run_verification_command(v_cmd, ws)
        if stdout:
            print(stdout.strip())
        if retcode != 0:
            if stderr:
                print(stderr.strip(), file=sys.stderr)
            print(
                f"\n❌ [BENTO HARD PAUSE] Verification failed (Exit Code {retcode}). "
                f"Task {current_task['task_id']} remains OPEN. Fix before advancing.",
                file=sys.stderr,
            )
            return retcode

    tasks[idx]["status"] = "DONE"
    next_idx = idx + 1
    queue_data["current_index"] = next_idx

    if next_idx < len(tasks):
        next_task = tasks[next_idx]
        active_md = render_active_bento_markdown(next_task, next_idx, len(tasks), ws)
        atomic_write_text(active_path, active_md)
        atomic_write_text(queue_path, json.dumps(queue_data, indent=2))
        sync_orion_infrastructure(ws, queue_data.get("source_file", ""), tasks, next_idx)
        print(
            f"✅ [ORION BENTO ADVANCED] Task {current_task['task_id']} -> [FIXED]. "
            f"Now active: Task {next_idx + 1}/{len(tasks)} ({next_task['task_id']}: {next_task['title']}) "
            f"in .orion/working/{ACTIVE_TASK_FILE}"
        )
        return 0

    atomic_write_text(queue_path, json.dumps(queue_data, indent=2))
    sync_orion_infrastructure(ws, queue_data.get("source_file", ""), tasks, next_idx)
    done_md = (
        "# 🏁 ALL ORION BENTO TASKS COMPLETED\n\n"
        f"All {len(tasks)} atomic tasks from `{queue_data.get('source_file')}` have been applied and verified (`Exit Code 0`).\n"
        "- `.orion/working/execution_state.json`: `DONE`\n"
        "- `.orion/working/audit/00-ledger.md`: All items marked `[FIXED]`\n"
    )
    atomic_write_text(active_path, done_md)
    print(f"🏁 [ORION BENTO COMPLETE] All {len(tasks)}/{len(tasks)} tasks verified and marked [FIXED] in 00-ledger.md!")
    return 0


def cmd_status() -> int:
    orion_working = get_orion_dir() / "working"
    queue_path = orion_working / QUEUE_FILE
    if not queue_path.is_file():
        print("[ORION BENTO] No active queue.")
        return 0

    queue_data = json.loads(queue_path.read_text(encoding="utf-8"))
    tasks = queue_data.get("tasks", [])
    idx = int(queue_data.get("current_index", 0))
    print(f"Source Plan : {queue_data.get('source_file')}")
    print(f"Progress    : {min(idx, len(tasks))}/{len(tasks)} completed\n")
    for i, t in enumerate(tasks):
        marker = "👉" if i == idx else ("✅" if i < idx else "⏳")
        track_tag = f"[{t.get('track_id', 'CHAIN')}]" if t.get('track_id') else ""
        phase_tag = f"[P{t.get('phase_id', '1')}]"
        print(
            f"  {marker} [{i + 1:02d}] {phase_tag} {track_tag} Task {t['task_id']}: {t['target_file']} "
            f"(L{t['start_line']}-L{t['end_line']}) — {t['title']} [{t['status']}]"
        )
    tracks = set(t.get('track_id') for t in tasks if t.get('track_id') and t.get('track_id') != 'CHAIN')
    if len(tracks) > 1:
        print(f"\n💡 Multi-Agent Opportunity: {len(tracks)} Disjoint Tracks detected ({', '.join(sorted(tracks))}). Can be executed concurrently via subagents.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    args_list = list(argv if argv is not None else sys.argv[1:])
    if args_list and args_list[0].lower() in ("bento", "bento_slicer"):
        args_list.pop(0)

    parser = argparse.ArgumentParser(
        description="Universal Orion FSM, Audit-Ledger & Bento Task Dispenser"
    )
    sub = parser.add_subparsers(dest="subcommand")

    p_init = sub.add_parser("init", help="Slice an Audit Report or implementation_plan.md into .orion/ queues")
    p_init.add_argument("plan_path", help="Path to Audit Report or implementation_plan.md")

    p_slice = sub.add_parser("slice", help="Alias for init: slice plan/audit into .orion/ queues")
    p_slice.add_argument("plan_path", help="Path to Audit Report or implementation_plan.md")

    p_next = sub.add_parser("next", help="Verify current task and dispense the next task into ACTIVE_TASK.md")
    p_next.add_argument("--verify", action="store_true", help="Run current task verification gate before advancing")

    p_done = sub.add_parser("done", help="Mark current active task as DONE and dispense the next task")
    p_done.add_argument("--verify", action="store_true", help="Run current task verification gate before advancing")

    sub.add_parser("status", help="Show current Bento & Orion FSM queue progress")

    args = parser.parse_args(args_list)
    if args.subcommand in ("init", "slice"):
        return cmd_init(args.plan_path)
    elif args.subcommand in ("next", "done"):
        return cmd_next(run_verify=args.verify)
    elif args.subcommand == "status":
        return cmd_status()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
