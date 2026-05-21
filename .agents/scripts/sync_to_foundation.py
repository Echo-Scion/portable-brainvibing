# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import os
import shutil
import argparse
import re

# Configuration
# Path to your central Foundation repository (Relatively determined from script location)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FOUNDATION_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR)) 
FOUNDATION_AGENTS = os.path.join(FOUNDATION_ROOT, ".agents")

# Folders that represent "The Brain" and should evolve
EVOLVABLE_FOLDERS = ["skills", "rules", "workflows", "canons", "templates", "scripts", "evals", "docs"]

# Root-level files in .agents that may evolve and should be propagated upstream.
ROOT_SYNC_FILES = ["DEPLOY_ME.md"]

# Only these files are eligible for automatic version bump.
VERSION_BUMP_FILES = {"SKILL.md"}

# Files/Folders to NEVER sync back to foundation (project-specific)
BLACKLIST = {
    "local",         # Project-specific experiments
    "tasks",         # Project-specific atomic tasks (inside workflows/)
    "personal",
    "debug_scripts",
    "pull_planning_context.py", # Local drive specific sync script
    ".git",
    "node_modules",
    "__pycache__",
    "vitals",
    "MEMORY.md",
    "SAAS_MEMORY.md"
}

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
        return FOUNDATION_AGENTS

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

def main():
    parser = argparse.ArgumentParser(description="Sync local agent evolution back to the Global Foundation.")
    parser.add_argument("--project", help="Path to the local project root", default=".")
    parser.add_argument("--dry-run", action="store_true", help="Simulate sync without modifying files.")
    
    args = parser.parse_args()
    
    # Resolve absolute path for project root
    project_root = os.path.abspath(args.project)
    
    sync_upstream(project_root, dry_run=args.dry_run)

if __name__ == "__main__":
    main()