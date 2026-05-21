# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
from __future__ import annotations
import os
import shutil
import sys
import re
import argparse
import json

# AI Configuration Registry
AI_CONFIGS = {
    "gemini": {
        "template": "AGENTS.template.md",
        "target_path": "GEMINI.md",
        "target_dir": "",  # Root
        "format": "markdown",
        "merge_strategy": "marker"
    },
    "copilot": {
        "template": "AGENTS.template.md",
        "target_path": ".github/copilot-instructions.md",
        "target_dir": ".github",
        "format": "markdown",
        "merge_strategy": "marker"
    },

    "claude": {
        "template": "AGENTS.template.md",
        "target_path": "CLAUDE.md",
        "target_dir": "",  # Root
        "format": "markdown",
        "merge_strategy": "marker"
    }
}

def smart_merge_config(template_path: str, target_path: str, project_name: str, ai_format: str, dry_run: bool = False):
    """
    Smart merge AI config files with foundation mandates.
    Preserves custom content while updating foundation blocks.
    
    Args:
        template_path: Path to template file
        target_path: Path to target config file
        project_name: Name of project for injection
        ai_format: 'markdown' or 'rules'
        dry_run: If True, simulate without writing
    
    Returns:
        tuple: (final_content, status_message)
    """
    if not os.path.exists(template_path):
        return None, f"Template not found: {template_path}"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        raw_template = f.read()
    
    # Inject project name
    raw_template = raw_template.replace("{project_name}", project_name)
    
    # Determine markers based on format
    if ai_format == "markdown":
        start_marker = "<!-- START FOUNDATION MANDATES -->"
        end_marker = "<!-- END FOUNDATION MANDATES -->"
    else:  # rules format
        start_marker = "# === FOUNDATION RULES START ==="
        end_marker = "# === FOUNDATION RULES END ==="
    
    # Extract foundation block from template
    pattern = re.escape(start_marker) + r"(.*?)" + re.escape(end_marker)
    template_match = re.search(pattern, raw_template, re.DOTALL)
    
    if not template_match:
        # Template doesn't have markers, use entire content
        foundation_block = raw_template
    else:
        foundation_block = start_marker + template_match.group(1) + end_marker
    
    final_content = ""
    status = ""
    
    if os.path.exists(target_path):
        # Target exists - smart merge
        with open(target_path, 'r', encoding='utf-8') as f:
            local_content = f.read()
        
        if start_marker in local_content and end_marker in local_content:
            # Has markers - replace foundation block only
            final_content = re.sub(
                pattern, 
                foundation_block.replace("\\", "\\\\"),  # Escape backslashes for re.sub
                local_content, 
                flags=re.DOTALL
            )
            status = "UPDATED (Merged Block)"
        else:
            # No markers - prepend foundation block
            if ai_format == "markdown":
                header = f"# Workspace Rules: {project_name}\n\n"
                separator = "\n\n## PROJECT-SPECIFIC RULES\n<!-- Do not remove the foundation markers above. Put your custom rules below. -->\n\n"
            else:
                header = f"# Rules for {project_name}\n\n"
                separator = "\n\n# === PROJECT-SPECIFIC RULES ===\n"
            
            final_content = header + foundation_block + separator + local_content
            status = "MERGED (Prepended & Wrapped)"
    else:
        # Target doesn't exist - create new
        final_content = raw_template
        status = "CREATED"
    
    if not dry_run:
        # Ensure target directory exists
        target_dir = os.path.dirname(target_path)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
    
    return final_content, status

