"""
Sovereign Harness Engine Orchestrator & CLI Controller.
Pure Python 3 standard library implementation.
Dispatches admission promotion, lifecycle evaluations, curator cluster folding, and index surfacing.
"""
import os
import sys
import json
import argparse
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
_scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from core.db import atomic_write_text as _atomic_write_text, log_telemetry as _log_telemetry


if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from capture import SecretRedactor, ToolQuantumCapture
    from lifecycle import LifecycleManager, SkillMember, LifecycleResult
    from staging import IntentQueue, StagedIntent, StagingServer
    from curator import ClusterCurator, ConsolidationProposal
    from admission import SovereignPromoter, AdmissionFinding
else:
    from .capture import SecretRedactor, ToolQuantumCapture
    from .lifecycle import LifecycleManager, SkillMember, LifecycleResult
    from .staging import IntentQueue, StagedIntent, StagingServer
    from .curator import ClusterCurator, ConsolidationProposal
    from .admission import SovereignPromoter, AdmissionFinding

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Sovereign foundation root resolution (harness -> core -> scripts -> .agents -> foundation root)
FOUNDATION_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
DEFAULT_SKILLS_DIR = os.path.join(FOUNDATION_ROOT, ".agents", "skills")
DEFAULT_STATE_DIR = os.path.join(FOUNDATION_ROOT, ".orion", "harness")


