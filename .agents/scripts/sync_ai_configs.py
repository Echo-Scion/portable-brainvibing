# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Sync AI Configurations Script

Synchronizes foundation mandates across all deployed AI config files
in a target project. Preserves custom rules while updating foundation blocks.

Usage:
    python sync_ai_configs.py                    # Sync all deployed AIs in current directory
    python sync_ai_configs.py --target /path/    # Sync specific project
    python sync_ai_configs.py --ai gemini,copilot # Sync specific AIs only
    python sync_ai_configs.py --dry-run          # Preview changes
"""

import os
import sys
import json
import argparse

# Import AI registry and smart merge from deploy_foundation
# In real scenario, this would be a shared module
# For now, we duplicate the essential parts

AI_CONFIGS = {
    "gemini": {"template": "GEMINI.template.md", "target_path": "GEMINI.md", "target_dir": "", "format": "markdown"},
    "copilot": {"template": "COPILOT.template.md", "target_path": ".github/copilot-instructions.md", "target_dir": ".github", "format": "markdown"},
    "cursor": {"template": "CURSORRULES.template", "target_path": ".cursorrules", "target_dir": "", "format": "rules"},
    "windsurf": {"template": "WINDSURFRULES.template", "target_path": ".windsurfrules", "target_dir": "", "format": "rules"},
    "cline": {"template": "CLINERULES.template", "target_path": ".clinerules", "target_dir": "", "format": "rules"},
    "claude": {"template": "CLAUDE.template.md", "target_path": "CLAUDE.md", "target_dir": "", "format": "markdown"}
}

def load_deployed_ais(target_root: str):
    """Load list of deployed AIs from tracking file."""
    deployed_file = os.path.join(target_root, ".agents", ".deployed_ais")
    if not os.path.exists(deployed_file):
        return None
    
    try:
        with open(deployed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("deployed_ais", [])
    except Exception as e:
        print(f"⚠️  Warning: Could not read .deployed_ais: {e}")
        return None

def get_foundation_path(target_root: str):
    """Read foundation path from .foundation_path file."""
    path_file = os.path.join(target_root, ".agents", ".foundation_path")
    if not os.path.exists(path_file):
        return None
    
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"⚠️  Warning: Could not read .foundation_path: {e}")
        return None

def smart_merge_config(template_content: str, target_path: str, project_name: str, ai_format: str, dry_run: bool = False):
    """Smart merge AI config - preserves custom content."""
    import re
    
    # Inject project name
    template_content = template_content.replace("{project_name}", project_name)
    
    # Determine markers
    if ai_format == "markdown":
        start_marker = "<!-- START FOUNDATION MANDATES -->"
        end_marker = "<!-- END FOUNDATION MANDATES -->"
    else:
        start_marker = "# === FOUNDATION RULES START ==="
        end_marker = "# === FOUNDATION RULES END ==="
    
    # Extract foundation block
    pattern = re.escape(start_marker) + r"(.*?)" + re.escape(end_marker)
    template_match = re.search(pattern, template_content, re.DOTALL)
    
    if not template_match:
        foundation_block = template_content
    else:
        foundation_block = start_marker + template_match.group(1) + end_marker
    
    if not os.path.exists(target_path):
        return None, "File not found - skipping"
    
    # Read existing file
    with open(target_path, 'r', encoding='utf-8') as f:
        local_content = f.read()
    
    if start_marker not in local_content or end_marker not in local_content:
        return None, "No foundation markers found - skipping"
    
    # Replace foundation block only
    final_content = re.sub(
        pattern,
        foundation_block.replace("\\", "\\\\"),
        local_content,
        flags=re.DOTALL
    )
    
    if not dry_run:
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
    
    return final_content, "SYNCED"

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
        print("❌ Error: Foundation path not found.")
        print("   This project may not be deployed from a foundation.")
        print("   Run deploy_foundation.py first.")
        return {}
    
    if not os.path.exists(foundation_path):
        print(f"❌ Error: Foundation not found at: {foundation_path}")
        return {}
    
    print(f"📍 Foundation: {foundation_path}")
    
    # Determine which AIs to sync
    if selected_ais is None:
        # Try to load from tracking file
        deployed = load_deployed_ais(target_root)
        if deployed:
            selected_ais = deployed
            print(f"📋 Syncing deployed AIs: {', '.join(selected_ais)}")
        else:
            # Default to all
            selected_ais = list(AI_CONFIGS.keys())
            print(f"📋 Syncing all AIs (no tracking file found)")
    
    # Get project name
    project_name = os.path.basename(os.path.abspath(target_root))
    
    # Sync each AI
    results = {}
    source_templates = os.path.join(foundation_path, ".agents", "templates")
    
    print(f"\n🔄 Syncing AI configurations...")
    if dry_run:
        print("🧪 [DRY RUN] No files will be modified.\n")
    
    for ai_name in selected_ais:
        if ai_name not in AI_CONFIGS:
            results[ai_name] = {"status": "ERROR", "message": f"Unknown AI: {ai_name}"}
            continue
        
        config = AI_CONFIGS[ai_name]
        template_path = os.path.join(source_templates, config["template"])
        
        if not os.path.exists(template_path):
            results[ai_name] = {"status": "ERROR", "message": "Template not found"}
            print(f"  ⚠️  {ai_name}: Template not found")
            continue
        
        # Build target path
        if config["target_dir"]:
            target_path = os.path.join(target_root, config["target_dir"], os.path.basename(config["target_path"]))
        else:
            target_path = os.path.join(target_root, config["target_path"])
        
        try:
            # Read template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Smart merge
            content, status = smart_merge_config(
                template_content,
                target_path,
                project_name,
                config["format"],
                dry_run
            )
            
            if content is None:
                results[ai_name] = {"status": "SKIPPED", "message": status}
                print(f"  ⏭️  {ai_name}: {status}")
            else:
                results[ai_name] = {"status": "SUCCESS", "message": status}
                print(f"  ✅ {ai_name}: {status}{' (SIMULATED)' if dry_run else ''}")
        except Exception as e:
            results[ai_name] = {"status": "ERROR", "message": str(e)}
            print(f"  ❌ {ai_name}: {e}")
    
    # Update tracking file
    if not dry_run:
        deployed_file = os.path.join(target_root, ".agents", ".deployed_ais")
        try:
            data = {"project_name": project_name, "deployed_ais": selected_ais, "sync_results": results}
            with open(deployed_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"\n⚠️  Warning: Could not update tracking file: {e}")
    
    print(f"\n✅ Sync completed{' (SIMULATED)' if dry_run else ''}.")
    return results

def main():
    parser = argparse.ArgumentParser(
        description="Sync AI configuration files with latest foundation templates.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync all deployed AIs in current project
  python sync_ai_configs.py
  
  # Sync specific project
  python sync_ai_configs.py --target /path/to/project
  
  # Sync specific AIs only
  python sync_ai_configs.py --ai gemini,copilot
  
  # Preview changes without modifying files
  python sync_ai_configs.py --dry-run

Available AIs: gemini, copilot, cursor, windsurf, cline, claude
        """
    )
    parser.add_argument("--target", help="Path to target project root", default=".")
    parser.add_argument("--ai", help="Comma-separated list of AIs to sync. If omitted, syncs all deployed AIs.", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Simulate sync without modifying files.")
    parser.add_argument("--list-ais", action="store_true", help="List available AI configurations and exit.")
    
    args = parser.parse_args()
    
    if args.list_ais:
        print("Available AI Configurations:")
        for ai_name, config in AI_CONFIGS.items():
            print(f"  • {ai_name:12s} → {config['target_path']}")
        return
    
    # Parse AI selection
    selected_ais = None
    if args.ai:
        selected_ais = [ai.strip().lower() for ai in args.ai.split(",")]
        invalid = [ai for ai in selected_ais if ai not in AI_CONFIGS]
        if invalid:
            print(f"❌ Error: Unknown AI(s): {', '.join(invalid)}")
            print(f"Available: {', '.join(AI_CONFIGS.keys())}")
            sys.exit(1)
    
    sync_ai_configs(args.target, selected_ais=selected_ais, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
