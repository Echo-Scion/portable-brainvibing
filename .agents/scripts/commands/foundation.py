import os
import shutil
import argparse
import re
import json
import sys
import subprocess

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


AI_CONFIGS = {
    "gemini": {"template": "AGENTS.template.md", "target_dir": "", "target_path": "GEMINI.md", "format": "md"},
    "copilot": {"template": "AGENTS.template.md", "target_dir": ".github", "target_path": "copilot-instructions.md", "format": "md"},
    "cursor": {"template": "AGENTS.template.md", "target_dir": "", "target_path": ".cursorrules", "format": "md"},
    "windsurf": {"template": "AGENTS.template.md", "target_dir": "", "target_path": ".windsurfrules", "format": "md"},
    "cline": {"template": "AGENTS.template.md", "target_dir": "", "target_path": ".clinerules", "format": "md"},
    "claude": {"template": "AGENTS.template.md", "target_dir": "", "target_path": "CLAUDE.md", "format": "md"}
}

def get_ecosystem_config(foundation_dir, framework):
    return {}

def resolve_templates(target_dir, manifest, target_files=None):
    framework = manifest.get("framework", "")
    language = manifest.get("language", "")
    
    if target_files is None:
        target_files = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".md"):
                    target_files.append(os.path.join(root, file))
    else:
        target_files = [os.path.join(target_dir, f) for f in target_files]
        
    for filepath in target_files:
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = content
            if framework:
                new_content = new_content.replace("{{FRAMEWORK}}", framework)
            if language:
                new_content = new_content.replace("{{LANGUAGE}}", language)
                
            if new_content != content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
        except Exception as e:
            print(f"    [WARNING] Failed to resolve templates in {filepath}: {e}")