def deploy_ai_configs(source_root: str, target_root: str, project_name: str, selected_ais: list, dry_run: bool = False):
    """
    Deploy AI configuration files to target project.
    
    Args:
        source_root: Path to foundation root
        target_root: Path to target project
        project_name: Project name for injection
        selected_ais: List of AI names to deploy (e.g., ['gemini', 'copilot'])
        dry_run: If True, simulate without writing
    
    Returns:
        dict: Deployment results per AI
    """
    source_templates = os.path.join(source_root, ".agents", "templates")
    results = {}
    
    print(f"\n📝 Deploying AI configurations for: {', '.join(selected_ais)}")
    
    for ai_name in selected_ais:
        if ai_name not in AI_CONFIGS:
            results[ai_name] = {"status": "ERROR", "message": f"Unknown AI: {ai_name}"}
            continue
        
        config = AI_CONFIGS[ai_name]
        template_path = os.path.join(source_templates, config["template"])
        
        # Build target path
        if config["target_dir"]:
            target_path = os.path.join(target_root, config["target_dir"], os.path.basename(config["target_path"]))
        else:
            target_path = os.path.join(target_root, config["target_path"])
        
        try:
            content, status = smart_merge_config(
                template_path,
                target_path,
                project_name,
                config["format"],
                dry_run
            )
            
            if content is None:
                results[ai_name] = {"status": "ERROR", "message": status}
                print(f"  ❌ {ai_name}: {status}")
            else:
                results[ai_name] = {"status": "SUCCESS", "message": status, "path": target_path}
                print(f"  ✅ {ai_name}: {status}{' (SIMULATED)' if dry_run else ''}")
                print(f"     → {target_path}")
        except Exception as e:
            results[ai_name] = {"status": "ERROR", "message": str(e)}
            print(f"  ❌ {ai_name}: {e}")
    
    # Track deployed AIs
    if not dry_run:
        deployed_file = os.path.join(target_root, ".agents", ".deployed_ais")
        try:
            with open(deployed_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "project_name": project_name,
                    "deployed_ais": selected_ais,
                    "results": results
                }, f, indent=2)
            print(f"\n📌 Deployed AI configurations tracked in .agents/.deployed_ais")
        except Exception as e:
            print(f"⚠️  Warning: Could not track deployed AIs: {e}")
    
    return results

def verify_github_native_deployment(target_root: str, dry_run: bool = False) -> bool:
    """
    Verify that GitHub native stack was deployed correctly.
    
    Checks for:
    - Required .github/rules/ files
    - Required .github/agents/ files
    - Required .github/workflows/ files
    - Required .github/ root documentation
    
    Returns:
        bool: True if all checks passed, False otherwise
    """
    target_github = os.path.join(target_root, ".github")
    issues = []
    
    if not os.path.exists(target_github):
        print(f"  ⚠️  .github/ directory not found")
        return False
    
    # Check required rule files
    required_rules = [
        ("agent-core.md", "Core behavioral rules"),
        ("tier-execution.md", "Tier execution protocols"),
        ("security-gates.md", "Security gates"),
        ("context-standards.md", "Context standards")
    ]
    
    rules_dir = os.path.join(target_github, "rules")
    if os.path.exists(rules_dir):
        for rule_file, desc in required_rules:
            path = os.path.join(rules_dir, rule_file)
            if not os.path.exists(path):
                issues.append(f"  ❌ Missing rule: .github/rules/{rule_file} ({desc})")
            else:
                print(f"  ✅ .github/rules/{rule_file}")
    else:
        issues.append(f"  ❌ Missing directory: .github/rules/")
    
    # Check required agent files
    required_agents = [
        ("copilot.agent.md", "Primary Copilot agent"),
        ("foundation-deployer.agent.md", "Deployer agent"),
        ("integrity-auditor.agent.md", "QA/Security agent"),
        ("README.md", "Agents documentation")
    ]
    
    agents_dir = os.path.join(target_github, "agents")
    if os.path.exists(agents_dir):
        for agent_file, desc in required_agents:
            path = os.path.join(agents_dir, agent_file)
            if not os.path.exists(path):
                issues.append(f"  ❌ Missing agent: .github/agents/{agent_file} ({desc})")
            else:
                print(f"  ✅ .github/agents/{agent_file}")
    else:
        issues.append(f"  ❌ Missing directory: .github/agents/")
    
    # Check required workflow files
    required_workflows = [
        ("verify-agents.yml", "Verification workflow"),
        ("deploy-foundation.yml", "Deployment workflow"),
        ("check-staleness.yml", "Staleness detection"),
        ("publish-foundation.yml", "Publishing workflow")
    ]
    
    workflows_dir = os.path.join(target_github, "workflows")
    if os.path.exists(workflows_dir):
        for workflow_file, desc in required_workflows:
            path = os.path.join(workflows_dir, workflow_file)
            if not os.path.exists(path):
                issues.append(f"  ❌ Missing workflow: .github/workflows/{workflow_file} ({desc})")
            else:
                print(f"  ✅ .github/workflows/{workflow_file}")
    else:
        issues.append(f"  ❌ Missing directory: .github/workflows/")
    
    # Check root documentation
    for doc_file in ["ARCHITECTURE.md", "README.md"]:
        path = os.path.join(target_github, doc_file)
        if not os.path.exists(path):
            issues.append(f"  ❌ Missing documentation: .github/{doc_file}")
        else:
            print(f"  ✅ .github/{doc_file}")
    
    # Report issues
    if issues:
        print("\n  Issues found during verification:")
        for issue in issues:
            print(issue)
        return False
    
    print("  ✅ All GitHub native components verified")
    return True

