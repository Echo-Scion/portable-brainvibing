"""
Skill Library Prefix-Cluster Curator & Umbrella Consolidator.
Pure Python 3 standard library implementation.
Detects narrow skill fragmentation and clusters near-duplicate skills under unified umbrella domains.
"""
import os
import re
from typing import Dict, Any, List, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class ConsolidationProposal:
    cluster_prefix: str
    suggested_umbrella: str
    member_skills: List[str]
    descriptions: Dict[str, str]
    category: str = "general"
    rationale: str = ""


class ClusterCurator:
    """
    Analyzes registered skills and generates umbrella consolidation proposals.
    Prevents one-session-one-rule micro-rule fragmentation.
    """

    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir

    def scan_skills(self) -> Dict[str, Dict[str, Any]]:
        """
        Reads all skills in skills_dir and extracts metadata from SKILL.md.
        """
        skills = {}
        if not os.path.exists(self.skills_dir):
            return skills

        for entry in os.listdir(self.skills_dir):
            if entry.startswith(".") or entry == "archive" or entry == ".archive":
                continue
            skill_path = os.path.join(self.skills_dir, entry)
            if not os.path.isdir(skill_path):
                continue

            md_path = os.path.join(skill_path, "SKILL.md")
            desc = ""
            category = "general"
            if os.path.exists(md_path):
                try:
                    with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    from core.scanner import parse_frontmatter
                    fm, _ = parse_frontmatter(content)
                    if fm and "description" in fm and fm["description"]:
                        desc = str(fm["description"]).strip().strip("\"'")
                    if fm and "category" in fm and fm["category"]:
                        category = str(fm["category"]).strip().strip("\"'")
                except Exception as _e:
                    if os.environ.get("ORION_DEBUG"):
                        import sys
                        sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in curator:scan_skills: {_e}\n")

            skills[entry] = {
                "name": entry,
                "path": skill_path,
                "description": desc,
                "category": category
            }
        return skills

    def find_clusters(self, min_cluster_size: int = 2) -> List[ConsolidationProposal]:
        """
        Groups skills by common hyphenated prefix (e.g. 'flutter-auth', 'flutter-nav' -> 'flutter').
        """
        skills = self.scan_skills()
        prefix_groups: Dict[str, List[str]] = {}

        for name in skills:
            parts = name.split("-")
            if len(parts) >= 2:
                prefix = parts[0]
                if len(prefix) >= 3:  # Ignore trivial 1-2 char prefixes
                    prefix_groups.setdefault(prefix, []).append(name)

        proposals = []
        for prefix, members in sorted(prefix_groups.items()):
            if len(members) >= min_cluster_size:
                descs = {m: skills[m]["description"] for m in members}
                categories = [skills[m]["category"] for m in members if skills[m]["category"] != "general"]
                chosen_category = categories[0] if categories else prefix

                proposals.append(
                    ConsolidationProposal(
                        cluster_prefix=prefix,
                        suggested_umbrella=prefix,
                        member_skills=sorted(members),
                        descriptions=descs,
                        category=chosen_category,
                        rationale=f"Cluster has {len(members)} narrow skills sharing prefix '{prefix}-*'. Recommend absorbing into umbrella '{prefix}' with labeled subsections."
                    )
                )

        return proposals