def get_foundation_path(target_root):
    marker = os.path.join(target_root, ".agents", ".foundation_path")
    if os.path.exists(marker):
        with open(marker, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def load_deployed_ais(target_root):
    marker = os.path.join(target_root, ".agents", ".deployed_ais")
    if os.path.exists(marker):
        try:
            with open(marker, "r", encoding="utf-8") as f:
                return json.load(f).get("deployed_ais", [])
        except Exception:
            pass
    return None

def smart_merge_config(template_content, target_path, project_name, fmt, dry_run, manifest):
    content = template_content.replace("{project_name}", project_name)
    if manifest:
        if manifest.get("framework"):
            content = content.replace("{{FRAMEWORK}}", manifest.get("framework"))
        if manifest.get("language"):
            content = content.replace("{{LANGUAGE}}", manifest.get("language"))
    
    merge_status = "Deployed (Fresh)"
    
    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            old_content = f.read()
            
        if not dry_run:
            shutil.copy2(target_path, target_path + ".bak")
            
        marker = "<!-- END FOUNDATION MANDATES -->"
        idx = old_content.find(marker)
        if idx != -1:
            user_content = old_content[idx + len(marker):].strip()
            idx_new = content.find(marker)
            if idx_new != -1:
                base_new = content[:idx_new + len(marker)]
                content = base_new + "\n\n" + user_content + "\n"
                merge_status = "Merged (Preserved user config)"
            else:
                content += "\n\n" + user_content + "\n"
                merge_status = "Merged (Preserved user config, marker missing in template)"
        else:
            merge_status = "Updated (No marker found in old file)"

    if not dry_run:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
    return content, merge_status

# Folders that represent "The Brain" and should evolve
EVOLVABLE_FOLDERS = ["skills", "rules", "workflows", "canons", "templates", "scripts", "evals", "docs", "hooks"]
ROOT_SYNC_FILES = ["DEPLOY_ME.md", "AGENTS_INDEX.md"]
SEED_FILES = [".agents/LEARNINGS.md", "MEMORY.md"]
VERSION_BUMP_FILES = {"SKILL.md"}
BLACKLIST = {
    "local", "tasks", "personal", "debug_scripts",
    "pull_planning_context.py", ".git", "node_modules",
    "__pycache__", "vitals", "MEMORY.md", "SAAS_MEMORY.md",
    "EVOLUTION_LOG.jsonl"
}

# === DEPLOY ===


def cmd_deploy(args):
    # args.target, args.framework, args.language, args.dry_run
    target_dir = os.path.abspath(args.target)
    foundation_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    target_agents_dir = os.path.join(target_dir, ".agents")
    
    if args.dry_run:
        print(f"[DRY RUN] Deploying Foundation to: {target_dir}")
        print(f"[DRY RUN] Framework: {args.framework}, Language: {args.language}")
    else:
        print(f"Deploying Foundation to: {target_dir}")
        print(f"Framework: {args.framework}, Language: {args.language}")

    os.makedirs(target_agents_dir, exist_ok=True)
    
    manifest_path = os.path.join(target_agents_dir, ".project_manifest.json")
    manifest = {
        "framework": args.framework,
        "language": args.language,
        "ecosystem": get_ecosystem_config(foundation_dir, args.framework)
    }
    
    if not args.dry_run:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"  -> Created {manifest_path}")
    else:
        print(f"  [SIMULATED] -> Created {manifest_path} with ecosystem variables")

    marker_path = os.path.join(target_agents_dir, ".foundation_path")
    if not args.dry_run:
        with open(marker_path, "w", encoding="utf-8") as f:
            f.write(foundation_dir)
        print(f"  -> Created {marker_path}")
    else:
        print(f"  [SIMULATED] -> Created {marker_path}")

    for folder in EVOLVABLE_FOLDERS:
        src = os.path.join(foundation_dir, ".agents", folder)
        dest = os.path.join(target_agents_dir, folder)
        if os.path.exists(src):
            if not args.dry_run:
                shutil.copytree(src, dest, dirs_exist_ok=True)
                resolve_templates(dest, manifest)
            else:
                print(f"  [SIMULATED] -> Copied & Resolved Templates for {folder}/")

    for root_file in ROOT_SYNC_FILES:
        src_root = os.path.join(foundation_dir, ".agents", root_file)
        dest_root = os.path.join(target_agents_dir, root_file)
        if os.path.exists(src_root):
            if not args.dry_run:
                shutil.copy2(src_root, dest_root)
                resolve_templates(target_agents_dir, manifest, target_files=[root_file])
            else:
                print(f"  [SIMULATED] -> Copied {root_file}")

    for seed_file in SEED_FILES:
        src_seed = os.path.join(foundation_dir, seed_file)
        if seed_file.startswith(".agents/"):
            dest_seed = os.path.join(target_agents_dir, seed_file.replace(".agents/", ""))
        else:
            dest_seed = os.path.join(target_dir, seed_file)
            
        if os.path.exists(src_seed):
            if not os.path.exists(dest_seed):
                if not args.dry_run:
                    parent_dir = os.path.dirname(dest_seed)
                    if parent_dir:
                        os.makedirs(parent_dir, exist_ok=True)
                    shutil.copy2(src_seed, dest_seed)
                    if seed_file.startswith(".agents/"):
                        resolve_templates(target_agents_dir, manifest, target_files=[os.path.basename(seed_file)])
                    else:
                        resolve_templates(target_dir, manifest, target_files=[os.path.basename(seed_file)])
                    print(f"  -> Seeded {seed_file}")
                else:
                    print(f"  [SIMULATED] -> Seeded {seed_file}")
            else:
                if not args.dry_run:
                    print(f"  -> Preserved existing {seed_file}")

    template_dir = os.path.join(foundation_dir, ".agents", "templates")
    if os.path.exists(template_dir):
        if not args.dry_run:
            target_template_dir = os.path.join(target_agents_dir, "templates")
            os.makedirs(target_template_dir, exist_ok=True)
            ai_brands_path = os.path.join(foundation_dir, ".agents", "canons", "global", "ai_brands.json")
            if os.path.exists(ai_brands_path):
                with open(ai_brands_path, "r", encoding="utf-8") as f:
                    ai_brands = json.load(f)
                
                selected_ais = list(ai_brands.keys()) if getattr(args, "ai", "gemini").lower() == "all" else getattr(args, "ai", "gemini").split(",")
                deployed_ais_list = []
                
                for ai_name, brand in ai_brands.items():
                    if ai_name not in selected_ais:
                        continue
                    
                    deployed_ais_list.append(ai_name)
                    template_name = brand.get("template")
                    target_filename = brand.get("target_path")
                    
                    src_template = os.path.join(template_dir, template_name)
                    dest_template = os.path.join(target_template_dir, template_name)
                    
                    if os.path.exists(src_template):
                        shutil.copy2(src_template, dest_template)
                        resolve_templates(target_template_dir, manifest, target_files=[template_name])
            else:
                print("    [WARNING] ai_brands.json not found. Skipping root AI config propagation.")
            
            try:
                deployed_file = os.path.join(target_agents_dir, ".deployed_ais")
                project_name = os.path.basename(os.path.abspath(target_dir))
                with open(deployed_file, "w", encoding="utf-8") as df:
                    json.dump({
                        "project_name": project_name, 
                        "deployed_ais": deployed_ais_list,
                        "sync_results": {ai: {"status": "SUCCESS", "message": "Deployed"} for ai in deployed_ais_list}
                    }, df, indent=2)
            except Exception as e:
                print(f"    [WARNING] Could not write .deployed_ais: {e}")
                
            if not args.dry_run and deployed_ais_list:
                sync_ai_configs(target_dir, selected_ais=deployed_ais_list, dry_run=args.dry_run)
                
        else:
            print("  [SIMULATED] -> Processed Templates and propagated root AI configs")

    if not args.dry_run:
        print("  -> Initializing Orion Brain Graph...")
        orion_script = os.path.join(foundation_dir, ".agents", "scripts", "orion.py")
        if os.path.exists(orion_script):
            try:
                subprocess.run(["python", orion_script, "orion_ops", "init"], cwd=target_dir, check=True)
            except Exception as e:
                print(f"    [WARNING] Failed to initialize Orion Brain Graph: {e}")
        else:
            print(f"    [WARNING] orion.py not found at {orion_script}")

    print("\nDeployment Complete!")
    print("AI Agents in the target project are now connected to the Foundation.")
    print("⚡ [RECOMMENDED TIER: BUDGET] — Deploy operations are batch tasks. Switch back to Budget model for subsequent operations.")