def deploy(source_root: str, target_root: str, selected_ais: list | None = None, dry_run: bool = False):
    """
    Copies foundation skills and rules to the target project.
    Deploys AI configuration files for selected assistants.
    
    Args:
        source_root: Path to foundation root
        target_root: Path to target project
        selected_ais: List of AI names to deploy configs for. If None, deploys all.
        dry_run: If True, simulate without modifying files
    """
    if dry_run:
        print("🧪 [DRY RUN] Mode enabled. No files will be physically modified.")
    
    # Default to all AIs if none specified
    if selected_ais is None:
        selected_ais = list(AI_CONFIGS.keys())
    
    print(f"🚀 Deploying Foundation to: {target_root}")
    print(f"📋 AI Assistants: {', '.join(selected_ais)}")

    source_agents = os.path.join(source_root, ".agents")
    target_agents = os.path.join(target_root, ".agents")

    if not os.path.exists(source_agents):
        print(f"Error: Source foundation not found at {source_agents}")
        return False

    if not os.path.exists(target_agents):
        if not dry_run:
            os.makedirs(target_agents, exist_ok=True)
        print(f"Created local .agents/ at {target_agents}")

    # ⚠️ CRITICAL COUPLING:
    # If you modify FOLDERS_TO_SYNC or deployment logic below, 
    # YOU MUST ALSO UPDATE the agentic fallback instructions in `.agents/DEPLOY_ME.md`!
    FOLDERS_TO_SYNC = ["skills", "rules", "canons", "templates", "evals", "docs", "scripts"]
    
    # GitHub native structure folders (new in v2.0)
    GITHUB_FOLDERS_TO_SYNC = ["rules", "agents", "workflows"]

    # Exclude list: relative paths or filenames that must never be overwritten on target
    BLACKLIST = {
        "scripts/deploy_foundation.py",
        ".git",
        "node_modules"
    }
    
    # GitHub-specific exclusions (preserve project customizations)
    GITHUB_BLACKLIST = {
        "custom",  # Project-specific rules/agents/workflows
        ".copilot-memory.md"  # Session-scoped memory
    }

    def sync_recursive(src: str, dest: str, blacklist: set[str] | None = None, base_rel_path: str = ""):
        """Surgical sync: syncs files and removes stale items not present in src."""
        if blacklist is None:
            blacklist = set()
            
        def is_blacklisted(rel_item_path: str) -> bool:
            basename = os.path.basename(rel_item_path)
            rel_unix = rel_item_path.replace('\\', '/')
            return basename in blacklist or rel_unix in blacklist

        if not os.path.exists(dest):
            if not dry_run:
                os.makedirs(dest, exist_ok=True)
            print(f"  [CREATE] {dest}")

        # Phase 1: Remove stale files from dest
        if os.path.exists(dest):
            for item in os.listdir(dest):
                item_rel = os.path.join(base_rel_path, item).replace("\\", "/")
                if is_blacklisted(item_rel):
                    continue
                
                s_item = os.path.join(src, item)
                d_item = os.path.join(dest, item)
                
                if not os.path.exists(s_item):
                    if not dry_run:
                        if os.path.isdir(d_item):
                            shutil.rmtree(d_item)
                        else:
                            os.remove(d_item)
                    print(f"  [DELETE STALE] {item_rel}")

        # Phase 2: Copy from src to dest
        for item in os.listdir(src):
            item_rel = os.path.join(base_rel_path, item).replace("\\", "/")
            if is_blacklisted(item_rel):
                continue

            s = os.path.join(src, item)
            d = os.path.join(dest, item)

            if os.path.isdir(s):
                sync_recursive(s, d, blacklist, item_rel)
            else:
                if not dry_run:
                    shutil.copy2(s, d)
                # Removing extremely verbose per-file logging to keep console clean,
                # you will still see [DELETE STALE] or higher level operations.

    # 1. Sync standard .agents folders
    for folder in FOLDERS_TO_SYNC:
        src_path = os.path.join(source_agents, folder)
        dest_path = os.path.join(target_agents, folder)

        if not os.path.exists(src_path):
            continue

        print(f"Syncing {folder}...")
        sync_recursive(src_path, dest_path, BLACKLIST)

    # 2. Sync GitHub native structure (.github/)
    print("\n📊 GitHub Native Stack Deployment")
    source_github = os.path.join(source_root, ".github")
    target_github = os.path.join(target_root, ".github")
    
    if os.path.exists(source_github):
        for folder in GITHUB_FOLDERS_TO_SYNC:
            src_path = os.path.join(source_github, folder)
            dest_path = os.path.join(target_github, folder)
            
            if not os.path.exists(src_path):
                continue
            
            print(f"  Syncing .github/{folder}...")
            sync_recursive(src_path, dest_path, GITHUB_BLACKLIST)
        
        # 2.1 Sync GitHub root documentation files
        github_root_files = ["ARCHITECTURE.md", "README.md"]
        for fname in github_root_files:
            src_file = os.path.join(source_github, fname)
            dest_file = os.path.join(target_github, fname)
            
            if os.path.exists(src_file):
                if not dry_run:
                    os.makedirs(target_github, exist_ok=True)
                    shutil.copy2(src_file, dest_file)
                print(f"  [COPY] .github/{fname}")

    # 3. Sync workflows/ root files ONLY
    src_workflows = os.path.join(source_agents, "workflows")
    dest_workflows = os.path.join(target_agents, "workflows")
    if os.path.exists(src_workflows):
        print("Syncing workflows (root files only, skipping tasks/)...")
        if not os.path.exists(dest_workflows):
            if not dry_run:
                os.makedirs(dest_workflows, exist_ok=True)
        for item in os.listdir(src_workflows):
            s = os.path.join(src_workflows, item)
            d = os.path.join(dest_workflows, item)
            if os.path.isfile(s) and item not in BLACKLIST:
                if not dry_run:
                    shutil.copy2(s, d)
                print(f"  [COPY] {item} -> workflows/")
        tasks_dir = os.path.join(dest_workflows, "tasks")
        if not os.path.exists(tasks_dir):
            if not dry_run:
                os.makedirs(tasks_dir, exist_ok=True)
            print("  Created workflows/tasks/ for project-specific tasks.")

    # 3. Retrieve project name
    project_name = os.path.basename(os.path.abspath(target_root))

    # 4. Seed LEARNINGS.md if it doesn't exist
    learnings_path = os.path.join(target_agents, "LEARNINGS.md")
    if not os.path.exists(learnings_path):
        if not dry_run:
            with open(learnings_path, "w", encoding="utf-8") as f:
                f.write(f"# Persistent Learnings & Post-Mortems\n\nThis file serves as the collective memory for AI agents working in {project_name}. It documents systemic failures, complex bug fixes, and architectural \"gotchas\" to prevent repetition of errors.\n\n## 0. Log Template\n> **[DATE]** | **[TASK_ID]** | **[TIER]**\n> - **Issue**: Brief description of what went wrong or the complexity faced.\n> - **Root Cause**: The foundational reason for the failure.\n> - **Solution**: The specific pattern or fix that worked.\n> - **Debt/Warning**: Future considerations or brittle areas discovered.\n\n---\n")
        print("  [CREATE] Seeded empty LEARNINGS.md")


    # 4.5 Deploy AI Configuration Files
    deploy_ai_configs(source_root, target_root, project_name, selected_ais, dry_run)

    # 5. Persist the source foundation path
    if not dry_run:
        try:
            with open(os.path.join(target_agents, ".foundation_path"), "w", encoding="utf-8") as f:
                f.write(os.path.abspath(source_root))
            print("📌 Foundation path persisted for sync support.")
        except Exception as e:
            print(f"⚠️  Warning: Could not persist foundation path: {e}")

    # 5.5 Verify GitHub native deployment (NEW in v2.0)
    print("\n🔍 Verifying GitHub native stack deployment...")
    github_verification = verify_github_native_deployment(target_root, dry_run)
    if not github_verification:
        print("⚠️  Warning: GitHub native stack verification found issues. Review above.")
    else:
        print("✅ GitHub native stack verified successfully")

    # 6. Post Deploy Hooks
    if not dry_run:
        scripts_dir = os.path.join(target_agents, "scripts")
        
        # Run sync_ai_configs if needed
        sync_discovery_script = os.path.join(scripts_dir, "sync_ai_configs.py")
        if os.path.exists(sync_discovery_script):
            print("\n🎯 Running sync_ai_configs.py...")
            # NOTE: Automatically executing downstream scripts during deployment is disabled 
            # by default to prevent unwanted side-effects on the target project's local workspace.
            # If a full configuration sync is required, run sync_ai_configs.py explicitly.
            # subprocess.run([sys.executable, sync_discovery_script], cwd=target_root)

    print(f"\n✅ Deployment finished{' (SIMULATED)' if dry_run else ''}.")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Deploy Global Foundation physically to a local project with multi-AI support.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy all AI configs (default)
  python deploy_foundation.py --target /path/to/project
  
  # Deploy specific AI only
  python deploy_foundation.py --target /path/to/project --ai copilot
  
  # Deploy multiple AIs
  python deploy_foundation.py --target /path/to/project --ai gemini,copilot,cursor
  
  # Dry run to preview changes
  python deploy_foundation.py --target /path/to/project --dry-run
  
