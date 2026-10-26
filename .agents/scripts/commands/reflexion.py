#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Native VerbalReflectiveLearner, Self-Evolution, Temporal Pulse & Linkify Engine.
Pure Python 3 standard library implementation.
Absorbs:
- core/reflexion.py (ReflexionEngine, PromptRuleCompiler, ReflexionLoop)
- commands/consolidate.py (Temporal Pulse & Episodic Consolidation)
- commands/linkify.py (Obsidian Interop Wikilink Injector)
"""
import os
import sys
import json
import re
import uuid
import glob
import shutil
import subprocess
import shlex
import bisect
import ast
import time
import hashlib
from datetime import datetime
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Union, Set

try:
    from core.db import log_telemetry as _log_telemetry, atomic_write_text
except ImportError:
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")
    def atomic_write_text(filepath: str, content: str) -> None:
        import uuid
        abs_path = os.path.abspath(str(filepath))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        temp_file = f"{abs_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(temp_file, abs_path)
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception as _e:
        _log_telemetry(_e, 'reflexion.py:reconfigure')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
BASE_DIR = os.path.abspath(os.path.join(SCRIPTS_DIR, '..'))
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

try:
    from core.db import connect_sqlite
except ImportError:
    import sqlite3
    connect_sqlite = sqlite3.connect

from core.paths import get_persistence_db_path
from core.capabilities import enqueue_cloud_handoff

LEARNINGS_FILE = os.path.join(BASE_DIR, 'LEARNINGS.md')
OBSERVATIONS_FILE = os.path.join(BASE_DIR, 'OBSERVATIONS.md')
OBSERVATIONS_ARCHIVE_FILE = os.path.join(BASE_DIR, 'OBSERVATIONS.archive.md')
MATRIX_DIR = os.path.join(WORKSPACE_DIR, '.orion', 'matrix')

EPISODIC_DIR = os.path.join(WORKSPACE_DIR, '.orion', 'episodic')
SESSION_DIR = os.path.join(EPISODIC_DIR, 'sessions')
MILESTONE_DIR = os.path.join(EPISODIC_DIR, 'milestones')
EPOCH_DIR = os.path.join(EPISODIC_DIR, 'epochs')

SESSION_ARCHIVE = os.path.join(SESSION_DIR, 'processed')
MILESTONE_ARCHIVE = os.path.join(MILESTONE_DIR, 'processed')

SESSION_HISTORY = os.path.join(EPISODIC_DIR, 'session_history.md')
HANDOFF_FILE = os.path.join(WORKSPACE_DIR, '.orion', 'working', 'handoff.md')


# ==============================================================================
# SECTION 1: VERBAL REFLECTIVE LEARNER & SELF-EVOLUTION ENGINE
# ==============================================================================

class ReflexionEngine:
    """
    Linguistic Self-Reflection & Persistent Learning (VerbalReflectiveLearner pattern).
    Captures post-error reflections and converts them into durable invariants in LEARNINGS.md.
    """
    def __init__(self, learnings_path: str = LEARNINGS_FILE):
        self.learnings_path = learnings_path

    def record_learning(
        self,
        title: str,
        root_cause: str = "",
        fix_applied: str = "",
        self_evolve_rule: str = "",
        trigger: str = "",
        evidence: str = "",
        intervention: str = "",
        guard: str = "",
        resting_tier: str = "TIER-0"
    ) -> bool:
        date_str = datetime.now().strftime("%Y-%m-%d")
        tier_upper = resting_tier.upper()
        if not tier_upper.startswith("TIER-"):
            tier_upper = f"TIER-{tier_upper}"

        lines = [
            "",
            "---",
            "",
            f"## {date_str} — {title.strip()} [Lowest Viable Tier: {tier_upper}]",
            ""
        ]

        if trigger:
            lines.append(f"- **Trigger**: {trigger.strip()}")
        if evidence:
            lines.append(f"- **Evidence**: {evidence.strip()}")
        if intervention:
            lines.append(f"- **Intervention (Action Recipe)**: {intervention.strip()}")
        if guard:
            lines.append(f"- **Do-Not-Trigger Guard**: {guard.strip()}")
        if root_cause:
            lines.append(f"- **Root Cause**: {root_cause.strip()}")
        if fix_applied:
            lines.append(f"- **Fix Applied**: {fix_applied.strip()}")
        if self_evolve_rule:
            lines.append(f"- **Self-Evolve Invariant**: {self_evolve_rule.strip()}")
        lines.append("")

        entry = "\n".join(lines)
        try:
            with open(self.learnings_path, 'a', encoding='utf-8') as f:
                f.write(entry)
            # Darwinian Circuit Breaker Reset: automatically clear lockout upon learning
            try:
                from core.harness.capture import ToolQuantumCapture
                session_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID") or os.environ.get("ANTIGRAVITY_SESSION_ID", "cli_session")
                harness_dir = os.path.join(WORKSPACE_DIR, ".orion", "harness")
                ToolQuantumCapture(state_dir=harness_dir).reset_circuit_breaker(session_id)
            except Exception as _cb_err:
                _log_telemetry(_cb_err, "reflexion.py:reset_circuit_breaker")
            return True
        except Exception as e:
            _log_telemetry(e, 'reflexion.py:record_learning')
            return False

    def list_learnings(self) -> List[Dict[str, str]]:
        if not os.path.exists(self.learnings_path):
            return []
        learnings = []
        try:
            with open(self.learnings_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            sections = re.split(r'\n---\n', content)
            for sec in sections:
                title_match = re.search(r'##\s*(\d{4}-\d{2}-\d{2})\s*—\s*([^\[\n]+)(?:\[Lowest Viable Tier:\s*([^\]]+)\])?', sec)
                if title_match:
                    date = title_match.group(1)
                    title = title_match.group(2).strip()
                    tier = title_match.group(3).strip() if title_match.group(3) else "TIER-0"

                    def _extract(field_name):
                        m = re.search(rf'\*\*{re.escape(field_name)}\*\*:\s*(.+?)(?=\n\s*-\s*\*\*|\n\n\*\*|$)', sec, re.DOTALL)
                        return m.group(1).strip() if m else ""

                    trigger = _extract("Trigger")
                    evidence = _extract("Evidence")
                    intervention = _extract("Intervention (Action Recipe)")
                    guard = _extract("Do-Not-Trigger Guard")
                    cause = _extract("Root Cause")
                    rule = _extract("Self-Evolve Invariant") or _extract("Self-Evolve Rule")
                    fix = _extract("Fix Applied")

                    learnings.append({
                        "date": date,
                        "title": title,
                        "tier": tier,
                        "trigger": trigger,
                        "evidence": evidence,
                        "intervention": intervention,
                        "guard": guard,
                        "root_cause": cause,
                        "fix_applied": fix,
                        "rule": rule
                    })
        except Exception as e:
            _log_telemetry(e, 'reflexion.py:list_learnings')
        return learnings

    def graduate_learning(self, title_query: str, skill_name: Optional[str] = None, intents_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Graduates a recurring failure learning from LEARNINGS.md into a Sovereign Harness skill intent.
        Converts the text bullet into a modular skill proposal (SKILL.md + references/remediation.md).
        """
        learnings = self.list_learnings()
        target = None
        for item in learnings:
            if title_query.lower() in item["title"].lower():
                target = item
                break

        if not target:
            return {"ok": False, "error": f"Learning with title containing '{title_query}' not found"}

        if not skill_name:
            clean = re.sub(r"[^a-z0-9]+", "-", target["title"].lower()).strip("-")
            clean_slug = clean[:25].rstrip("-")
            skill_name = f"rule-{clean_slug}" if not clean_slug.startswith("rule-") else clean_slug

        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", skill_name):
            skill_name = "rule-" + re.sub(r"[^a-z0-9]+", "-", skill_name).strip("-")

        rule_text = target.get("rule") or target.get("intervention") or target.get("root_cause") or "Execute remediation before commit."
        trigger_cue = target.get("trigger") or f"encountering {target['title']}"
        if not re.search(r"(?i)\bwhen\b|[\"'][^\"']+[\"']|`[^`]+`", trigger_cue):
            trigger_cue = f"Use when {trigger_cue}"

        body = (
            f"---\n"
            f"name: {skill_name}\n"
            f"description: {trigger_cue}\n"
            f"category: learning\n"
            f"---\n"
            f"# {target['title']}\n\n"
            f"## Invariant Rule\n"
            f"{rule_text}\n\n"
            f"See .agents/skills/{skill_name}/references/remediation.md for full root cause and evidence.\n"
        )

        remediation_content = (
            f"# Remediation Trace: {target['title']}\n\n"
            f"- **Date Recorded**: {target.get('date', '')}\n"
            f"- **Lowest Viable Tier**: {target.get('tier', 'TIER-0')}\n"
            f"- **Root Cause**: {target.get('root_cause', '')}\n"
            f"- **Fix Applied**: {target.get('fix_applied', '')}\n"
            f"- **Intervention**: {target.get('intervention', '')}\n"
            f"- **Guard**: {target.get('guard', '')}\n"
        )

        evidence_text = target.get("evidence") or target.get("root_cause") or "Observed recurring error trace in LEARNINGS.md"
        reason_text = f"Graduated recurring learning: {target['title']}"

        from core.harness.staging import IntentQueue, StagedIntent
        target_intents_dir = intents_dir or os.path.join(WORKSPACE_DIR, '.orion', 'harness', 'intents')
        queue = IntentQueue(target_intents_dir)

        intent_id = str(uuid.uuid4())[:8]
        intent = StagedIntent(
            id=intent_id,
            action="create",
            name=skill_name,
            reason=reason_text,
            evidence=evidence_text,
            level="project",
            body=body,
            files={"references/remediation.md": remediation_content}
        )

        target_path = queue.enqueue(intent)

        try:
            with open(self.learnings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if target['title'] in content and f"[Graduated to Skill: {skill_name}]" not in content:
                content = content.replace(
                    f"— {target['title']}",
                    f"— {target['title']} [Graduated to Skill: {skill_name}]"
                )
                atomic_write_text(self.learnings_path, content)
        except Exception as _e:
            _log_telemetry(_e, "reflexion.graduate_learning.mark")

        rel_path = os.path.relpath(target_path, WORKSPACE_DIR).replace(os.sep, '/')
        return {
            "ok": True,
            "intent_id": intent_id,
            "skill_name": skill_name,
            "staged_path": rel_path
        }

    def detect_and_graduate_recurring(self, intents_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        # 1. Drain recurring mechanical catches from Seam 1 (.orion/working/mechanical_catches.json) into LEARNINGS.md
        try:
            from core.db import drain_mechanical_catches
            catches = drain_mechanical_catches(clear=False)
            ctx_counts: Dict[str, List[Dict[str, Any]]] = {}
            for c in catches:
                ctx_key = f"{c.get('context', 'unknown')}::{c.get('exception_type', 'Error')}"
                ctx_counts.setdefault(ctx_key, []).append(c)
            for ctx_key, events in ctx_counts.items():
                if len(events) >= 2:
                    sample = events[-1]
                    self.record_learning(
                        title=f"Recurring Mechanical Catch in {sample.get('context', 'unknown')}",
                        root_cause=f"{sample.get('exception_type')}: {sample.get('error', '')[:200]}",
                        fix_applied="Captured via @sovereign_catch telemetry sink",
                        self_evolve_rule=f"Enforce boundary invariant guard on {sample.get('context')}",
                        trigger=f"When invoking {sample.get('context')}",
                        evidence=f"Observed {len(events)} mechanical catch events in mechanical_catches.json",
                        intervention=f"Validate input/output contract for {sample.get('context')}",
                        guard="Do not suppress genuine runtime exceptions",
                        resting_tier="TIER-0",
                    )
        except Exception as _ce:
            _log_telemetry(_ce, "reflexion.py:drain_catches_to_learnings")

        learnings = self.list_learnings()
        graduated = []
        seen_norms = set()
        for item in learnings:
            title = item.get("title", "")
            norm = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            if norm and norm not in seen_norms:
                seen_norms.add(norm)
                res = self.graduate_learning(title, intents_dir=intents_dir)
                if res.get("ok"):
                    graduated.append(res)
        return graduated


class ObservationLedger:
    """
    Observation Ledger & Signal Capture System (Phase 1).
    Manages raw observations in .agents/OBSERVATIONS.md and .agents/OBSERVATIONS.archive.md.
    """
    def __init__(self, active_path: str = None, archive_path: str = None, ledger_path: str = None):
        self.active_path = active_path or ledger_path or OBSERVATIONS_FILE
        self.archive_path = archive_path or OBSERVATIONS_ARCHIVE_FILE
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        if not os.path.exists(self.active_path):
            header = (
                "# Observation Ledger (Active & Parked Signals)\n\n"
                "> Raw signals: corrections, tool failures, mechanical catches, verify fails, rule violations.\n\n"
            )
            atomic_write_text(self.active_path, header)
        if not os.path.exists(self.archive_path):
            header = (
                "# Observation Ledger Archive (Resolved Signals)\n\n"
                "> Resolved, declined, or superseded observations.\n\n"
            )
            atomic_write_text(self.archive_path, header)

    def _parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        entries = []
        blocks = re.split(r"(?m)^(?=##\s+Observation\s+)", content)
        for block in blocks:
            if not block.strip().startswith("## Observation "):
                continue
            lines = block.strip().splitlines()
            title_line = lines[0]
            m_title = re.match(r"##\s+Observation\s+#?(\d+):\s*(.+)", title_line)
            if not m_title:
                continue
            obs_id = int(m_title.group(1))
            title = m_title.group(2).strip()

            entry = {
                "id": obs_id,
                "anchor_id": f"O{obs_id}",
                "title": title,
                "fingerprint": "",
                "status": "open",
                "kind": "improve",
                "target": "",
                "rule_id": "",
                "siblings_checked": "true",
                "scope": "project",
                "parked_until": "",
                "evidence": "",
                "created": "",
                "resolved": "",
                "resolution": "",
                "superseded_by": "",
                "count": 1,
                "seen_in": "",
                "applies_to": ""
            }

            for line in lines[1:]:
                m_kv = re.match(r"^\s*-\s*\*\*([a-zA-Z0-9_]+)\*\*\s*:\s*(.*)$", line)
                if m_kv:
                    k = m_kv.group(1).lower()
                    v = m_kv.group(2).strip()
                    if k == "id":
                        try:
                            entry["id"] = int(v)
                        except ValueError:
                            pass
                    elif k == "count":
                        try:
                            entry["count"] = int(v)
                        except ValueError:
                            entry["count"] = 1
                    elif k in entry:
                        entry[k] = v

            entries.append(entry)
        return entries

    def get_all_observations(self) -> List[Dict[str, Any]]:
        return self._parse_file(self.active_path)

    def get_archive_observations(self) -> List[Dict[str, Any]]:
        return self._parse_file(self.archive_path)

    def get_next_id(self) -> int:
        active = self.get_all_observations()
        arch = self.get_archive_observations()
        max_id = 0
        for item in active + arch:
            if item["id"] > max_id:
                max_id = item["id"]
        return max_id + 1

    def compute_fingerprint(self, kind: str, target_or_rule: str, title: str) -> str:
        raw = f"{kind.strip().lower()}:{target_or_rule.strip().lower()}:{title.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

    def add_observation(
        self,
        title: str,
        kind: str = "improve",
        target: str = "",
        rule_id: str = "",
        scope: str = "project",
        evidence: str = "",
        status: str = "open",
        parked_until: str = "",
        siblings_checked: str = "true",
        count: int = 1,
        seen_in: str = "",
        applies_to: str = ""
    ) -> Dict[str, Any]:
        if status == "parked" and not parked_until.strip():
            raise ValueError("Observations with status 'parked' require a valid 'parked_until' date (YYYY-MM-DD)")

        is_subagent = (
            os.environ.get("ANTIGRAVITY_SUBAGENT") == "1" or
            os.environ.get("SUBAGENT") == "1" or
            os.environ.get("WORKER_DELEGATE") == "1"
        )
        if is_subagent:
            return {
                "id": -1,
                "fingerprint": "subagent_refused",
                "title": title,
                "status": "refused_subagent",
                "kind": kind,
                "target": target,
                "rule_id": rule_id,
                "siblings_checked": siblings_checked,
                "scope": scope,
                "parked_until": parked_until,
                "evidence": evidence,
                "created": "",
                "resolved": "",
                "resolution": "subagents write nothing",
                "count": count,
                "seen_in": seen_in,
                "applies_to": applies_to
            }

        ws_dir = os.path.abspath(WORKSPACE_DIR)
        if target and os.path.isabs(target):
            norm_target = os.path.abspath(target)
            if norm_target.startswith(ws_dir):
                target = os.path.relpath(norm_target, ws_dir).replace("\\", "/")

        if evidence:
            if ws_dir in evidence:
                evidence = evidence.replace(ws_dir, ".").replace(ws_dir.replace("\\", "/"), ".")
            if "file://" in evidence:
                evidence = re.sub(r"file://[^\s)]+", lambda m: m.group(0).replace("file://", ""), evidence)

        target_or_rule = rule_id if rule_id else target
        fp = self.compute_fingerprint(kind, target_or_rule, title)

        active = self.get_all_observations()
        for item in active:
            if item.get("fingerprint") == fp and item.get("status") in ("open", "parked"):
                if evidence:
                    existing_ev_parts = [p.strip() for p in item.get("evidence", "").split(" | ") if p.strip()]
                    if evidence.strip() not in existing_ev_parts:
                        existing_ev_parts.append(evidence.strip())
                    item["evidence"] = " | ".join(existing_ev_parts)
                item["count"] = int(item.get("count", 1)) + 1
                if seen_in and seen_in not in item.get("seen_in", ""):
                    item["seen_in"] = (item.get("seen_in", "") + ", " + seen_in).strip(", ")
                if applies_to and applies_to not in item.get("applies_to", ""):
                    item["applies_to"] = (item.get("applies_to", "") + ", " + applies_to).strip(", ")
                self._write_active_list(active)
                return item

        obs_id = self.get_next_id()
        now_str = datetime.now().isoformat()

        entry = {
            "id": obs_id,
            "fingerprint": fp,
            "title": title.strip(),
            "status": status.strip(),
            "kind": kind.strip(),
            "target": target.strip(),
            "rule_id": rule_id.strip(),
            "siblings_checked": siblings_checked.strip() or "true",
            "scope": scope.strip() or "project",
            "parked_until": parked_until.strip(),
            "evidence": evidence.strip(),
            "created": now_str,
            "resolved": "",
            "resolution": "",
            "count": count,
            "seen_in": seen_in.strip(),
            "applies_to": applies_to.strip()
        }

        if status.strip() in ("actioned", "resolved", "declined"):
            entry["resolved"] = now_str
            entry["resolution"] = "Added directly with resolved status"
            self._append_to_archive(entry)
            return entry

        active.append(entry)
        self._write_active_list(active)
        return entry

    def _format_entry(self, entry: Dict[str, Any]) -> str:
        lines = [
            f"## Observation {entry['id']}: {entry['title']}",
            f"- **id**: {entry['id']}",
            f"- **fingerprint**: {entry['fingerprint']}",
            f"- **status**: {entry['status']}",
            f"- **kind**: {entry['kind']}",
            f"- **target**: {entry['target']}",
            f"- **rule_id**: {entry['rule_id']}",
            f"- **siblings_checked**: {entry['siblings_checked']}",
            f"- **scope**: {entry['scope']}",
        ]
        if entry.get("count") and int(entry.get("count", 1)) > 1:
            lines.append(f"- **count**: {entry['count']}")
        if entry.get("seen_in"):
            lines.append(f"- **seen_in**: {entry['seen_in']}")
        if entry.get("applies_to"):
            lines.append(f"- **applies_to**: {entry['applies_to']}")
        if entry.get("parked_until"):
            lines.append(f"- **parked_until**: {entry['parked_until']}")
        if entry.get("evidence"):
            lines.append(f"- **evidence**: {entry['evidence']}")
        if entry.get("created"):
            lines.append(f"- **created**: {entry['created']}")
        if entry.get("resolved"):
            lines.append(f"- **resolved**: {entry['resolved']}")
        if entry.get("resolution"):
            lines.append(f"- **resolution**: {entry['resolution']}")
        if entry.get("superseded_by"):
            lines.append(f"- **superseded_by**: {entry['superseded_by']}")
        lines.append("")
        return "\n".join(lines)

    def _write_active_list(self, entries: List[Dict[str, Any]]):
        header = (
            "# Observation Ledger (Active & Parked Signals)\n\n"
            "> Raw signals: corrections, tool failures, mechanical catches, verify fails, rule violations.\n\n"
        )
        content = header + "\n".join(self._format_entry(e) for e in entries)
        atomic_write_text(self.active_path, content)

    def _write_archive_list(self, entries: List[Dict[str, Any]]):
        header = (
            "# Observation Ledger Archive (Resolved Signals)\n\n"
            "> Resolved, declined, or superseded observations.\n\n"
        )
        content = header + "\n".join(self._format_entry(e) for e in entries)
        atomic_write_text(self.archive_path, content)

    def _append_to_archive(self, entry: Dict[str, Any]) -> None:
        arch = self.get_archive_observations()
        arch.append(entry)
        self._write_archive_list(arch)

    def list_observations(self, status: str = None, limit: int = None) -> List[Dict[str, Any]]:
        active = self.get_all_observations()
        if status:
            active = [e for e in active if e.get("status") == status]
        if limit and limit > 0:
            active = active[:limit]
        return active

    def check_rule_violations(self, rule_id: str) -> Dict[str, Any]:
        if not rule_id:
            return {"rule_id": "", "count": 0, "forced_tier0": False, "observations": []}
        active = self.get_all_observations()
        arch = self.get_archive_observations()
        matching_active = [e for e in active if e.get("rule_id") == rule_id and e.get("status") in ("open", "parked")]
        matching_rolled = [e for e in arch if e.get("rule_id") == rule_id and e.get("kind") == "violation" and e.get("status") == "superseded"]
        all_matching = matching_active + matching_rolled
        count = sum(int(e.get("count", 1)) for e in all_matching)
        forced_tier0 = count >= 2
        return {
            "rule_id": rule_id,
            "count": count,
            "forced_tier0": forced_tier0,
            "observations": all_matching
        }

    def get_digest(self) -> str:
        active = self.get_all_observations()

        if os.path.exists(self.active_path):
            with open(self.active_path, "r", encoding="utf-8", errors="replace") as f:
                raw = f.read()
            if "## Observation " in raw and len(active) == 0:
                return "OBSERVATION SCAN BROKEN"

        open_count = sum(1 for e in active if e.get("status") == "open")
        parked_count = sum(1 for e in active if e.get("status") == "parked")
        targets = [e.get("target") or e.get("rule_id") for e in active if e.get("target") or e.get("rule_id")]
        top_target = targets[0] if targets else "none"

        # Check Head Generation if available
        head_gen_label = "none"
        try:
            from core.memory import RecallMemoryManager
            with RecallMemoryManager() as rm:
                head = rm.get_head_generation()
                if head:
                    head_gen_label = f"G{head.get('generation_count', 0)}"
        except Exception:
            pass

        return f"gen={head_gen_label} open={open_count} parked={parked_count} top-target={top_target}"

    def rollover_generation(self, max_active_keep: int = 10) -> Dict[str, Any]:
        """
        Synthesizes older active/actioned observations into a compact Head Reflection
        and retires them into OBSERVATIONS.archive.md with status='superseded' and
        superseded_by='GEN-<n>'. Preserves freshest max_active_keep entries in active ledger.
        """
        active = self.get_all_observations()
        if len(active) <= max_active_keep:
            return {"status": "NOOP", "active_count": len(active), "superseded_count": 0}

        # Keep freshest max_active_keep entries (sorted by id desc)
        sorted_active = sorted(active, key=lambda x: x.get("id", 0))
        to_retire = sorted_active[:-max_active_keep]
        to_keep = sorted_active[-max_active_keep:]

        # Build synthesis summary and anchor index
        anchor_map = {}
        summary_lines = []
        for e in to_retire:
            anchor_id = f"O{e['id']}"
            anchor_map[anchor_id] = {
                "title": e.get("title", ""),
                "target": e.get("target", "") or e.get("rule_id", ""),
                "kind": e.get("kind", ""),
                "evidence": e.get("evidence", "")[:120]
            }
            summary_lines.append(f"[{anchor_id}] {e.get('title')} ({e.get('target', 'core')}): {e.get('evidence', '')[:100]}")

        raw_summary_text = "\n".join(summary_lines)

        # Compact summary text using Shannon Surprisal if available
        compacted_summary = raw_summary_text
        try:
            from commands.compact import CorpusInformationCompactor
            with CorpusInformationCompactor() as compactor:
                compacted_summary = compactor.compact(raw_summary_text, keep_ratio=0.6)
        except Exception as _ce:
            _log_telemetry(_ce, "reflexion:rollover_compact")

        # Persist to memory_generations table
        new_gen_id = f"GEN-OBS-{int(time.time())}"
        try:
            from core.memory import RecallMemoryManager
            with RecallMemoryManager() as rm:
                gen_res = rm.create_reflection_generation(
                    reflection_text=compacted_summary,
                    anchor_map=anchor_map,
                    retention_floor_turns=6
                )
                new_gen_id = gen_res["id"]
        except Exception as _me:
            _log_telemetry(_me, "reflexion:rollover_memory_gen")

        # Mark retired entries with superseded_by and move to archive
        now_str = datetime.now().isoformat()
        for e in to_retire:
            e["status"] = "superseded"
            e["superseded_by"] = new_gen_id
            e["resolved"] = now_str
            e["resolution"] = f"Rolled over into {new_gen_id}"

        self._write_active_list(to_keep)

        arch = self.get_archive_observations()
        arch.extend(to_retire)
        self._write_archive_list(arch)

        return {
            "status": "SUCCESS",
            "head_generation_id": new_gen_id,
            "active_remaining": len(to_keep),
            "superseded_count": len(to_retire),
            "reflection_bytes": len(compacted_summary)
        }

    def resolve_observation(self, obs_id: int, resolution: str = "resolved", status: str = "actioned") -> bool:
        active = self.get_all_observations()
        target_entry = None
        remaining = []

        for e in active:
            if e["id"] == obs_id:
                target_entry = e
            else:
                remaining.append(e)

        if not target_entry:
            return False

        target_entry["status"] = status
        target_entry["resolved"] = datetime.now().isoformat()
        target_entry["resolution"] = resolution

        self._write_active_list(remaining)

        arch = self.get_archive_observations()
        arch.append(target_entry)
        self._write_archive_list(arch)
        return True


def mine_operator_habits(workspace_dir: Optional[str] = None, profile_path: Optional[str] = None) -> Dict[str, Any]:
    ws = os.path.abspath(workspace_dir) if workspace_dir else WORKSPACE_DIR
    orion_working = os.path.join(ws, ".orion", "working")
    if not profile_path:
        profile_path = os.path.join(orion_working, "operator_profile.json")

    os.makedirs(os.path.dirname(profile_path), exist_ok=True)

    tool_histogram = Counter()
    correction_heatmap = Counter()
    action_sequence = []
    verify_failures = 0

    traj_file = os.path.join(orion_working, "trajectory.jsonl")
    if os.path.exists(traj_file):
        try:
            with open(traj_file, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.strip():
                        try:
                            item = json.loads(line.strip())
                            action_type = item.get("action_type") or item.get("payload", {}).get("tool_name")
                            if action_type:
                                tool_histogram[action_type] += 1
                                action_sequence.append(action_type)
                        except Exception:
                            pass
        except Exception as _te:
            _log_telemetry(_te, "reflexion:mine_habits_read_traj")

    ngram_counts = Counter()
    if len(action_sequence) >= 3:
        for i in range(len(action_sequence) - 2):
            gram = tuple(action_sequence[i:i+3])
            ngram_counts[gram] += 1

    ngram_patterns = []
    for gram, cnt in ngram_counts.items():
        if cnt >= 3:
            ngram_patterns.append({
                "pattern": list(gram),
                "count": cnt,
                "proposes_skill": f"propose_skill_{'_and_'.join(gram)}"
            })

            try:
                ledger = ObservationLedger()
                pattern_str = " -> ".join(gram)
                ledger.add_observation(
                    title=f"Propose skill for frequent action sequence: {pattern_str}",
                    kind="habit",
                    target="skills",
                    rule_id="OPERATOR_HABIT_SKILL_PROPOSAL",
                    evidence=f"Action sequence [{pattern_str}] repeated {cnt} times"
                )
            except Exception:
                pass

    catches_file = os.path.join(orion_working, "mechanical_catches.json")
    if os.path.exists(catches_file):
        try:
            with open(catches_file, "r", encoding="utf-8", errors="replace") as f:
                catches = json.load(f)
                if isinstance(catches, list):
                    for c in catches:
                        ctx = c.get("context", "unknown")
                        correction_heatmap[ctx] += 1
                        if "verify" in ctx.lower() or "gate" in ctx.lower():
                            verify_failures += 1
        except Exception as _ce:
            _log_telemetry(_ce, "reflexion:mine_habits_read_catches")

    profile_data = {
        "timestamp": datetime.now().isoformat(),
        "tool_histogram": dict(tool_histogram),
        "correction_heatmap": dict(correction_heatmap),
        "ngram_patterns": ngram_patterns,
        "verify_failures": verify_failures,
        "total_actions_logged": len(action_sequence)
    }

    try:
        from core.harness.capture import SecretRedactor
        raw_json = json.dumps(profile_data, indent=2)
        redacted_json = SecretRedactor.redact_text(raw_json)
        atomic_write_text(profile_path, redacted_json)
        return {"ok": True, "profile_path": profile_path, "patterns_found": len(ngram_patterns)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def backfill_historical_observations(workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Backfills historical friction points, bugfixes, and handover notes into ObservationLedger.
    Scans context/00_Strategy/MEMORY.md and .orion/episodic/session_history.md.
    """
    ws = os.path.abspath(workspace_dir) if workspace_dir else WORKSPACE_DIR
    ledger = ObservationLedger()
    backfilled_count = 0

    sources = [
        os.path.join(ws, "context", "00_Strategy", "MEMORY.md"),
        os.path.join(ws, ".orion", "episodic", "session_history.md"),
    ]

    for src_path in sources:
        if not os.path.isfile(src_path):
            continue
        try:
            with open(src_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            for line in content.splitlines():
                line_s = line.strip()
                if not line_s.startswith(("-", "*")):
                    continue
                lower_l = line_s.lower()
                if any(m in lower_l for m in ("[bugfix]", "[fix]", "[friction]", "[error]", "[learning]", "[deviation]", "[gap]")):
                    clean_title = re.sub(r"^[-*]\s*(\[[A-Za-z0-9_-]+\]\s*)?", "", line_s).strip()
                    if len(clean_title) > 10:
                        ledger.add_observation(
                            title=clean_title[:120],
                            kind="improve",
                            target=os.path.basename(src_path),
                            rule_id="HISTORICAL_BACKFILL",
                            evidence=line_s[:200],
                            status="actioned"
                        )
                        backfilled_count += 1
        except Exception as _e:
            _log_telemetry(_e, "reflexion:backfill_historical")

    return {"ok": True, "backfilled_count": backfilled_count}


class PromptRuleCompiler:
    """
    Deterministic Rule Enforcement Verifier.
    Verifies rule IDs against registered AST security rules (security_rules.yml)
    and mechanical check suites in verify_agents.py.
    """
    def __init__(self, matrix_dir: str = MATRIX_DIR, base_agents_dir: str = BASE_DIR):
        self.matrix_dir = matrix_dir
        self.base_agents_dir = base_agents_dir

    def _load_deterministic_rule_ids(self) -> Set[str]:
        enforced_ids: Set[str] = set()
        sec_yml = os.path.join(self.base_agents_dir, "rules", "ast", "security_rules.yml")
        if os.path.exists(sec_yml):
            try:
                with open(sec_yml, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("id:"):
                            enforced_ids.add(line.split(":", 1)[1].strip().lower())
            except Exception as _e:
                _log_telemetry(_e, "reflexion.py:load_sec_yml")

        # 1. Parse AST of verify_agents.py to extract check functions and categories
        va_file = os.path.join(self.base_agents_dir, "scripts", "commands", "verify_agents.py")
        if os.path.exists(va_file):
            try:
                with open(va_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=va_file)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("check_"):
                        chk_name = node.name.replace("check_", "").replace("_", "-").lower()
                        enforced_ids.add(chk_name)
                        for part in chk_name.split("-"):
                            if len(part) > 3:
                                enforced_ids.add(part)
                    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                        val = node.value.strip().lower()
                        for prefix in ("gate ", "check "):
                            if val.startswith(prefix):
                                clean_val = val.split(":", 1)[-1].strip().replace(" ", "-").replace("&", "").replace("--", "-")
                                if clean_val:
                                    enforced_ids.add(clean_val)
            except Exception as _e:
                _log_telemetry(_e, "reflexion.py:ast_parse_verify_agents")

        # 2. Parse AST of core/security.py
        sec_py = os.path.join(self.base_agents_dir, "scripts", "core", "security.py")
        if os.path.exists(sec_py):
            try:
                with open(sec_py, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=sec_py)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        enforced_ids.add(node.name.lower().replace("_", "-"))
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id.isupper():
                                enforced_ids.add(target.id.lower().replace("_", "-"))
            except Exception as _e:
                _log_telemetry(_e, "reflexion.py:ast_parse_security_py")

        # 3. Parse AST of evals/audit_aesthetics.py
        aes_py = os.path.join(self.base_agents_dir, "evals", "audit_aesthetics.py")
        if os.path.exists(aes_py):
            try:
                with open(aes_py, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=aes_py)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and ("audit" in node.name or "scan" in node.name):
                        enforced_ids.add(node.name.lower().replace("_", "-"))
            except Exception as _e:
                _log_telemetry(_e, "reflexion.py:ast_parse_audit_aesthetics")

        # Core mechanical categories
        enforced_ids.update({
            "security", "mechanical", "protocol", "link", "hygiene",
            "context-lint", "instruction-lint", "schema-cohesion",
            "version-synchronization", "router-parity", "ast-security",
            "ast-sql-injection", "ast-command-injection", "ast-hardcoded-secret",
            "no-empty-catch", "security-integrity", "portability-hygiene",
            "rtk", "token", "prompt-security", "trojan-source"
        })
        return enforced_ids

    def audit_rule_enforcement(self) -> Dict[str, Any]:
        rules: List[Dict[str, Any]] = []
        if os.path.exists(self.matrix_dir):
            for fname in os.listdir(self.matrix_dir):
                if fname.endswith('.json'):
                    fp = os.path.join(self.matrix_dir, fname)
                    try:
                        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                for k, v in data.items():
                                    if k == "global":
                                        continue
                                    rules.append({
                                        "source_matrix": fname,
                                        "id": k,
                                        "description": str(v)[:120] if v else ""
                                    })
                    except Exception as e:
                        _log_telemetry(e, 'reflexion.py:audit_rules:load')

        enforced_registry = self._load_deterministic_rule_ids()
        enforced = []
        advisory_only = []

        for r in rules:
            rid = str(r['id']).lower().replace("_", "-")
            k_clean = re.sub(r'[^a-zA-Z0-9\s-]', ' ', str(r['id'])).lower()
            words = [w for w in k_clean.split() if len(w) > 3]
            is_enforced = (
                any(rid == eid or rid.startswith(eid) or eid in rid for eid in enforced_registry)
                or any(w in enforced_registry for w in words)
            )
            if is_enforced:
                enforced.append(r)
            else:
                advisory_only.append(r)

        total = len(rules)
        coverage_pct = (len(enforced) / total * 100.0) if total > 0 else 100.0

        return {
            "total_rules": total,
            "enforced_count": len(enforced),
            "advisory_count": len(advisory_only),
            "mechanical_coverage_pct": round(coverage_pct, 1),
            "enforced_sample": enforced[:5],
            "advisory_sample": advisory_only[:5]
        }


@dataclass(slots=True)
class TrialAttempt:
    trial_number: int
    solution: str
    error_output: str
    reflection: str


class ReflexionLoop:
    def __init__(self, max_trials: int = 3):
        self.max_trials = max_trials
        self.history: List[TrialAttempt] = []

    def record_attempt(self, solution: str, error_output: str, reflection: str) -> TrialAttempt:
        trial_num = len(self.history) + 1
        attempt = TrialAttempt(
            trial_number=trial_num,
            solution=solution,
            error_output=error_output,
            reflection=reflection
        )
        self.history.append(attempt)
        return attempt

    def is_circuit_broken(self) -> bool:
        return len(self.history) >= self.max_trials

    def run_evaluator(self, test_cmd: Union[str, List[str]], timeout: float = 30.0) -> Tuple[int, str]:
        try:
            if isinstance(test_cmd, list):
                cmd = test_cmd
            else:
                cmd = shlex.split(test_cmd, posix=(os.name != "nt"))

            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            combined = f"{res.stdout}\n{res.stderr}".strip() if res.stdout and res.stderr else (res.stdout or res.stderr or "").strip()
            return res.returncode, combined
        except subprocess.TimeoutExpired:
            return 124, f"TimeoutExpired: Evaluator exceeded {timeout}s"
        except Exception as e:
            _log_telemetry(e, f"ReflexionLoop:run_evaluator:{test_cmd}")
            return 1, str(e)

    def synthesize_critique(self, error_output: str) -> str:
        tb_match = re.search(r'File "([^"]+)", line (\d+), in (\S+)', error_output)
        js_match = re.search(r'at\s+(?:[^\s(]+\s+\()?([^():\s]+\.(?:ts|tsx|js|dart)):(\d+):\d+', error_output)

        loc_info = ""
        target_file, target_line = None, None
        if tb_match:
            target_file, target_line, fn_name = tb_match.group(1), int(tb_match.group(2)), tb_match.group(3)
            loc_info = f" [Origin: {os.path.basename(target_file)}:L{target_line} in `{fn_name}`]"
        elif js_match:
            target_file, target_line = js_match.group(1), int(js_match.group(2))
            loc_info = f" [Origin: {os.path.basename(target_file)}:L{target_line}]"

        span_hint = ""
        if target_file and os.path.isfile(target_file):
            try:
                from core.scanner import generate_skeleton
                for skel_line in generate_skeleton(target_file):
                    m = re.search(r'\[L(\d+)-L(\d+)\]\s*(.+)', skel_line)
                    if m and int(m.group(1)) <= target_line <= int(m.group(2)):
                        span_hint = f" Target AST Span: `[L{m.group(1)}-L{m.group(2)}] {m.group(3)}`."
                        break
            except Exception as _e:
                _log_telemetry(_e, "ReflexionLoop:skeleton_lookup")

        lower = error_output.lower()
        if "syntaxerror" in lower or "indentationerror" in lower:
            base = "Syntax/AST Parse Violation."
        elif "assertionerror" in lower or "assert" in lower:
            base = "Contract Assertion Failure: state delta did not match expected invariant."
        elif "timeout" in lower:
            base = "Execution Timeout: infinite loop or blocking I/O detected."
        elif "nameerror" in lower or "attributeerror" in lower or "typeerror" in lower:
            base = "Symbol/Type Resolution Failure."
        else:
            base = "Unhandled Runtime Exception."

        return f"{base}{loc_info}{span_hint}"

    def build_reflection_prompt(self, problem: str) -> str:
        prompt = [f"Task Objective: {problem}\n"]
        for t in self.history:
            prompt.append(f"--- Trial {t.trial_number} Failed ---")
            prompt.append(f"Error Diagnostic:\n{t.error_output}")
            prompt.append(f"Verbal Self-Reflection:\n{t.reflection}\n")
        prompt.append("Instruction: Provide a corrected implementation resolving the flaws diagnosed above.")
        return "\n".join(prompt)

    @staticmethod
    def _classify_failure_complexity(error_output: str, source_lines_count: int) -> Tuple[str, int]:
        """
        Tier-0 Mechanical Complexity Estimator:
        Inspects error output and file metrics to classify repair difficulty dynamically
        so 3B, 7B, 14B, and 30B+ models each receive tasks matching their capability envelope.
        """
        err_lower = (error_output or "").lower()
        if any(k in err_lower for k in ("syntaxerror", "indentationerror", "importerror", "modulenotfounderror", "nameerror")):
            return "micro_syntax", min(source_lines_count, 15)
        if source_lines_count <= 250:
            return "single_fn", min(source_lines_count, 50)
        return "multi_fn", min(source_lines_count, 120)

    def auto_heal(
        self,
        target_file: str,
        test_cmd: Union[str, List[str]],
        problem_description: str = "",
        timeout: float = 30.0,
        min_params_b: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Seam 3: Elastic Neuro-Symbolic Self-Healing Loop across 0B..70B+ Local SLMs & Cloud Tiers.
        - Dynamically matches failure complexity against available local model parameters (1.5B, 3B, 7B, 14B, 30B+).
        - Enforces AST validity and test verification on every candidate patch with atomic rollback on failure.
        - Gracefully slides to Cloud 'BUDGET', 'STANDARD', or 'PREMIUM' with a pre-digested AST diagnostic packet
          whenever the local model is offline, below the dynamic complexity floor, or exhausts its trial budget.
        """
        from core.capabilities import execute_neuro_symbolic, resolve_elastic_execution_plan
        from core.db import atomic_write_text

        abs_target = os.path.abspath(target_file)
        if not os.path.isfile(abs_target):
            return {"healed": False, "reason": f"Target file not found: {target_file}", "trials": 0}

        exit_code, output = self.run_evaluator(test_cmd, timeout=timeout)
        if exit_code == 0:
            return {"healed": True, "status": "already_green", "trials": 0, "output": output}

        with open(abs_target, "r", encoding="utf-8", errors="replace") as f:
            original_source = f.read()

        source_lines_count = len(original_source.splitlines())
        task_complexity, est_span = self._classify_failure_complexity(output, source_lines_count)
        elastic_plan = resolve_elastic_execution_plan(
            task_complexity=task_complexity,
            blast_radius_files=1,
            span_lines=est_span,
        )

        effective_min_b = min_params_b if min_params_b is not None else elastic_plan["effective_min_params_b"]
        dynamic_max_trials = (
            min(self.max_trials, elastic_plan["local_max_trials"])
            if min_params_b is None
            else self.max_trials
        )

        def _validate_patch_schema(data: Any) -> Tuple[bool, str]:
            if not isinstance(data, dict):
                return False, "Output must be a JSON object"
            for req_key in ("old_string", "new_string", "reflection"):
                if req_key not in data or not isinstance(data[req_key], str):
                    return False, f"Missing or non-string required key: '{req_key}'"
            if not data["old_string"].strip():
                return False, "'old_string' must be non-empty"
            if data["old_string"] not in original_source:
                return False, "'old_string' does not match exact lines in target file"
            if abs_target.endswith(".py"):
                candidate = original_source.replace(data["old_string"], data["new_string"], 1)
                try:
                    ast.parse(candidate)
                except SyntaxError as se:
                    return False, f"Candidate patch introduces Python SyntaxError: {se}"
            return True, "valid"

        local_slm_skipped = (dynamic_max_trials == 0)
        while not self.is_circuit_broken() and len(self.history) < dynamic_max_trials:
            trial_num = len(self.history) + 1
            critique = self.synthesize_critique(output)
            reflection_ctx = self.build_reflection_prompt(problem_description or critique)
            prompt = (
                f"{reflection_ctx}\n\n"
                f"Target File ({os.path.basename(abs_target)}):\n"
                f"```\n{original_source[:8000]}\n```\n\n"
                f"Latest Test Output (Exit Code {exit_code}):\n{output[-1500:]}\n\n"
                "Return ONLY a JSON object with keys:\n"
                '{"old_string": "<exact lines to replace>", "new_string": "<fixed lines>", "reflection": "<root cause>"}'
            )

            patch_data, provider = execute_neuro_symbolic(
                task_type="autoharness_self_heal",
                prompt=prompt,
                validator_fn=_validate_patch_schema,
                fallback_fn=None,
                handoff_payload=None,
                timeout_sec=min(timeout, 25.0),
                temperature=0.1,
                min_params_b=effective_min_b,
            )

            if not isinstance(patch_data, dict):
                local_slm_skipped = True
                break

            patched_source = original_source.replace(patch_data["old_string"], patch_data["new_string"], 1)
            atomic_write_text(abs_target, patched_source)

            new_code, new_out = self.run_evaluator(test_cmd, timeout=timeout)
            self.record_attempt(
                solution=patch_data["new_string"][:300],
                error_output=new_out[:500],
                reflection=patch_data.get("reflection", critique),
            )

            if new_code == 0:
                engine = ReflexionEngine()
                engine.record_learning(
                    title=f"Self-Healed {os.path.basename(abs_target)} on trial #{trial_num}",
                    root_cause=patch_data.get("reflection", critique),
                    fix_applied=f"Surgical diff applied via {provider}",
                    self_evolve_rule=f"Verify AST and invariant conditions in {os.path.basename(abs_target)}",
                    trigger=f"Test failure on {os.path.basename(abs_target)}",
                    evidence=f"Exit Code {exit_code} -> Exit Code 0 in {trial_num} trial(s)",
                    intervention=patch_data.get("reflection", critique),
                    guard="Preserve existing function signatures",
                    resting_tier="TIER-0",
                )
                return {
                    "healed": True,
                    "provider": provider,
                    "trials": trial_num,
                    "task_complexity": task_complexity,
                    "reflection": patch_data.get("reflection", ""),
                }

            # Mandatory Rollback Gate (Anti-Shotgun Rule)
            atomic_write_text(abs_target, original_source)
            exit_code, output = new_code, new_out

        atomic_write_text(abs_target, original_source)

        if len(self.history) >= 3:
            recommended_tier = "PREMIUM"
            reason_code = "circuit_breaker_3_consecutive_local_failures"
        else:
            recommended_tier = elastic_plan["recommended_cloud_tier"]
            reason_code = (
                f"elastic_downshift_local_{elastic_plan['installed_params_b']}B_for_{task_complexity}_min_{effective_min_b}B"
                if local_slm_skipped
                else f"borderline_local_trial_exhausted_escalate_{recommended_tier.lower()}"
            )

        critique_summary = self.synthesize_critique(output)
        try:
            from core.capabilities import enqueue_cloud_handoff
            enqueue_cloud_handoff(
                task_type="reflexion_surgical_repair",
                payload={
                    "target_file": os.path.relpath(abs_target, WORKSPACE_DIR),
                    "test_cmd": test_cmd if isinstance(test_cmd, str) else " ".join(test_cmd),
                    "task_complexity": task_complexity,
                    "trials_attempted": len(self.history),
                    "recommended_tier": recommended_tier,
                    "ast_critique": critique_summary,
                    "last_error": output[-1000:],
                },
                reason=reason_code,
            )
        except Exception as _he:
            _log_telemetry(_he, "ReflexionLoop:enqueue_cloud_handoff")

        return {
            "healed": False,
            "reason": reason_code,
            "task_complexity": task_complexity,
            "recommended_tier": recommended_tier,
            "ast_critique": critique_summary,
            "trials": len(self.history),
        }


# ==============================================================================
# SECTION 2: TEMPORAL PULSE & EPISODIC CONSOLIDATION
# ==============================================================================

def ensure_dirs():
    for d in [SESSION_DIR, MILESTONE_DIR, EPOCH_DIR, SESSION_ARCHIVE, MILESTONE_ARCHIVE]:
        os.makedirs(d, exist_ok=True)


def parse_transcript_observations(transcript_path=None):
    observations = {
        "timestamp": datetime.now().isoformat(),
        "requests": [],
        "decisions": [],
        "bugfixes": [],
        "features": [],
        "refactors": [],
        "discoveries": [],
        "security_alerts": [],
        "sensitive": [],
        "open_loops": [],
        "modified_files": set(),
        "executed_commands": set()
    }

    target_path = None
    if transcript_path and os.path.exists(transcript_path):
        target_path = transcript_path
    else:
        candidates = [
            os.path.join(WORKSPACE_DIR, '.orion', 'working', 'transcript.jsonl'),
            os.path.join(WORKSPACE_DIR, '.orion', 'transcript.jsonl'),
        ]
        home = os.path.expanduser('~')
        gemini_logs = glob.glob(os.path.join(home, '.gemini', 'antigravity', 'brain', '*', '.system_generated', 'logs', 'transcript.jsonl'))
        gemini_logs.extend(glob.glob(os.path.join(home, '.gemini', 'antigravity-ide', 'brain', '*', '.system_generated', 'logs', 'transcript.jsonl')))
        if gemini_logs:
            gemini_logs.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            candidates.extend(gemini_logs[:3])

        for cand in candidates:
            if os.path.exists(cand):
                target_path = cand
                break

    if not target_path or not os.path.exists(target_path):
        observations["modified_files"] = []
        observations["executed_commands"] = []
        return observations

    tag_regex = re.compile(
        r'\[(decision|bugfix|feature|refactor|discovery|security_alert|sensitive|open_loop)\]\s*:?\s*(.+)',
        re.IGNORECASE
    )

    try:
        with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    entry = json.loads(line_str)
                except Exception:
                    continue

                entry_type = entry.get("type")
                content = entry.get("content", "")

                if entry_type == "USER_INPUT" and isinstance(content, str) and content.strip():
                    clean_content = re.sub(r'<[^>]+>', '', content).strip()
                    if clean_content and len(clean_content) > 5 and clean_content not in observations["requests"]:
                        observations["requests"].append(clean_content[:200])

                if isinstance(content, str):
                    for match in tag_regex.finditer(content):
                        tag = match.group(1).lower()
                        val = match.group(2).strip()
                        category_map = {
                            "decision": "decisions",
                            "bugfix": "bugfixes",
                            "feature": "features",
                            "refactor": "refactors",
                            "discovery": "discoveries",
                            "security_alert": "security_alerts",
                            "sensitive": "sensitive",
                            "open_loop": "open_loops"
                        }
                        target_list = category_map.get(tag)
                        if target_list and val not in observations[target_list]:
                            observations[target_list].append(val)

                tool_calls = entry.get("tool_calls", [])
                if isinstance(tool_calls, list):
                    for tc in tool_calls:
                        if isinstance(tc, dict):
                            fn_name = tc.get("name") or tc.get("toolAction")
                            args = tc.get("args", {}) or tc.get("arguments", {})
                            if fn_name in ["write_to_file", "replace_file_content", "multi_replace_file_content"]:
                                target_f = args.get("TargetFile") or args.get("target_file")
                                if target_f:
                                    observations["modified_files"].add(target_f)
                            elif fn_name in ["run_command", "execute"]:
                                cmd_str = args.get("CommandLine") or args.get("command")
                                if cmd_str:
                                    observations["executed_commands"].add(cmd_str[:120])
    except Exception as e:
        sys.stderr.write(f"[WARN] Error parsing transcript {target_path}: {e}\n")

    observations["modified_files"] = sorted(list(observations["modified_files"]))
    observations["executed_commands"] = sorted(list(observations["executed_commands"]))
    return observations


def consolidate_session(transcript_path=None):
    ensure_dirs()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(SESSION_DIR, f"session_{timestamp}.md")

    handoff_content = ""
    if os.path.exists(HANDOFF_FILE):
        try:
            with open(HANDOFF_FILE, 'r', encoding='utf-8') as f:
                handoff_content = f.read()
        except Exception as e:
            sys.stderr.write(f"[WARN] Failed to read handoff file: {e}\n")

    learnings_content = ""
    if os.path.exists(LEARNINGS_FILE):
        try:
            with open(LEARNINGS_FILE, 'r', encoding='utf-8') as f:
                learnings_content = f.read()
        except Exception as e:
            sys.stderr.write(f"[WARN] Failed to read learnings file: {e}\n")

    db_path = os.path.join(WORKSPACE_DIR, '.orion', 'orion.db')
    db_events = []
    if os.path.exists(db_path):
        try:
            conn = connect_sqlite(db_path)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='telemetry'")
            if c.fetchone():
                c.execute("SELECT event_type, exit_code, timestamp FROM telemetry ORDER BY id DESC LIMIT 50")
                for row in c.fetchall():
                    db_events.append({
                        "event_type": row[0],
                        "payload": {"exit_code": row[1], "error": f"{row[0]} (exit_code={row[1]})" if row[1] else ""},
                        "timestamp": row[2]
                    })
            conn.close()
        except Exception as e:
            sys.stderr.write(f"[WARN] Telemetry retrieval skipped: {e}\n")

    obs = parse_transcript_observations(transcript_path)

    all_decisions = list(obs["decisions"])
    all_errors = list(obs["bugfixes"])
    for ev in db_events:
        if ev["event_type"] == "decision" and ev["payload"].get("description"):
            desc = ev["payload"]["description"]
            if desc not in all_decisions:
                all_decisions.append(desc)
        elif ev["event_type"] in ["error", "circuit_breaker", "remediation_failure"]:
            err_msg = ev["payload"].get("error") or ev["payload"].get("reason") or ev["event_type"]
            if str(err_msg) not in all_errors:
                all_errors.append(str(err_msg))

    harness_dir = os.path.join(WORKSPACE_DIR, '.orion', 'harness')
    harness_data = {"staged_intents": [], "ledger_mutations": []}
    harness_section = "- _(no active sovereign harness mutations in this session)_"
    if os.path.exists(harness_dir):
        try:
            from core.harness.staging import IntentQueue
            intents_dir = os.path.join(harness_dir, 'intents')
            if os.path.exists(intents_dir):
                queue = IntentQueue(intents_dir)
                staged = queue.peek()
                for intent in staged:
                    harness_data["staged_intents"].append({
                        "id": intent.id,
                        "name": intent.name,
                        "action": intent.action,
                        "reason": intent.reason
                    })

            skills_dir = os.path.join(WORKSPACE_DIR, '.agents', 'skills')
            mutations = []
            if os.path.exists(skills_dir):
                for sk_name in sorted(os.listdir(skills_dir)):
                    l_file = os.path.join(skills_dir, sk_name, '.ledger.jsonl')
                    if os.path.isfile(l_file):
                        try:
                            with open(l_file, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.strip():
                                        entry = json.loads(line.strip())
                                        entry["skill"] = sk_name
                                        mutations.append(entry)
                        except Exception as _le:
                            _log_telemetry(_le, "reflexion:read_ledger")
            if mutations:
                harness_data["ledger_mutations"] = mutations[-5:]

            blocks = []
            if harness_data["staged_intents"]:
                blocks.append("**Staged Skill Intents**:\n" + "\n".join(
                    f"- `{st['id']}` [{st['action']}]: **{st['name']}** — {st['reason']}" for st in harness_data["staged_intents"]
                ))
            if harness_data["ledger_mutations"]:
                blocks.append("**Recent Mutation Ledger**:\n" + "\n".join(
                    f"- `[{mut.get('action', '')}]`: {mut.get('skill', '')} — {mut.get('reason', '')}" for mut in harness_data["ledger_mutations"]
                ))
            if blocks:
                harness_section = "\n\n".join(blocks)
        except Exception as e:
            harness_section = f"-(harness inspection non-fatal error: {e})-"

    recent_turns = []
    try:
        from core.memory import RecallMemoryManager
        recent_turns = RecallMemoryManager().get_recent_turns(limit=10)
    except Exception as _rt_err:
        _log_telemetry(_rt_err, "reflexion:get_recent_turns")

    turns_section = "\n".join(f"- **{t['role']}**: {t['content'][:120]}" for t in recent_turns) if recent_turns else "- _(no recall turns recorded in this session)_"

    git_diff_summary = ""
    try:
        if os.path.exists(os.path.join(WORKSPACE_DIR, '.git')):
            status_res = subprocess.run(
                ["git", "status", "--short"],
                cwd=WORKSPACE_DIR,
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'
            )
            if status_res.returncode == 0 and status_res.stdout.strip():
                git_diff_summary = status_res.stdout.strip()
    except Exception:
        git_diff_summary = ""

    diff_block = f"```text\n{git_diff_summary}\n```" if git_diff_summary else "_(clean working tree; 0 uncommitted deltas)_"

    obs_blocks = []
    if obs["requests"]:
        obs_blocks.append("### User Requests & Session Intent\n" + "\n".join(f"- {r}" for r in obs["requests"][:5]))
    if all_decisions:
        obs_blocks.append("### Architectural Decisions (`[decision]`)\n" + "\n".join(f"- {d}" for d in all_decisions[:8]))
    if all_errors:
        obs_blocks.append("### Bugfixes & Root Causes (`[bugfix]`)\n" + "\n".join(f"- {e}" for e in all_errors[:8]))
    if obs["features"]:
        obs_blocks.append("### Features & Capabilities (`[feature]`)\n" + "\n".join(f"- {ft}" for ft in obs["features"][:8]))
    if obs["refactors"]:
        obs_blocks.append("### Refactorings & AST Hardening (`[refactor]`)\n" + "\n".join(f"- {rf}" for rf in obs["refactors"][:8]))
    if obs["discoveries"]:
        obs_blocks.append("### Codebase Discoveries (`[discovery]`)\n" + "\n".join(f"- {dc}" for dc in obs["discoveries"][:8]))
    if obs["security_alerts"] or obs["sensitive"]:
        sec_items = [f"- [security_alert] {s}" for s in obs["security_alerts"]] + [f"- [sensitive] {s}" for s in obs["sensitive"]]
        obs_blocks.append("### Security & Configuration Boundaries\n" + "\n".join(sec_items[:8]))
    if obs["open_loops"]:
        obs_blocks.append("### Open Loops & Deferred Debt (`[open_loop]`)\n" + "\n".join(f"- {ol}" for ol in obs["open_loops"][:8]))

    observations_section = "\n\n".join(obs_blocks) if obs_blocks else "- _(no explicit tagged observations detected)_"

    pulse = f"""# Session Pulse — {timestamp}

## Session Summary
{handoff_content[:500] if handoff_content else '_(no handoff data)_'}

## Recent Conversation Turns (Recall Memory)
{turns_section}

## High-Signal Episodic Observations
{observations_section}

## Modified Files & Git Delta
{diff_block}

## Active Learnings
{chr(10).join(learnings_content.split(chr(10))[:10]) if learnings_content else '- _(no learnings yet)_'}

## Autonomous Skill Evolution (Harness Ledgers)
{harness_section}

---
_Generated by Temporal Pulse Engine at {datetime.now().isoformat()}_
"""

    atomic_write_text(output_path, pulse)

    print(f"[PULSE] Session pulse generated: {output_path}")

    if harness_data.get("staged_intents") or harness_data.get("ledger_mutations"):
        try:
            harness_log_lines = []
            for st in harness_data["staged_intents"]:
                harness_log_lines.append(f"- [feature]: Staged autonomous skill intent `{st['name']}` ({st['action']}): {st['reason']}")
            for mut in harness_data["ledger_mutations"][-3:]:
                harness_log_lines.append(f"- [refactor]: Harness ledger mutation `{mut['skill']}` ({mut['action']}): {mut['reason']}")
            if harness_log_lines and os.path.exists(SESSION_HISTORY):
                with open(SESSION_HISTORY, "a", encoding="utf-8") as f:
                    f.write(f"\n## Harness Skill Evolution — {timestamp}\n" + "\n".join(harness_log_lines) + "\n")
        except Exception as e:
            sys.stderr.write(f"[WARN] Failed to append harness entry to session history: {e}\n")

    unprocessed_sessions = glob.glob(os.path.join(SESSION_DIR, 'session_*.md'))
    if len(unprocessed_sessions) >= 5:
        print(f"[PULSE] 5+ sessions detected. Automatically triggering Milestone Synthesis.")
        consolidate_milestone()

    return output_path


def _extract_tagged_observations(text: str) -> Dict[str, List[str]]:
    """Extract and deduplicate tagged observations: [decision], [bugfix], [feature], [open_loop], [lesson]."""
    obs = {
        "decision": [],
        "bugfix": [],
        "feature": [],
        "open_loop": [],
        "lesson": [],
        "other": []
    }
    seen = set()
    for line in text.splitlines():
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            continue
        line_lower = line_clean.lower()
        matched_tag = None
        for tag in ["decision", "bugfix", "feature", "open_loop", "lesson"]:
            if f"[{tag}]" in line_lower or f"[{tag.replace('_', ' ')}]" in line_lower:
                matched_tag = tag
                break
        
        normalized = re.sub(r"\[.*?\]", "", line_clean).strip(" -*•")
        if not normalized or normalized.lower() in seen:
            continue
        seen.add(normalized.lower())

        if matched_tag:
            obs[matched_tag].append(line_clean)
        elif line_clean.startswith(("-", "*", "•")):
            obs["other"].append(line_clean)
    return obs


def _query_orion_db_context() -> Dict[str, Any]:
    """Query orion.db for architectural state, high-traffic pages, relations, and contradictions."""
    db_ctx = {
        "high_traffic_pages": [],
        "recent_relations": [],
        "unresolved_contradictions": []
    }
    try:
        db_path = get_persistence_db_path(WORKSPACE_DIR)
        if os.path.exists(db_path):
            conn = connect_sqlite(db_path)
            c = conn.cursor()
            try:
                c.execute("SELECT path, access_count, importance FROM pages ORDER BY access_count DESC LIMIT 5")
                db_ctx["high_traffic_pages"] = [f"{row[0]} (hits: {row[1]}, imp: {row[2]})" for row in c.fetchall()]
            except Exception:
                pass
            try:
                c.execute("SELECT subject_id, predicate, object_id FROM relations ORDER BY id DESC LIMIT 8")
                db_ctx["recent_relations"] = [f"({r[0]}) -[{r[1]}]-> ({r[2]})" for r in c.fetchall()]
            except Exception:
                pass
            try:
                c.execute("SELECT edge_a_source, edge_a_relation, edge_a_target, evidence FROM contradictions WHERE resolution = 'unresolved' LIMIT 5")
                db_ctx["unresolved_contradictions"] = [f"{r[0]} vs {r[2]} ({r[1]}): {r[3]}" for r in c.fetchall()]
            except Exception:
                pass
            conn.close()
    except Exception as _e:
        _log_telemetry(_e, "reflexion.py:_query_orion_db_context")
    return db_ctx


def consolidate_milestone():
    ensure_dirs()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(MILESTONE_DIR, f"milestone_{timestamp}.md")

    session_files = sorted(glob.glob(os.path.join(SESSION_DIR, 'session_*.md')))
    if not session_files:
        print(f"[SKIP] No unprocessed session pulses found.")
        return None

    raw_content = []
    for f_path in session_files:
        with open(f_path, 'r', encoding='utf-8') as f:
            raw_content.append(f.read())

    all_text = "\n".join(raw_content)
    tagged = _extract_tagged_observations(all_text)
    db_ctx = _query_orion_db_context()

    obs_review_block = ""
    try:
        obs_ledger = ObservationLedger()
        open_obs = obs_ledger.list_observations(status="open")
        total_open = len(open_obs)
        if total_open > 0:
            review_slice = open_obs[:10] if total_open > 15 else open_obs
            rule_groups = {}
            for item in open_obs:
                r_id = item.get("rule_id")
                if r_id:
                    rule_groups.setdefault(r_id, []).append(item)

            obs_lines = [
                f"### Active Observation Bounded Slice Review (Total Open: {total_open}, Reviewing: {len(review_slice)})"
            ]
            for item in review_slice:
                r_id = item.get("rule_id") or "none"
                obs_lines.append(f"- **#{item['id']}** [{item['kind']}] {item['title']} (target: {item['target'] or 'workspace'}, rule: {r_id})")
                if r_id != "none" and len(rule_groups.get(r_id, [])) >= 2:
                    obs_lines.append(f"  - ⚡ **2nd Violation Barrier Escalation**: Rule `{r_id}` has {len(rule_groups[r_id])} open violations. Forced to **Tier-0** AST/assertion check.")

            obs_review_block = "\n".join(obs_lines)
    except Exception as _obs_err:
        _log_telemetry(_obs_err, "reflexion:consolidate_milestone_obs_review")

    nb = None
    try:
        from commands.brain import NanoBrain
        nb = NanoBrain()
    except Exception:
        pass

    synthesized_text = ""
    if nb and getattr(nb, "tier_level", 1) >= 3 and nb.ping():
        try:
            prompt = (
                f"You are the Chief Architectural Consolidator for an autonomous coding ecosystem.\n"
                f"Synthesize the following session pulses and graph context into a high-level milestone report.\n"
                f"Identify architectural shifts, validated bugfixes, and remaining open loops.\n\n"
                f"OBSERVATIONS:\n{json.dumps(tagged, indent=2)}\n\n"
                f"GRAPH CONTEXT:\n{json.dumps(db_ctx, indent=2)}\n\n"
                f"SYNTHESIS REPORT:"
            )
            res = nb.generate(prompt, max_tokens=1000)
            if res and not res.startswith("[DELEGATE_TO_CLOUD]"):
                synthesized_text = res.strip()
        except Exception as _e:
            _log_telemetry(_e, "reflexion.py:nanobrain_synthesize")

    if not synthesized_text:
        enqueue_cloud_handoff(
            "CONSOLIDATE_MILESTONE",
            {
                "timestamp": timestamp,
                "session_count": len(session_files),
                "sessions": [os.path.basename(f) for f in session_files],
                "tagged_observations": tagged,
                "db_context": db_ctx
            },
            reason="requires_tier_3_synthesis"
        )
        lines = []
        for cat, items in tagged.items():
            if items:
                lines.append(f"### {cat.upper().replace('_', ' ')}")
                lines.extend(items[:8])
                lines.append("")
        synthesized_text = "\n".join(lines)

    summary = f"""# Milestone Synthesis — {timestamp}

## Sessions Included ({len(session_files)})
{chr(10).join(f'- {os.path.basename(f)}' for f in session_files)}

## Architectural & Graph Context (orion.db)
### Top Central / Active Files
{chr(10).join(f'- `{p}`' for p in db_ctx['high_traffic_pages']) if db_ctx['high_traffic_pages'] else '- No page traffic recorded yet.'}

### Recent Knowledge Graph Relations
{chr(10).join(f'- {r}' for r in db_ctx['recent_relations']) if db_ctx['recent_relations'] else '- No recent relations recorded.'}

### Active Contradictions
{chr(10).join(f'- ⚠️ {c}' for c in db_ctx['unresolved_contradictions']) if db_ctx['unresolved_contradictions'] else '- Zero unresolved contradictions.'}

## Consolidated Observations & Progress
{synthesized_text}

## Active Observations & Barrier Escalations
{obs_review_block if obs_review_block else '- Zero open observations in active ledger.'}

---
_Generated by Temporal Pulse Engine with Cognitive-Deterministic Verification at {datetime.now().isoformat()}_
"""

    atomic_write_text(output_path, summary)

    # Trigger Generational Rollover of ObservationLedger to maintain lean active context
    try:
        ledger = ObservationLedger()
        rollover_res = ledger.rollover_generation(max_active_keep=10)
        if rollover_res.get("superseded_count", 0) > 0:
            print(f"[PULSE] Observation Generational Rollover complete: {rollover_res['head_generation_id']} (archived {rollover_res['superseded_count']} observations).")
    except Exception as _ro_err:
        _log_telemetry(_ro_err, "consolidate_milestone:rollover_generation")

    for f_path in session_files:
        shutil.move(f_path, os.path.join(SESSION_ARCHIVE, os.path.basename(f_path)))

    print(f"[PULSE] Milestone synthesis generated: {output_path}")

    unprocessed_milestones = glob.glob(os.path.join(MILESTONE_DIR, 'milestone_*.md'))
    if len(unprocessed_milestones) >= 4:
        print(f"[PULSE] 4+ milestones detected. Automatically triggering Epoch Consolidation.")
        consolidate_epoch()

    return output_path


def consolidate_epoch():
    ensure_dirs()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(EPOCH_DIR, f"epoch_{timestamp}.md")

    milestone_files = sorted(glob.glob(os.path.join(MILESTONE_DIR, 'milestone_*.md')))
    if not milestone_files:
        print(f"[SKIP] No unprocessed milestones found.")
        return None

    epoch_raw = []
    for f_path in milestone_files:
        with open(f_path, 'r', encoding='utf-8') as f:
            epoch_raw.append(f.read())

    all_milestone_text = "\n".join(epoch_raw)
    tagged = _extract_tagged_observations(all_milestone_text)
    db_ctx = _query_orion_db_context()

    nb = None
    try:
        from commands.brain import NanoBrain
        nb = NanoBrain()
    except Exception:
        pass

    synthesized_text = ""
    if nb and getattr(nb, "tier_level", 1) >= 3 and nb.ping():
        try:
            prompt = (
                f"You are the Ecosystem Chief Historian.\n"
                f"Synthesize the following 4 milestones and architectural state into an Epoch consolidation report.\n"
                f"Extract candidate canons for promotion into .agents/canons/.\n\n"
                f"MILESTONES SUMMARY:\n{json.dumps(tagged, indent=2)}\n\n"
                f"GRAPH CONTEXT:\n{json.dumps(db_ctx, indent=2)}\n\n"
                f"EPOCH REPORT:"
            )
            res = nb.generate(prompt, max_tokens=1500)
            if res and not res.startswith("[DELEGATE_TO_CLOUD]"):
                synthesized_text = res.strip()
        except Exception as _e:
            _log_telemetry(_e, "reflexion.py:nanobrain_epoch")

    if not synthesized_text:
        enqueue_cloud_handoff(
            "CONSOLIDATE_EPOCH",
            {
                "timestamp": timestamp,
                "milestone_count": len(milestone_files),
                "milestones": [os.path.basename(f) for f in milestone_files],
                "tagged_observations": tagged,
                "db_context": db_ctx
            },
            reason="requires_tier_3_synthesis"
        )
        lines = []
        for cat, items in tagged.items():
            if items:
                lines.append(f"### {cat.upper().replace('_', ' ')}")
                lines.extend(items[:10])
                lines.append("")
        synthesized_text = "\n".join(lines)

    consolidation = f"""# Epoch Consolidation — {timestamp}

## Milestones Included ({len(milestone_files)})
{chr(10).join(f'- {os.path.basename(f)}' for f in milestone_files)}

## Long-Term Architectural State (orion.db)
### Dominant Hubs
{chr(10).join(f'- `{p}`' for p in db_ctx['high_traffic_pages']) if db_ctx['high_traffic_pages'] else '- No page traffic recorded.'}

### Triplet Invariant Graph
{chr(10).join(f'- {r}' for r in db_ctx['recent_relations']) if db_ctx['recent_relations'] else '- No recent relations recorded.'}

## Consolidated Epoch Learnings & Canon Candidates
{synthesized_text}

## Recommended Actions
- [ ] Review patterns for canon promotion (.agents/canons/)
- [ ] Archive session entries older than 90 days
- [ ] Update AGENT_IDENTITY.md with new lessons

---
_Generated by Temporal Pulse Engine with Cognitive-Deterministic Verification at {datetime.now().isoformat()}_
"""

    atomic_write_text(output_path, consolidation)

    for f_path in milestone_files:
        shutil.move(f_path, os.path.join(MILESTONE_ARCHIVE, os.path.basename(f_path)))

    print(f"[PULSE] Epoch consolidation generated: {output_path}")
    return output_path


# ==============================================================================
# SECTION 3: WIKILINK AUTO-INJECTION (LINKIFY)
# ==============================================================================

def get_markdown_files(base_dir):
    md_files = {}
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.md'):
                basename = f[:-3]
                if len(basename) > 4:
                    md_files[basename] = os.path.join(root, f)
    return md_files


GENERIC_IGNORE = {
    'readme', 'skill', 'knowledge', 'security', 'index', 'page', 'matrix',
    'agents', 'foundation', 'rules', 'canons', 'workflows', 'scripts', 'test', 'tests',
    'session-offload', 'blueprint'
}


def linkify_text(text, md_files, current_file_path):
    sorted_names = [n for n in sorted(md_files.keys(), key=len, reverse=True)
                    if n.lower() not in GENERIC_IGNORE and len(n) > 3]

    cur_abs = os.path.abspath(current_file_path)
    valid_names = [n for n in sorted_names if os.path.abspath(md_files[n]) != cur_abs]
    if not valid_names:
        return text

    raw_protected = []
    fm = re.match(r'^---.*?---\s*', text, re.DOTALL)
    if fm:
        raw_protected.append((fm.start(), fm.end()))
    for m in re.finditer(r'```.*?```', text, re.DOTALL):
        raw_protected.append((m.start(), m.end()))
    for m in re.finditer(r'`[^`\n]+`', text):
        raw_protected.append((m.start(), m.end()))
    for m in re.finditer(r'^#+ .*$', text, re.MULTILINE):
        raw_protected.append((m.start(), m.end()))
    for m in re.finditer(r'\[([^\]]+)\]\([^)]+\)', text):
        raw_protected.append((m.start(), m.end()))
    for m in re.finditer(r'\[\[(.*?)\]\]', text):
        raw_protected.append((m.start(), m.end()))

    raw_protected.sort(key=lambda x: x[0])
    merged_protected = []
    for s, e in raw_protected:
        if merged_protected and s <= merged_protected[-1][1]:
            merged_protected[-1] = (merged_protected[-1][0], max(merged_protected[-1][1], e))
        else:
            merged_protected.append((s, e))

    starts = [p[0] for p in merged_protected]
    ends = [p[1] for p in merged_protected]

    def is_protected(pos):
        idx = bisect.bisect_right(starts, pos) - 1
        return idx >= 0 and pos < ends[idx]

    pattern = re.compile(
        r'(?<!\[)(?<!\[\[)(?<!`)(?<!\w)(?<!/)(' +
        '|'.join(re.escape(n) for n in valid_names) +
        r')(?:\.md)?(?!\w)(?!\]\])(?!\])(?!`)(?!\))(?!/)'
    )

    replacements = []
    for m in pattern.finditer(text):
        if not is_protected(m.start()):
            replacements.append((m.start(), m.end(), m.group(1)))

    replacements.sort(key=lambda x: x[0], reverse=True)

    filtered_replacements = []
    last_start = float('inf')
    for r in replacements:
        start, end, matched_text = r
        if end <= last_start:
            filtered_replacements.append(r)
            last_start = start

    new_text = text
    for start, end, matched_text in filtered_replacements:
        new_text = new_text[:start] + f"[[{matched_text}]]" + new_text[end:]

    return new_text


def linkify_workspace():
    target_dirs = [
        os.path.join(BASE_DIR, "rules"),
        os.path.join(BASE_DIR, "skills"),
        os.path.join(WORKSPACE_DIR, "context"),
        os.path.join(WORKSPACE_DIR, ".orion", "sources"),
        os.path.join(WORKSPACE_DIR, ".orion", "matrix")
    ]

    all_md_files = {}
    for d in target_dirs:
        if os.path.exists(d):
            all_md_files.update(get_markdown_files(d))

    if not all_md_files:
        print("[INFO] No markdown files found to linkify.")
        return 0

    modified_count = 0
    error_count = 0
    for d in target_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.endswith('.md'):
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                    except UnicodeDecodeError:
                        try:
                            with open(file_path, 'r', encoding='utf-16') as file:
                                content = file.read()
                        except Exception as e:
                            print(f"[ERROR] Could not read {file_path}: {e}")
                            error_count += 1
                            continue
                    except Exception as e:
                        print(f"[ERROR] Could not read {file_path}: {e}")
                        error_count += 1
                        continue

                    new_content = linkify_text(content, all_md_files, file_path)

                    if new_content != content:
                        try:
                            atomic_write_text(file_path, new_content)
                            modified_count += 1
                            print(f"[LINKIFY] Updated: {os.path.relpath(file_path, WORKSPACE_DIR)}")
                        except Exception as e:
                            print(f"[ERROR] Could not write {file_path}: {e}")
                            error_count += 1

    if error_count > 0:
        print(f"\n[FAIL] Linkify encountered {error_count} error(s). Modified {modified_count} files.")
        return 1
    else:
        print(f"\n[SUCCESS] Linkify complete. Modified {modified_count} files.")
        return 0


# ==============================================================================
# SECTION 4: UNIFIED CLI DISPATCHER
# ==============================================================================

def main():
    if len(sys.argv) >= 2 and sys.argv[1].lower() == "reflexion":
        sys.argv.pop(1)
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print("Usage: reflexion.py <command> [args...]")
        print("\nCommands:")
        print("  record           Record a failure reflection in LEARNINGS.md")
        print("  list             List all recorded self-evolution learnings")
        print("  audit            Audit declarative rule enforcement coverage")
        print("  reflect          Run verbal reflection evaluation loop on test command")
        print("  graduate         Graduate a learning into a staged harness skill")
        print("  detect-recurring Scan learnings for recurring failures and auto-graduate")
        print("  consolidate      Run Temporal Pulse knowledge consolidation (session|milestone|epoch)")
        print("  linkify          Auto-inject wikilinks across context, rules, and skills")
        sys.exit(0 if len(sys.argv) >= 2 and sys.argv[1] in ["-h", "--help"] else 1)

    cmd = sys.argv[1].lower()

    if cmd == "consolidate" or cmd in ["session", "milestone", "epoch", "daily", "weekly", "monthly"]:
        args = sys.argv[2:] if cmd == "consolidate" else sys.argv[1:]
        action = args[0].lower() if args else "session"
        transcript_arg = None
        if "--transcript" in args:
            t_idx = args.index("--transcript")
            if t_idx + 1 < len(args):
                transcript_arg = args[t_idx + 1]
        elif len(args) > 1 and not args[1].startswith("-"):
            transcript_arg = args[1]

        if action in ['session', 'daily']:
            consolidate_session(transcript_arg)
        elif action in ['milestone', 'weekly']:
            consolidate_milestone()
        elif action in ['epoch', 'monthly']:
            consolidate_epoch()
        else:
            print(f"Unknown consolidate action: {action}")
            sys.exit(1)
        return

    if cmd == "linkify":
        code = linkify_workspace()
        sys.exit(code)

    import argparse
    parser = argparse.ArgumentParser(description="VerbalReflectiveLearner & Self-Evolution Engine")
    subparsers = parser.add_subparsers(dest="subcommand")

    rec_parser = subparsers.add_parser("record", help="Record a failure reflection in LEARNINGS.md")
    rec_parser.add_argument("--title", required=True, help="Title of the learning")
    rec_parser.add_argument("--trigger", default="", help="Harness-Zero recognizable trigger condition")
    rec_parser.add_argument("--evidence", default="", help="Harness-Zero concrete trajectory evidence")
    rec_parser.add_argument("--intervention", default="", help="Harness-Zero action recipe / intervention")
    rec_parser.add_argument("--guard", default="", help="Harness-Zero do-not-trigger boundary")
    rec_parser.add_argument("--tier", default="tier-0", choices=["tier-0", "tier-1", "tier-2", "tier-3"], help="Lowest Viable Tier")
    rec_parser.add_argument("--cause", default="", help="Root cause of the failure")
    rec_parser.add_argument("--fix", default="", help="Fix applied")
    rec_parser.add_argument("--rule", default="", help="Self-evolve invariant rule")

    subparsers.add_parser("list", help="List all recorded self-evolution learnings")

    audit_parser = subparsers.add_parser("audit", help="Audit rule enforcement coverage")
    audit_parser.add_argument("--json", action="store_true", help="JSON output")

    reflect_parser = subparsers.add_parser("reflect", help="Run verbal reflection evaluation loop")
    reflect_parser.add_argument("--test", required=True, help="Test command to run")
    reflect_parser.add_argument("--max-trials", type=int, default=3, help="Max trials before circuit breaking")

    grad_parser = subparsers.add_parser("graduate", help="Graduate a learning from LEARNINGS.md into a staged harness skill")
    grad_parser.add_argument("--title", required=True, help="Substring of learning title to graduate")
    grad_parser.add_argument("--name", default="", help="Optional explicit skill name slug")
    grad_parser.add_argument("--json", action="store_true", help="JSON output")

    recur_parser = subparsers.add_parser("detect-recurring", help="Scan learnings for recurring failures and auto-graduate to harness")
    recur_parser.add_argument("--json", action="store_true", help="JSON output")

    obs_add = subparsers.add_parser("observe", help="Record a raw signal observation in OBSERVATIONS.md")
    obs_add.add_argument("--title", default="", help="Title of observation")
    obs_add.add_argument("--backfill", action="store_true", help="Backfill historical observations from memory and session history")
    obs_add.add_argument("--kind", default="improve", choices=["improve", "new-skill", "simplify", "violation", "habit"], help="Observation kind")
    obs_add.add_argument("--target", default="", help="Target file or component")
    obs_add.add_argument("--rule-id", default="", help="Associated rule ID")
    obs_add.add_argument("--scope", default="project", choices=["project", "foundation"], help="Scope")
    obs_add.add_argument("--evidence", default="", help="Evidence or trajectory excerpt")
    obs_add.add_argument("--status", default="open", choices=["open", "parked"], help="Initial status")
    obs_add.add_argument("--parked-until", default="", help="Parked until date (YYYY-MM-DD)")

    obs_list = subparsers.add_parser("observations", help="List observations from OBSERVATIONS.md")
    obs_list.add_argument("--status", choices=["open", "parked", "actioned", "declined", "superseded"], help="Filter by status")
    obs_list.add_argument("--slice", type=int, default=0, help="Limit output count")

    obs_res = subparsers.add_parser("resolve", help="Resolve an observation and move to archive")
    obs_res.add_argument("id", type=int, help="Observation ID to resolve")
    obs_res.add_argument("--resolution", default="actioned", help="Resolution description")
    obs_res.add_argument("--status", default="actioned", choices=["actioned", "declined", "superseded"], help="Target status")

    subparsers.add_parser("habits", help="Mine operator habits and action n-grams into operator_profile.json")

    parsed_args = parser.parse_args(sys.argv[1:])

    engine = ReflexionEngine()

    if parsed_args.subcommand == "record":
        ok = engine.record_learning(
            title=parsed_args.title,
            root_cause=parsed_args.cause,
            fix_applied=parsed_args.fix,
            self_evolve_rule=parsed_args.rule,
            trigger=parsed_args.trigger,
            evidence=parsed_args.evidence,
            intervention=parsed_args.intervention,
            guard=parsed_args.guard,
            resting_tier=parsed_args.tier
        )
        if ok:
            print(f"[REFLECTIVE_LEARNER] Learning recorded in {LEARNINGS_FILE}: '{parsed_args.title}' [Lowest Viable Tier: {parsed_args.tier.upper()}]")
        else:
            print("[ERROR] Failed to record learning.")
            sys.exit(1)

    elif parsed_args.subcommand == "list":
        items = engine.list_learnings()
        print(f"\n🧠 Systemic Learnings Log ({len(items)} entries)")
        print("=" * 60)
        for idx, item in enumerate(items, 1):
            print(f"[{idx:02d}] {item['date']} — {item['title']}")
            print(f"     Cause: {item['root_cause'][:100]}")
            print(f"     Rule : {item['rule'][:100]}\n")

    elif parsed_args.subcommand == "audit":
        compiler = PromptRuleCompiler()
        report = compiler.audit_rule_enforcement()
        if parsed_args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"\n⚖️ Declarative Rule Enforcement Audit (DeclarativePromptPipeline Anti-Graveyard Gate)")
            print("=" * 60)
            print(f"Total Rules Indexed  : {report['total_rules']}")
            print(f"Mechanically Enforced: {report['enforced_count']} ({report['mechanical_coverage_pct']}%)")
            print(f"Advisory Only        : {report['advisory_count']}")
            print(f"Status               : {'PASS' if report['mechanical_coverage_pct'] >= 40.0 else 'WARN'}\n")

    elif parsed_args.subcommand == "reflect":
        loop = ReflexionLoop(max_trials=parsed_args.max_trials)
        code, output = loop.run_evaluator(parsed_args.test)
        if code == 0:
            print(f"[EVALUATOR_PASS] Command passed on initial trial (Exit Code 0).")
        else:
            critique = loop.synthesize_critique(output)
            loop.record_attempt(solution=parsed_args.test, error_output=output, reflection=critique)
            print(f"[EVALUATOR_FAIL] Trial 1 failed (Exit Code {code}).")
            print(f"Critique: {critique}")

    elif parsed_args.subcommand == "graduate":
        res = engine.graduate_learning(
            title_query=parsed_args.title,
            skill_name=parsed_args.name if parsed_args.name else None
        )
        if parsed_args.json:
            print(json.dumps(res, indent=2))
        else:
            if res.get("ok"):
                print(f"[GRADUATION_OK] Graduated '{parsed_args.title}' -> staged skill '{res['skill_name']}'")
                print(f"                Intent ID  : {res['intent_id']}")
                print(f"                Staged Path: {res['staged_path']}")
            else:
                print(f"[GRADUATION_ERROR] {res.get('error', 'Unknown error')}")
                sys.exit(1)

    elif parsed_args.subcommand == "detect-recurring":
        res = engine.detect_and_graduate_recurring()
        if parsed_args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"[RECURRING_SCAN] Found {len(res)} recurring learnings graduated:")
            for item in res:
                print(f"  - Graduated to '{item['skill_name']}' (Intent: {item['intent_id']})")

    elif parsed_args.subcommand == "observe":
        if getattr(parsed_args, "backfill", False):
            res = backfill_historical_observations()
            print(f"[BACKFILL] Completed backfill: {res.get('backfilled_count', 0)} historical observation(s) recorded.")
        else:
            if not parsed_args.title:
                print("[ERROR] --title is required when not using --backfill", file=sys.stderr)
                sys.exit(1)
            ledger = ObservationLedger()
            item = ledger.add_observation(
                title=parsed_args.title,
                kind=parsed_args.kind,
                target=parsed_args.target,
                rule_id=parsed_args.rule_id,
                scope=parsed_args.scope,
                evidence=parsed_args.evidence,
                status=parsed_args.status,
                parked_until=parsed_args.parked_until
            )
            print(f"[OBSERVE] Recorded Observation #{item['id']} [{item['kind']}] '{item['title']}' (fingerprint: {item['fingerprint']})")

    elif parsed_args.subcommand == "observations":
        ledger = ObservationLedger()
        items = ledger.list_observations(status=parsed_args.status, limit=parsed_args.slice if parsed_args.slice > 0 else None)
        print(f"\n🔍 Observation Ledger ({len(items)} active entries)")
        print("=" * 60)
        for item in items:
            print(f"#{item['id']} [{item['status'].upper()}] ({item['kind']}) — {item['title']}")
            if item['target']:
                print(f"     Target : {item['target']}")
            if item['rule_id']:
                print(f"     Rule ID: {item['rule_id']}")
            if item['evidence']:
                print(f"     Evidence: {item['evidence'][:100]}\n")

    elif parsed_args.subcommand == "resolve":
        ledger = ObservationLedger()
        ok = ledger.resolve_observation(parsed_args.id, resolution=parsed_args.resolution, status=parsed_args.status)
        if ok:
            print(f"[RESOLVE] Observation #{parsed_args.id} resolved ({parsed_args.status}) and archived.")
        else:
            print(f"[ERROR] Observation #{parsed_args.id} not found in active ledger.")
            sys.exit(1)

    elif parsed_args.subcommand == "habits":
        res = mine_operator_habits()
        if res.get("ok"):
            print(f"[HABITS] Operator habit profile generated: {res['profile_path']} ({res['patterns_found']} habit patterns found)")
        else:
            print(f"[ERROR] Failed to mine operator habits: {res.get('error')}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
