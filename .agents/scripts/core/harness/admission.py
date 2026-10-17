"""
Sovereign Promoter & Deterministic Admission Gatekeeper.
Pure Python 3 standard library implementation.
Validates proposed skill changes across 6 deterministic classes in memory before atomic commit.
"""
import os
import sys
import re
import ast
import json
import hashlib
import uuid
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from capture import SecretRedactor
    from staging import StagedIntent
else:
    from .capture import SecretRedactor
    from .staging import StagedIntent

try:
    from core.db import atomic_write_text as _atomic_write_text, log_telemetry as _log_telemetry
except ImportError:
    from ..db import atomic_write_text as _atomic_write_text, log_telemetry as _log_telemetry

SUBFILE_DIRS = ("references", "scripts", "examples", "resources", "templates", "assets")
ABS_PATH_RE = re.compile(r"(?:/home/|/Users/|/root/)[^\s`)\]]+|[A-Za-z]:\\[^\s`)\]]+")
PLACEHOLDER_RE = re.compile(r"\b(TODO|FIXME|XXX):|<(?:TODO|FIXME|XXX|TBD|PLACEHOLDER|REPLACE[_ ]?ME|INSERT[_ ]?HERE|FILL[_ ]?IN)>")
TRIGGER_CUE_RE = re.compile(r"(?i)\bwhen\b|[\"'][^\"']+[\"']|`[^`]+`")


@dataclass
class AdmissionFinding:
    family: str
    message: str
    rule_id: str