# === PUSH UPSTREAM ===
def increment_patch_version(content):
    """
    Finds 'version: "x.y.z"' or 'version: x.y.z' and increments z.
    """
    version_pattern = r'^(version:\s*["\']?)(\d+\.\d+\.)(\d+)(["\']?)$'
    
    def replace_version(match):
        prefix = match.group(1)
        base = match.group(2)
        patch = int(match.group(3))
        suffix = match.group(4)
        return f"{prefix}{base}{patch + 1}{suffix}"

    new_content, count = re.subn(version_pattern, replace_version, content, flags=re.MULTILINE)
    return new_content, count > 0


def resolve_foundation_agents(project_agents: str) -> str:
    """
    Resolve target foundation .agents path from marker file when available.
    Supports marker values that point either to foundation root OR directly to .agents.
    """
    foundation_path_marker = os.path.join(project_agents, ".foundation_path")

    if not os.path.exists(foundation_path_marker):
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    with open(foundation_path_marker, "r", encoding="utf-8") as f:
        marker_path = f.read().strip()

    marker_path = os.path.abspath(marker_path)

    # Case A: marker already points to .agents directory.
    if os.path.basename(marker_path).lower() == ".agents":
        return marker_path

    # Case B: marker points to foundation root.
    return os.path.join(marker_path, ".agents")


def files_differ(src: str, dest: str) -> bool:
    if not os.path.exists(dest):
        return True
    with open(src, "rb") as f:
        src_bytes = f.read()
    with open(dest, "rb") as f:
        dest_bytes = f.read()
    return src_bytes != dest_bytes