Available AIs: gemini, copilot, cursor, windsurf, cline, claude
        """
    )
    parser.add_argument("--source", help="Path to the global foundation root", default=None)
    parser.add_argument("--target", help="Path to the target project root", default=".")
    parser.add_argument("--ai", help="Comma-separated list of AI assistants to deploy configs for. Use 'all' for all AIs (default).", default="all")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deployment without modifying files.")
    parser.add_argument("--list-ais", action="store_true", help="List available AI configurations and exit.")

    args = parser.parse_args()
    
    # List available AIs
    if args.list_ais:
        print("Available AI Configurations:")
        for ai_name, config in AI_CONFIGS.items():
            print(f"  • {ai_name:12s} → {config['target_path']}")
        return

    source = args.source
    if not source:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        source = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    # Parse AI selection
    if args.ai.lower() == "all":
        selected_ais = list(AI_CONFIGS.keys())
    else:
        selected_ais = [ai.strip().lower() for ai in args.ai.split(",")]
        # Validate AI names
        invalid = [ai for ai in selected_ais if ai not in AI_CONFIGS]
        if invalid:
            print(f"❌ Error: Unknown AI(s): {', '.join(invalid)}")
            print(f"Available: {', '.join(AI_CONFIGS.keys())}")
            sys.exit(1)

    deploy(source, args.target, selected_ais=selected_ais, dry_run=args.dry_run)

if __name__ == "__main__":
    main()