class SovereignPromoter:
    """
    Admission Controller and Atomic Committer.
    Ensures that self-authored skills satisfy structural, security, and quality gates.
    """

    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        os.makedirs(self.skills_dir, exist_ok=True)

    def validate_intent(
        self,
        intent: StagedIntent,
        live_skills: Dict[str, Any]
    ) -> Tuple[bool, List[AdmissionFinding]]:
        """
        Runs the 6 deterministic in-memory validation classes on an intent.
        """
        findings: List[AdmissionFinding] = []

        action = intent.action
        name = intent.name
        level = intent.level
        body = intent.body or ""

        # --- CLASS 1: Safety & Secrets Check ---
        redacted_body = SecretRedactor.redact_text(body)
        if redacted_body != body:
            findings.append(AdmissionFinding("safety", "Intent body contains unredacted credentials or API keys", "HARNESS-SEC-01"))

        if intent.files:
            for rel_path, file_content in intent.files.items():
                if SecretRedactor.redact_text(file_content) != file_content:
                    findings.append(AdmissionFinding("safety", f"Subfile {rel_path} contains unredacted credentials", "HARNESS-SEC-01"))
                if rel_path.endswith(".py"):
                    try:
                        ast.parse(file_content, filename=rel_path)
                    except SyntaxError as e:
                        findings.append(AdmissionFinding("safety", f"Subfile {rel_path} has Python syntax error: {e}", "HARNESS-SYN-01"))

        # --- CLASS 2: Structure & Frontmatter (Antigravity Gold Standard: docs/skills.md) ---
        if action in ("create", "update"):
            from core.scanner import parse_frontmatter
            fm, _ = parse_frontmatter(body)
            if not fm:
                findings.append(AdmissionFinding("structure", "Missing required YAML frontmatter (--- ... ---)", "HARNESS-STR-01"))
            else:
                raw_desc = fm.get("description", "")
                desc_text = " ".join(str(raw_desc).split()) if raw_desc else ""
                if not desc_text:
                    findings.append(AdmissionFinding("structure", "Frontmatter must include non-empty description", "HARNESS-STR-02"))
                elif not TRIGGER_CUE_RE.search(desc_text):
                    findings.append(AdmissionFinding("structure", "Description must state WHEN to trigger (e.g. 'Use when...' or quote trigger words)", "HARNESS-STR-03"))

        # --- CLASS 3: LED Evidence & Provenance ---
        if not intent.reason or not intent.reason.strip():
            findings.append(AdmissionFinding("provenance", "Missing required ledger reason", "HARNESS-LED-01"))
        if not intent.evidence or not intent.evidence.strip():
            findings.append(AdmissionFinding("provenance", "Missing required verbatim evidence slice quote", "HARNESS-LED-02"))

        # --- CLASS 4: Completeness & Progressive Disclosure Threshold ---
        if action in ("create", "update"):
            total_lines = len(body.splitlines())
            if total_lines > 500:
                findings.append(AdmissionFinding("altitude", f"Progressive disclosure cap exceeded: {total_lines} lines (max 500). Hoist detail into references/", "HARNESS-ALT-01"))
            if PLACEHOLDER_RE.search(body):
                findings.append(AdmissionFinding("completeness", "Body contains unexpanded placeholder (TODO/FIXME/XXX)", "HARNESS-CMP-01"))

        # --- CLASS 5: Path Escapes & Absolute Path Denial ---
        if level == "global" and action in ("create", "update"):
            if ABS_PATH_RE.search(body):
                findings.append(AdmissionFinding("portability", "Global skills cannot contain absolute host filesystem paths", "HARNESS-PRT-01"))

        if intent.files:
            for rel_path in intent.files:
                parts = rel_path.replace("\\", "/").split("/")
                if ".." in parts or rel_path.startswith("/"):
                    findings.append(AdmissionFinding("security", f"Directory traversal in subfile path: {rel_path}", "HARNESS-SEC-02"))
                if not any(rel_path.startswith(d + "/") for d in SUBFILE_DIRS):
                    findings.append(AdmissionFinding("structure", f"Subfile must reside in {SUBFILE_DIRS}, got: {rel_path}", "HARNESS-STR-04"))
                if rel_path not in body and not rel_path.replace("\\", "/") in body:
                    findings.append(AdmissionFinding("completeness", f"Carried subfile '{rel_path}' is never referenced in SKILL.md body", "HARNESS-REF-01"))

        # --- CLASS 6: Self-Authored Marker & Umbrella Verification ---
        if action == "delete" and intent.absorbed_into:
            target = intent.absorbed_into
            if target not in live_skills:
                findings.append(AdmissionFinding("curation", f"Fold target umbrella '{target}' does not exist in live skills", "HARNESS-CUR-01"))

        return len(findings) == 0, findings

    def commit_intent(
        self,
        intent: StagedIntent,
        request_anchor: int = 0
    ) -> Tuple[bool, str]:
        """
        Executes atomic filesystem writes and sidecar updates upon admission approval.
        """
        skill_dir = os.path.join(self.skills_dir, intent.name)
        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        sidecar_path = os.path.join(skill_dir, ".sidecar.json")
        ledger_path = os.path.join(skill_dir, ".ledger.jsonl")

        if intent.action == "create":
            os.makedirs(skill_dir, exist_ok=True)
            refs_dir = os.path.join(skill_dir, "references")
            os.makedirs(refs_dir, exist_ok=True)

            # 1. Write support subfiles first
            if intent.files:
                for rel_path, content in intent.files.items():
                    sub_path = os.path.join(skill_dir, rel_path)
                    os.makedirs(os.path.dirname(sub_path), exist_ok=True)
                    tmp_sub = f"{sub_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}"
                    with open(tmp_sub, "w", encoding="utf-8") as f:
                        f.write(content)
                    os.replace(tmp_sub, sub_path)

            # 2. Materialize evidence slice
            ev_hash = hashlib.sha256(intent.evidence.encode("utf-8")).hexdigest()[:8]
            ev_filename = f"evidence-{ev_hash}.md"
            ev_path = os.path.join(refs_dir, ev_filename)
            _atomic_write_text(ev_path, f"# Evidence Trace [{ev_hash}]\n\n{intent.evidence}\n")

            # 3. Commit SKILL.md atomically
            tmp_md = f"{skill_md_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}"
            with open(tmp_md, "w", encoding="utf-8") as f:
                f.write(intent.body or "")
            os.replace(tmp_md, skill_md_path)

            # 4. Stamp sidecar
            sidecar_data = {
                "name": intent.name,
                "layer": intent.level,
                "created_by": "agent",
                "anchor": request_anchor,
                "use": 0,
                "view": 0,
                "patch": 0
            }
            _atomic_write_text(sidecar_path, json.dumps(sidecar_data, indent=2))

            # 5. Append ledger entry
            ledger_entry = {
                "action": "create",
                "reason": intent.reason,
                "evidence": f"references/{ev_filename}",
                "level": intent.level
            }
            with open(ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ledger_entry) + "\n")

            return True, f"Created skill {intent.name}"

        elif intent.action == "patch":
            if not os.path.exists(skill_md_path):
                return False, f"Target skill {intent.name} does not exist"

            with open(skill_md_path, "r", encoding="utf-8") as f:
                live_text = f.read()

            if not intent.old_string or intent.old_string not in live_text:
                return False, "Target old_string not found in SKILL.md"

            count = live_text.count(intent.old_string)
            if count > 1:
                return False, f"old_string matches {count} times (must match uniquely)"

            new_text = live_text.replace(intent.old_string, intent.new_string or "")

            tmp_md = f"{skill_md_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}"
            with open(tmp_md, "w", encoding="utf-8") as f:
                f.write(new_text)
            os.replace(tmp_md, skill_md_path)

            # Materialize evidence
            refs_dir = os.path.join(skill_dir, "references")
            os.makedirs(refs_dir, exist_ok=True)
            ev_hash = hashlib.sha256(intent.evidence.encode("utf-8")).hexdigest()[:8]
            ev_filename = f"evidence-{ev_hash}.md"
            ev_path = os.path.join(refs_dir, ev_filename)
            _atomic_write_text(ev_path, f"# Evidence Trace [{ev_hash}]\n\n{intent.evidence}\n")

            # Update sidecar patch counter
            if os.path.exists(sidecar_path):
                try:
                    with open(sidecar_path, "r", encoding="utf-8") as f:
                        sc = json.load(f)
                    sc["patch"] = sc.get("patch", 0) + 1
                    _atomic_write_text(sidecar_path, json.dumps(sc, indent=2))
                except Exception as _e:
                    _log_telemetry(_e, "admission:update_sidecar")

            # Append ledger
            ledger_entry = {
                "action": "patch",
                "reason": intent.reason,
                "evidence": f"references/{ev_filename}"
            }
            with open(ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ledger_entry) + "\n")

            return True, f"Patched skill {intent.name}"

        elif intent.action == "delete":
            if not os.path.exists(skill_dir):
                return False, f"Target skill {intent.name} does not exist"

            # Append retirement ledger entry
            ledger_entry = {
                "action": "delete",
                "reason": intent.reason,
                "evidence": intent.evidence,
                "absorbed_into": intent.absorbed_into or ""
            }
            try:
                with open(ledger_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(ledger_entry) + "\n")
            except Exception as _e:
                _log_telemetry(_e, "admission.py:write_delete_ledger")

            archive_dir = os.path.join(self.skills_dir, ".archive")
            os.makedirs(archive_dir, exist_ok=True)
            dst = os.path.join(archive_dir, intent.name)
            
            counter = 1
            final_dst = dst
            while os.path.exists(final_dst):
                final_dst = f"{dst}_{counter}"
                counter += 1

            os.replace(skill_dir, final_dst)
            return True, f"Archived skill {intent.name} to {final_dst}"

        elif intent.action == "update":
            if not os.path.exists(skill_dir):
                return False, f"Target skill {intent.name} does not exist"

            # 1. Update SKILL.md if body provided
            if intent.body:
                tmp_md = f"{skill_md_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}"
                with open(tmp_md, "w", encoding="utf-8") as f:
                    f.write(intent.body)
                os.replace(tmp_md, skill_md_path)

            # 2. Update/create subfiles
            if intent.files:
                for rel_path, content in intent.files.items():
                    clean_rel = os.path.normpath(rel_path).replace("\\", "/")
                    if clean_rel.startswith("../") or clean_rel.startswith("/") or ".." in clean_rel.split("/"):
                        return False, f"Path traversal attempt in subfile: {rel_path}"
                    sub_path = os.path.join(skill_dir, clean_rel)
                    os.makedirs(os.path.dirname(sub_path), exist_ok=True)
                    tmp_sub = f"{sub_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}"
                    with open(tmp_sub, "w", encoding="utf-8") as f:
                        f.write(content)
                    os.replace(tmp_sub, sub_path)

            # 3. Materialize evidence
            refs_dir = os.path.join(skill_dir, "references")
            os.makedirs(refs_dir, exist_ok=True)
            ev_hash = hashlib.sha256(intent.evidence.encode("utf-8")).hexdigest()[:8]
            ev_filename = f"evidence-{ev_hash}.md"
            ev_path = os.path.join(refs_dir, ev_filename)
            _atomic_write_text(ev_path, f"# Evidence Trace [{ev_hash}]\n\n{intent.evidence}\n")

            # 4. Update sidecar patch counter
            if os.path.exists(sidecar_path):
                try:
                    with open(sidecar_path, "r", encoding="utf-8") as f:
                        sc = json.load(f)
                    sc["patch"] = sc.get("patch", 0) + 1
                    _atomic_write_text(sidecar_path, json.dumps(sc, indent=2))
                except Exception as _e:
                    _log_telemetry(_e, "admission:update_sidecar")

            # 5. Append ledger
            ledger_entry = {
                "action": "update",
                "reason": intent.reason,
                "evidence": f"references/{ev_filename}"
            }
            with open(ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ledger_entry) + "\n")

            return True, f"Updated skill {intent.name}"

        elif intent.action == "remove_file":
            if not os.path.exists(skill_dir):
                return False, f"Target skill {intent.name} does not exist"

            target_rel = intent.old_string or (list(intent.files.keys())[0] if intent.files else None)
            if not target_rel:
                return False, "Target relative file path not specified in old_string or files"

            clean_rel = os.path.normpath(target_rel).replace("\\", "/")
            if clean_rel.startswith("../") or clean_rel.startswith("/") or ".." in clean_rel.split("/"):
                return False, f"Path traversal attempt in remove_file: {target_rel}"

            if not (clean_rel.startswith("references/") or clean_rel.startswith("scripts/")):
                return False, f"remove_file only permitted within references/ or scripts/: {clean_rel}"

            target_file_path = os.path.join(skill_dir, clean_rel)
            if not os.path.exists(target_file_path):
                return False, f"File to remove not found: {clean_rel}"

            os.remove(target_file_path)

            if os.path.exists(sidecar_path):
                try:
                    with open(sidecar_path, "r", encoding="utf-8") as f:
                        sc = json.load(f)
                    sc["patch"] = sc.get("patch", 0) + 1
                    _atomic_write_text(sidecar_path, json.dumps(sc, indent=2))
                except Exception as _e:
                    _log_telemetry(_e, "admission:remove_file_sidecar")

            ledger_entry = {
                "action": "remove_file",
                "file": clean_rel,
                "reason": intent.reason,
                "evidence": intent.evidence
            }
            with open(ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ledger_entry) + "\n")

            return True, f"Removed subfile {clean_rel} from skill {intent.name}"

        return False, f"Unsupported action: {intent.action}"