def copy_with_optional_version_bump(local_file: str, foundation_file: str, file_name: str, dry_run: bool) -> bool:
    """
    Copy local file to foundation path. Returns True if a version bump happened.
    """
    if dry_run:
        return False

    os.makedirs(os.path.dirname(foundation_file), exist_ok=True)

    if file_name in VERSION_BUMP_FILES:
        try:
            with open(local_file, "r", encoding="utf-8") as f:
                content = f.read()

            new_content, bumped = increment_patch_version(content)

            with open(foundation_file, "w", encoding="utf-8") as f:
                f.write(new_content)

            return bumped
        except Exception as e:
            print(f"    [WARNING] Could not auto-bump {file_name}: {e}")
            shutil.copy2(local_file, foundation_file)
            return False

    shutil.copy2(local_file, foundation_file)
    return False

def sync_upstream(project_root, dry_run=False):
    """
    Syncs changes from the local project's .agents back to the Foundation.
    Automatically increments version if SKILL.md or metadata files are changed.
    """
    if dry_run:
        print("[DRY RUN] Mode enabled. No files will be physically modified.")

    project_agents = os.path.join(project_root, ".agents")
    target_foundation_agents = resolve_foundation_agents(project_agents)

    if not os.path.exists(project_agents):
        print(f"Error: Local .agents folder not found at {project_agents}")
        return False

    if not os.path.exists(target_foundation_agents):
        print(f"Error: Foundation .agents not found at {target_foundation_agents}")
        print("Please check the .agents/.foundation_path file or FOUNDATION_ROOT in this script.")
        return False

    print("Starting Upstream Sync: [Project] -> [_foundation]")
    print(f"Target: {target_foundation_agents}\n")

    class SyncStatus:
        def __init__(self):
            self.changes_count: int = 0
            self.version_bumps: int = 0

    status = SyncStatus()

    # 1) Sync root-level .agents files explicitly (allowlisted)
    print("Checking root .agents files...")
    for file in ROOT_SYNC_FILES:
        local_file = os.path.join(project_agents, file)
        foundation_file = os.path.join(target_foundation_agents, file)

        if not os.path.exists(local_file):
            continue

        if not files_differ(local_file, foundation_file):
            continue

        tag = "[NEW]" if not os.path.exists(foundation_file) else "[MODIFIED]"
        print(f"  {tag} {file}")

        bumped = copy_with_optional_version_bump(local_file, foundation_file, file, dry_run)
        if bumped:
            print(f"    [INFO] Auto-bumped version for {file}")
            status.version_bumps += 1
        elif dry_run:
            print(f"  [SIMULATED] Copy {file} -> {target_foundation_agents}")

        status.changes_count += 1

    # 2) Sync evolvable folders
    for folder in EVOLVABLE_FOLDERS:
        src_path = os.path.join(project_agents, folder)
        dest_path = os.path.join(target_foundation_agents, folder)

        if not os.path.exists(src_path):
            continue

        print(f"Checking {folder}...")

        for root, dirs, files in os.walk(src_path):
            # Skip blacklisted directories
            filtered_dirs = [d for d in dirs if d not in BLACKLIST]
            dirs.clear()
            dirs.extend(filtered_dirs)
            
            for file in files:
                # Skip blacklisted items or local-specific evolution (prefixed with 'local-')
                if file in BLACKLIST or file.startswith("local-") or file == ".gitkeep" or file.endswith(".pyc"):
                    continue

                # Get relative path to maintain structure
                rel_path = os.path.relpath(os.path.join(root, file), src_path)

                # Double check if any part of the path starts with 'local-'
                path_parts = rel_path.split(os.sep)
                if any(p.startswith("local-") for p in path_parts):
                    continue

                local_file = os.path.join(root, file)
                foundation_file = os.path.join(dest_path, rel_path)

                # Check if foundation file exists and if content is different
                if not os.path.exists(foundation_file):
                    print(f"  [NEW] {os.path.join(folder, rel_path)}")
                    should_copy = True
                else:
                    if files_differ(local_file, foundation_file):
                        print(f"  [MODIFIED] {os.path.join(folder, rel_path)}")
                        should_copy = True
                    else:
                        should_copy = False

                if should_copy:
                    bumped = copy_with_optional_version_bump(local_file, foundation_file, file, dry_run)
                    if bumped:
                        print(f"    [INFO] Auto-bumped version for {file}")
                        status.version_bumps += 1
                    elif dry_run:
                        print(f"  [SIMULATED] Copy {file} -> {os.path.dirname(foundation_file)}")
                    
                    status.changes_count += 1

    if int(status.changes_count) > 0:
        print(f"\nSuccessfully synced {status.changes_count} files to Foundation.")
        if int(status.version_bumps) > 0:
            print(f"Total versions bumped: {status.version_bumps}")
        
        if not dry_run:
            print("\nSync completed successfully.")
        else:
            print("\n[DRY RUN] Would trigger graph and catalog updates in foundation.")
    else:
        print("\nNo changes detected. Foundation is already up-to-date.")

    return True


