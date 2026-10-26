"""
Skill Library Prefix-Cluster Curator & Umbrella Consolidator.
Pure Python 3 standard library implementation.
Detects narrow skill fragmentation and clusters near-duplicate skills under unified umbrella domains.
"""
import os
import re
from typing import Dict, Any, List, Set, Tuple
from dataclasses import dataclass, field

try:
    from core.db import log_telemetry as _log_telemetry
except ImportError:
    try:
        from ..db import log_telemetry as _log_telemetry
    except ImportError:
        def _log_telemetry(err=None, context=""):
            pass


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
                    _log_telemetry(_e, "curator:scan_skills")

            skills[entry] = {
                "name": entry,
                "path": skill_path,
                "description": desc,
                "category": category
            }
        return skills

    def find_clusters(self, min_cluster_size: int = 2) -> List[ConsolidationProposal]:
        """
        Groups skills by semantic similarity (via Ollama embeddings if online)
        or shared domain category + description token Jaccard overlap, avoiding naive prefix collisions.
        """
        skills = self.scan_skills()
        proposals = []

        # Tier-1: Use Ollama Embeddings if available to detect true semantic duplication
        try:
            from core.capabilities import resolve_ollama_base_url, get_embedding
            from core.db import cosine_similarity
            host = resolve_ollama_base_url()
            if host and len(skills) >= 2:
                vecs = {}
                for name, meta in skills.items():
                    emb = get_embedding(f"{name}: {meta.get('description', '')}", host=host)
                    if emb:
                        vecs[name] = emb
                visited = set()
                for n1 in sorted(vecs.keys()):
                    if n1 in visited:
                        continue
                    cluster = [n1]
                    for n2 in sorted(vecs.keys()):
                        if n1 != n2 and n2 not in visited:
                            if cosine_similarity(vecs[n1], vecs[n2]) >= 0.82:
                                cluster.append(n2)
                    if len(cluster) >= min_cluster_size:
                        visited.update(cluster)
                        descs = {m: skills[m]["description"] for m in cluster}
                        proposals.append(ConsolidationProposal(
                            cluster_prefix=n1,
                            suggested_umbrella=n1,
                            member_skills=cluster,
                            descriptions=descs,
                            category=skills[n1].get("category", "general"),
                            rationale=f"High semantic embedding similarity (>=0.82) detected via Ollama across {len(cluster)} skills."
                        ))
                if proposals:
                    return proposals
        except Exception as _e:
            _log_telemetry(_e, "curator:find_clusters_ollama")

        # Tier-0 Guarded Fallback: Only group if prefix is not a generic descriptor
        prefix_groups: Dict[str, List[str]] = {}
        generic_prefixes = {"project", "meta", "app", "code", "system", "auto", "strict", "core", "test"}

        for name in skills:
            parts = name.split("-")
            if len(parts) >= 2:
                prefix = parts[0]
                if len(prefix) >= 3 and prefix not in generic_prefixes:
                    prefix_groups.setdefault(prefix, []).append(name)

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

    def propose_siblings(self, skill_name: str) -> List[str]:
        """
        Identifies existing sibling skills sharing prefix families or semantic similarity.
        Prevents micro-skill fragmentation before creating/staging a new skill.
        """
        skills = self.scan_skills()
        if not skills:
            return []

        siblings: Set[str] = set()
        parts = skill_name.split("-")
        prefix = parts[0] if len(parts) >= 2 else skill_name
        generic_prefixes = {"project", "meta", "app", "code", "system", "auto", "strict", "core", "test"}

        # 1. Prefix match if non-generic
        if len(prefix) >= 3 and prefix not in generic_prefixes:
            for existing_name in skills:
                if existing_name != skill_name:
                    if existing_name.startswith(f"{prefix}-") or existing_name == prefix:
                        siblings.add(existing_name)

        # 2. Semantic match if Ollama is available
        try:
            from core.capabilities import resolve_ollama_base_url, get_embedding
            from core.db import cosine_similarity
            host = resolve_ollama_base_url()
            if host:
                target_emb = get_embedding(skill_name, host=host)
                if target_emb:
                    for existing_name, meta in skills.items():
                        if existing_name != skill_name and existing_name not in siblings:
                            desc = meta.get("description", "")
                            existing_emb = get_embedding(f"{existing_name}: {desc}", host=host)
                            if existing_emb and cosine_similarity(target_emb, existing_emb) >= 0.78:
                                siblings.add(existing_name)
        except Exception as _e:
            _log_telemetry(_e, "curator:propose_siblings_ollama")

        # 3. Token-based overlap fallback
        target_tokens = set(re.findall(r"\w+", skill_name.lower()))
        for existing_name in skills:
            if existing_name != skill_name and existing_name not in siblings:
                existing_tokens = set(re.findall(r"\w+", existing_name.lower()))
                overlap = target_tokens.intersection(existing_tokens)
                meaningful_overlap = [t for t in overlap if len(t) >= 4 and t not in generic_prefixes]
                if meaningful_overlap:
                    siblings.add(existing_name)

        return sorted(list(siblings))