class HarnessEngine:
    """
    Central controller connecting Capture, Staging, Admission Promoter,
    Lifecycle Governance, and Index Surfacing.
    """

    def __init__(
        self,
        skills_dir: str = DEFAULT_SKILLS_DIR,
        state_dir: str = DEFAULT_STATE_DIR
    ):
        self.skills_dir = skills_dir
        self.state_dir = state_dir
        self.intents_dir = os.path.join(self.state_dir, "intents")

        os.makedirs(self.skills_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)
        os.makedirs(self.intents_dir, exist_ok=True)

        self.queue = IntentQueue(self.intents_dir)
        self.promoter = SovereignPromoter(self.skills_dir)
        self.capture = ToolQuantumCapture(self.state_dir)
        self.curator = ClusterCurator(self.skills_dir)
        self.staging_server = StagingServer(self.queue)

    def _get_request_count(self) -> int:
        req_file = os.path.join(self.state_dir, "requests")
        if os.path.exists(req_file):
            try:
                with open(req_file, "r", encoding="utf-8") as f:
                    return int(f.read().strip())
            except Exception as _e:
                _log_telemetry(_e, "engine:get_request_count")
        return 0

    def increment_request_count(self) -> int:
        req_file = os.path.join(self.state_dir, "requests")
        count = self._get_request_count() + 1
        _atomic_write_text(req_file, str(count))
        return count

    def _surface_new_skill(self, intent: StagedIntent) -> None:
        """Insert one canonical index entry under ## 2. 🛠️ SKILLS after successful skill admission."""
        index_path = os.path.join(FOUNDATION_ROOT, ".agents", "AGENTS_INDEX.md")
        if not os.path.exists(index_path):
            return
        entry = f"- **{intent.name}**: `.agents/skills/{intent.name}/SKILL.md` (promoted by harness)\n"
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()

            if f"`{intent.name}`" in content or f"**{intent.name}**" in content:
                return

            marker = "### Consolidated Tier-3 References"
            if marker in content:
                parts = content.split(marker, 1)
                new_content = parts[0].rstrip() + f"\n{entry}\n" + marker + parts[1]
            elif "## 2. 🛠️ SKILLS" in content:
                parts = content.split("## 2. 🛠️ SKILLS", 1)
                new_content = parts[0] + "## 2. 🛠️ SKILLS" + f"\n{entry}" + parts[1]
            else:
                new_content = content + f"\n{entry}"

            _atomic_write_text(index_path, new_content)
        except OSError as exc:
            raise RuntimeError(f"Unable to update AGENTS_INDEX.md: {exc}") from exc

    def get_live_skills_metadata(self) -> Dict[str, Dict[str, Any]]:
        metadata = {}
        if not os.path.exists(self.skills_dir):
            return metadata

        for name in os.listdir(self.skills_dir):
            if name.startswith(".") or name in ("archive", ".archive"):
                continue
            skill_dir = os.path.join(self.skills_dir, name)
            if not os.path.isdir(skill_dir):
                continue

            sidecar_path = os.path.join(skill_dir, ".sidecar.json")
            sc_data = {
                "name": name,
                "layer": "project",
                "created_by": "unknown",
                "anchor": 0,
                "use": 0,
                "view": 0,
                "patch": 0
            }
            if os.path.exists(sidecar_path):
                try:
                    with open(sidecar_path, "r", encoding="utf-8") as f:
                        sc_data.update(json.load(f))
                except Exception as _e:
                    _log_telemetry(_e, "engine.py:load_sidecar")
            metadata[name] = sc_data
        return metadata

    @staticmethod
    def record_skill_event(skill_name: str, event_type: str = "view", skills_dir: Optional[str] = None) -> None:
        """Increment 'view' or 'use' counter on .agents/skills/<name>/.sidecar.json."""
        if not skill_name:
            return
        try:
            if skills_dir is None:
                from core.paths import get_agents_dir
                skills_dir = os.path.join(str(get_agents_dir()), "skills")
            skill_dir = os.path.join(skills_dir, skill_name)
            if not os.path.isdir(skill_dir):
                return
            sidecar_path = os.path.join(skill_dir, ".sidecar.json")
            sc_data = {
                "name": skill_name,
                "layer": "project",
                "created_by": "unknown",
                "anchor": 0,
                "use": 0,
                "view": 0,
                "patch": 0
            }
            if os.path.exists(sidecar_path):
                try:
                    with open(sidecar_path, "r", encoding="utf-8") as f:
                        sc_data.update(json.load(f))
                except Exception as _e:
                    _log_telemetry(_e, "engine:load_sidecar")
            if event_type == "use":
                sc_data["use"] = sc_data.get("use", 0) + 1
            else:
                sc_data["view"] = sc_data.get("view", 0) + 1
            _atomic_write_text(sidecar_path, json.dumps(sc_data, indent=2))
        except Exception as _e:
            _log_telemetry(_e, "engine:update_skill_stats")

    def promote_pending_queue(self) -> Dict[str, Any]:
        """
        Drains intent queue, validates each intent against the promoter gate,
        commits approved intents, and removes processed queue items.
        """
        pending = self.queue.drain()
        live_skills = self.get_live_skills_metadata()
        current_req = self._get_request_count()

        promoted = []
        rejected = []
        files_to_clear = []

        for fp, intent in pending:
            files_to_clear.append(fp)
            is_valid, findings = self.promoter.validate_intent(intent, live_skills)
            
            if not is_valid:
                rejected.append({
                    "id": intent.id,
                    "name": intent.name,
                    "action": intent.action,
                    "findings": [{"family": f.family, "message": f.message, "rule": f.rule_id} for f in findings]
                })
                continue

            target_skill_md = Path(self.skills_dir) / intent.name / "SKILL.md"
            prev_skill_md = target_skill_md.read_text(encoding="utf-8", errors="ignore") if target_skill_md.exists() else None
            # Pre-mutation snapshot of target skill files for rollback
            skill_dir_path = Path(self.skills_dir) / intent.name
            skill_snapshot: Dict[str, bytes] = {}
            if skill_dir_path.is_dir() and intent.action in ("delete", "remove_file", "patch", "update"):
                for root_s, _, files_s in os.walk(str(skill_dir_path)):
                    for fs in files_s:
                        full_fs = os.path.join(root_s, fs)
                        rel_fs = os.path.relpath(full_fs, str(skill_dir_path)).replace("\\", "/")
                        try:
                            with open(full_fs, "rb") as f_snap:
                                skill_snapshot[rel_fs] = f_snap.read()
                        except Exception:
                            pass

            success, msg = self.promoter.commit_intent(intent, request_anchor=current_req)
            if success:
                verify_ok = True
                verify_err = ""
                try:
                    import subprocess
                    from core.paths import get_workspace_dir
                    orion_bin = os.path.join(str(get_workspace_dir()), ".agents", "scripts", "orion.py")
                    if os.path.exists(orion_bin):
                        proc = subprocess.run(
                            [sys.executable, orion_bin, "verify_agents"],
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            timeout=30,
                            cwd=str(get_workspace_dir())
                        )
                        if proc.returncode != 0:
                            verify_ok = False
                            verify_err = proc.stderr.strip() or proc.stdout.strip()
                except Exception as _ve:
                    _log_telemetry(_ve, "promote_pending_queue:verify_agents")

                if not verify_ok:
                    skill_dir = os.path.join(self.skills_dir, intent.name)
                    if intent.action == "create":
                        if os.path.isdir(skill_dir):
                            for root, dirs, files in os.walk(skill_dir, topdown=False):
                                for f in files:
                                    try:
                                        os.remove(os.path.join(root, f))
                                    except OSError:
                                        pass
                                for d in dirs:
                                    try:
                                        os.rmdir(os.path.join(root, d))
                                    except OSError:
                                        pass
                            try:
                                os.rmdir(skill_dir)
                            except OSError:
                                pass
                    elif skill_snapshot:
                        # Restore full snapshot on failed verification
                        os.makedirs(skill_dir, exist_ok=True)
                        for rel_fs, snap_bytes in skill_snapshot.items():
                            dest_fs = os.path.join(skill_dir, rel_fs)
                            os.makedirs(os.path.dirname(dest_fs), exist_ok=True)
                            try:
                                with open(dest_fs, "wb") as f_rest:
                                    f_rest.write(snap_bytes)
                            except Exception:
                                pass
                    elif prev_skill_md is not None and target_skill_md.exists():
                        try:
                            _atomic_write_text(str(target_skill_md), prev_skill_md)
                        except Exception:
                            pass
                    rejected.append({
                        "id": intent.id,
                        "name": intent.name,
                        "action": intent.action,
                        "findings": [{"family": "verification", "message": f"Post-promotion mechanical verification failed: {verify_err[:200]}", "rule": "HARNESS-VERIFY-01"}]
                    })
                    continue

                if intent.action == "create":
                    self._surface_new_skill(intent)
                promoted.append({
                    "id": intent.id,
                    "name": intent.name,
                    "action": intent.action,
                    "message": msg
                })
                # Update live skills state
                live_skills[intent.name] = {"name": intent.name, "created_by": "agent"}
            else:
                rejected.append({
                    "id": intent.id,
                    "name": intent.name,
                    "action": intent.action,
                    "findings": [{"family": "commit", "message": msg, "rule": "HARNESS-CMT-01"}]
                })

        # Clear processed intents
        self.queue.clear(files_to_clear)

        if promoted:
            try:
                from commands.brain import compile_skill_routes
                compile_skill_routes()
            except Exception as _csr_err:
                _log_telemetry(_csr_err, "promote_pending_queue:compile_skill_routes")

        return {
            "status": "success",
            "promoted": promoted,
            "rejected": rejected,
            "total_processed": len(pending)
        }

    def evaluate_lifecycle(
        self,
        maturity: int = 100,
        capacity: int = 50,
        execute_archive: bool = True
    ) -> Dict[str, Any]:
        """
        Runs opportunity-relative lifecycle evaluation and lazily archives dormant skills.
        """
        live_metadata = self.get_live_skills_metadata()
        members = list(live_metadata.values())
        request_count = self._get_request_count()

        result = LifecycleManager.evaluate(
            members=members,
            request_count=request_count,
            maturity=maturity,
            capacity=capacity
        )

        archived_files = []
        if execute_archive and result.archived:
            archived_files = LifecycleManager.execute_archival(
                skills_dir=self.skills_dir,
                skill_names=result.archived
            )

        return {
            "request_count": request_count,
            "total_members": len(members),
            "probation_count": len(result.probation),
            "retained_count": len(result.retained),
            "archived_count": len(archived_files),
            "archived_skills": archived_files,
            "probation_skills": result.probation,
            "rates": result.rates
        }

    def build_session_index(self, max_desc_chars: int = 80) -> str:
        """
        Builds a compact grouped index of all live skills for session startup injection.
        """
        skills = self.curator.scan_skills()
        if not skills:
            return ""

        by_category: Dict[str, List[Tuple[str, str]]] = {}
        for name, data in sorted(skills.items()):
            cat = data.get("category", "general")
            desc = data.get("description", "")
            if len(desc) > max_desc_chars:
                desc = desc[:max_desc_chars - 3] + "..."
            by_category.setdefault(cat, []).append((name, desc))

        lines = ["# 🛡️ SOVEREIGN SKILL INDEX"]
        for cat, items in sorted(by_category.items()):
            lines.append(f"\n### {cat.upper()}")
            for name, desc in items:
                lines.append(f"- **{name}**: {desc}")
        lines.append("")
        return "\n".join(lines)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception as _e:
            _log_telemetry(_e, "engine.py:reconfigure")

    parser = argparse.ArgumentParser(description="Sovereign Harness Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Status
    subparsers.add_parser("status", help="Display current harness status")

    # Promote
    subparsers.add_parser("promote", help="Drain staging queue and promote admitted skills")

    # Lifecycle
    lc_parser = subparsers.add_parser("lifecycle", help="Run lazy opportunity-relative lifecycle evaluation")
    lc_parser.add_argument("--maturity", type=int, default=100, help="Probation maturity threshold")
    lc_parser.add_argument("--capacity", type=int, default=50, help="Capacity limit for mature skills")
    lc_parser.add_argument("--dry-run", action="store_true", help="Evaluate without executing physical directory moves")

    # Curate
    subparsers.add_parser("curate", help="Scan skills for prefix clusters and propose umbrella consolidations")

    # Index
    subparsers.add_parser("index", help="Generate compact categorized skill index for session injection")

    # Serve MCP
    subparsers.add_parser("serve", help="Run stdio JSON-RPC 2.0 MCP server for stage_skill")

    # Record Tool Call (Quantum Counter)
    rec_tool_parser = subparsers.add_parser("record-tool", help="Record a tool invocation in the session quantum counter")
    rec_tool_parser.add_argument("--tool", default="generic", help="Tool name")
    rec_tool_parser.add_argument("--session", default="default_session", help="Session or conversation ID")

    args = parser.parse_args()
    engine = HarnessEngine()

    if args.command == "status":
        live = engine.get_live_skills_metadata()
        pending = engine.queue.peek()
        reqs = engine._get_request_count()
        print("\n🛡️ Sovereign Skill Harness Status")
        print("=" * 50)
        print(f"Total Live Skills : {len(live)}")
        print(f"Pending in Queue  : {len(pending)}")
        print(f"Layer Requests    : {reqs}")
        print(f"Skills Root       : {engine.skills_dir}")
        print(f"State Root        : {engine.state_dir}\n")

    elif args.command == "promote":
        res = engine.promote_pending_queue()
        print(f"\n✨ Promoter Admission Drain: {res['total_processed']} processed")
        print(f"   Admitted : {len(res['promoted'])}")
        print(f"   Rejected : {len(res['rejected'])}")
        for p in res["promoted"]:
            print(f"   [+PASS] {p['action']} {p['name']}: {p['message']}")
        for r in res["rejected"]:
            print(f"   [-FAIL] {r['action']} {r['name']}: {r['findings']}")
        print()

    elif args.command == "lifecycle":
        res = engine.evaluate_lifecycle(
            maturity=args.maturity,
            capacity=args.capacity,
            execute_archive=not args.dry_run
        )
        print(f"\n⚖️ Lifecycle Governance Report (Requests: {res['request_count']})")
        print(f"   Probation Protected : {res['probation_count']}")
        print(f"   Retained Mature     : {res['retained_count']}")
        print(f"   Archived Dormant    : {res['archived_count']}")
        if res["archived_skills"]:
            print(f"   Archived to .archive: {', '.join(res['archived_skills'])}")
        print()

    elif args.command == "curate":
        proposals = engine.curator.find_clusters()
        print(f"\n🧩 Cluster Curator: Found {len(proposals)} umbrella opportunities")
        for prop in proposals:
            print(f"   Cluster '{prop.cluster_prefix}-*': {len(prop.member_skills)} members -> umbrella '{prop.suggested_umbrella}'")
            print(f"   Members : {', '.join(prop.member_skills)}")
            print(f"   Action  : {prop.rationale}\n")

    elif args.command == "index":
        print(engine.build_session_index())

    elif args.command == "serve":
        engine.staging_server.run_stdio_mcp()

    elif args.command == "record-tool":
        should_reflect, count = engine.capture.record_tool_call(args.session, args.tool, {})
        print(f"[HARNESS_CAPTURE] Session: {args.session} | Tool: {args.tool} | Calls: {count} | Reflect: {should_reflect}")
        if should_reflect:
            print(f"[QUANTUM_THRESHOLD_CROSSED] Session reached {engine.capture.quantum_threshold} tool calls. Triggering reflection.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