def cmd_upstream(args):
    project_root = os.path.abspath(args.project)
    
    # Idea 6: Genome Fingerprint auto-merge
    genome_path_local = os.path.join(project_root, ".agents", ".genome.json")
    foundation_path = get_foundation_path(project_root)
    if foundation_path:
        genome_path_upstream = os.path.join(foundation_path, ".agents", ".genome.json")
        if os.path.exists(genome_path_local) and os.path.exists(genome_path_upstream):
            try:
                import json
                with open(genome_path_local, 'r') as f: local_genome = json.load(f)
                with open(genome_path_upstream, 'r') as f: upstream_genome = json.load(f)
                
                # Auto-merge non-overlapping lists (Set union)
                upstream_genome["evolved_skills"] = list(set(upstream_genome.get("evolved_skills", []) + local_genome.get("evolved_skills", [])))
                upstream_genome["evolved_rules"] = list(set(upstream_genome.get("evolved_rules", []) + local_genome.get("evolved_rules", [])))
                upstream_genome["pruned_assets"] = list(set(upstream_genome.get("pruned_assets", []) + local_genome.get("pruned_assets", [])))
                
                # Merge fitness scores, preferring higher score
                local_scores = local_genome.get("fitness_scores", {})
                up_scores = upstream_genome.setdefault("fitness_scores", {})
                for k, v in local_scores.items():
                    if k not in up_scores or v > up_scores[k]:
                        up_scores[k] = v
                        
                upstream_genome["evolution_count"] = max(upstream_genome.get("evolution_count", 0), local_genome.get("evolution_count", 0))
                
                with open(genome_path_upstream, 'w') as f: json.dump(upstream_genome, f, indent=2)
                print(" [GENOME] Successfully auto-merged .genome.json upstream.")
            except Exception as e:
                print(f" [GENOME] Failed to merge .genome.json: {e}")

    sync_upstream(project_root, dry_run=args.dry_run)

# === SYNC AI CONFIGS ===
def sync_ai_configs(target_root: str, selected_ais: list | None = None, dry_run: bool = False):
    """
    Sync AI configuration files with latest foundation templates.
    
    Args:
        target_root: Path to target project
        selected_ais: List of AI names to sync. If None, syncs all deployed.
        dry_run: If True, simulate without writing
    
    Returns:
        dict: Sync results per AI
    """
    # Find foundation path
    foundation_path = get_foundation_path(target_root)
    if not foundation_path:
        if os.path.exists(os.path.join(target_root, ".agents", "templates", "AGENTS.template.md")):
            foundation_path = target_root
            print(" Running inside foundation.")
        else:
            print(" Error: Foundation path not found.")
            print("   This project may not be deployed from a foundation.")
            print("   Run foundation.py deploy first.")
            return {}
    
    if not os.path.exists(foundation_path):
        print(f" Error: Foundation not found at: {foundation_path}")
        return {}
    
    print(f" Foundation: {foundation_path}")
    
    # Determine which AIs to sync
    if selected_ais is None:
        # Try to load from tracking file
        deployed = load_deployed_ais(target_root)
        if deployed:
            selected_ais = deployed
            print(f" Syncing deployed AIs: {', '.join(selected_ais)}")
        else:
            # Default to all
            selected_ais = list(AI_CONFIGS.keys())
            print(f" Syncing all AIs (no tracking file found)")
    
    # Get project name
    project_name = os.path.basename(os.path.abspath(target_root))
    
    # Sync each AI
    results = {}
    source_templates = os.path.join(foundation_path, ".agents", "templates")
    
    print(f"\n Syncing AI configurations...")
    if dry_run:
        print(" [DRY RUN] No files will be modified.\n")
    
    # Read project manifest if available
    manifest = {}
    manifest_path = os.path.join(target_root, ".agents", ".project_manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception:
            pass

    for ai_name in selected_ais:
        if ai_name not in AI_CONFIGS:
            results[ai_name] = {"status": "ERROR", "message": f"Unknown AI: {ai_name}"}
            continue
        
        config = AI_CONFIGS[ai_name]
        template_path = os.path.join(source_templates, config["template"])
        
        if not os.path.exists(template_path):
            results[ai_name] = {"status": "ERROR", "message": "Template not found"}
            print(f"    {ai_name}: Template not found")
            continue
        
        # Build target path
        if config["target_dir"]:
            target_path = os.path.join(target_root, config["target_dir"], os.path.basename(config["target_path"]))
        else:
            target_path = os.path.join(target_root, config["target_path"])
        
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            # Read template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Smart merge
            content, status = smart_merge_config(
                template_content,
                target_path,
                project_name,
                config["format"],
                dry_run,
                manifest
            )
            
            if content is None:
                results[ai_name] = {"status": "SKIPPED", "message": status}
                print(f"    {ai_name}: {status}")
            else:
                results[ai_name] = {"status": "SUCCESS", "message": status}
                print(f"   {ai_name}: {status}{' (SIMULATED)' if dry_run else ''}")
        except Exception as e:
            results[ai_name] = {"status": "ERROR", "message": str(e)}
            print(f"   {ai_name}: {e}")
    
    # Update tracking file
    if not dry_run:
        deployed_file = os.path.join(target_root, ".agents", ".deployed_ais")
        try:
            data = {"project_name": project_name, "deployed_ais": selected_ais, "sync_results": results}
            with open(deployed_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"\n  Warning: Could not update tracking file: {e}")
    
    print(f"\n Sync completed{' (SIMULATED)' if dry_run else ''}.")
    return results


def cmd_sync_ai(args):
    selected_ais = args.ai.split(",") if getattr(args, "ai", None) else None
    sync_ai_configs(args.target, selected_ais=selected_ais, dry_run=args.dry_run)

# === CLI ===
def main():
    parser = argparse.ArgumentParser(description="Foundation Package & Deployment Manager")
    subparsers = parser.add_subparsers(dest="command")
    
    # Deploy
    parser_deploy = subparsers.add_parser("deploy", help="Deploy Foundation to a target project")
    parser_deploy.add_argument("--target", required=True, help="Target project root directory")
    parser_deploy.add_argument("--framework", required=True, help="Framework (e.g., react, flutter, node)")
    parser_deploy.add_argument("--language", required=True, help="Language (e.g., typescript, dart)")
    parser_deploy.add_argument("--ai", default="gemini", help="Comma-separated list of AIs to deploy (or 'all'). Defaults to 'gemini'.")
    parser_deploy.add_argument("--dry-run", action="store_true", help="Simulate deployment without modifying files")
    
    # Push Upstream
    parser_upstream = subparsers.add_parser("push-upstream", help="Sync local project changes back to Foundation")
    parser_upstream.add_argument("--project", default=".", help="Path to the local project root")
    parser_upstream.add_argument("--dry-run", action="store_true", help="Simulate sync without modifying files")
    
    # Sync AI
    parser_syncai = subparsers.add_parser("sync-ai", help="Sync AI brand configs to local templates")
    parser_syncai.add_argument("--target", required=True, help="Target project root directory")
    parser_syncai.add_argument("--ai", help="Comma-separated list of AIs to sync")
    parser_syncai.add_argument("--dry-run", action="store_true", help="Simulate sync without modifying files")

    args = parser.parse_args()
    
    if args.command == "deploy":
        cmd_deploy(args)
    elif args.command == "push-upstream":
        cmd_upstream(args)
    elif args.command == "sync-ai":
        cmd_sync_ai(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
