import argparse
import os
import re
import sys
from typing import Dict, List, Set, Tuple


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(AGENTS_DIR, ".."))
CONTEXT_DIR = os.path.join(PROJECT_ROOT, "context")
REGISTRY_FILE = os.path.join(AGENTS_DIR, "templates", "SAAS_STARTUP_STRUCTURE.md")


PILLAR_MASTERS: Dict[str, str] = {
    "00_Strategy": "BLUEPRINT.md",
    "01_Product": "ROADMAP.md",
    "02_Creative": "STYLE_GUIDE.md",
    "03_Tech": "ARCHITECTURE.md",
}

# Transitional compatibility: these are still used by active workflows/docs.
TRANSITIONAL_ALLOWED: Dict[str, Set[str]] = {
    "00_Strategy": {"MEMORY.md"},
    "01_Product": {"PRD.md"},
    "02_Creative": set(),
    "03_Tech": set(),
}

ROOT_ALLOWED = {
    "README.md",
    "MIGRATION_MAP.md",
    "local-hybrid-glass-lab-theme.md",
}


def parse_registry(path: str) -> Dict[str, Set[str]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Registry not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    allowed: Dict[str, Set[str]] = {k: set() for k in PILLAR_MASTERS.keys()}
    current_pillar = None

    pillar_pattern = re.compile(r"##\s+\d+\.\s+Pillar:\s+`([^`]+)/`")
    # Match table rows and extract category prefix from column 2.
    row_pattern = re.compile(r"\|\s*\*\*[^|]+\*\*\s*\|\s*`([^`]+)`\s*\|(.+)\|")

    for raw in lines:
        line = raw.strip()
        p_match = pillar_pattern.match(line)
        if p_match:
            current_pillar = p_match.group(1)
            continue

        r_match = row_pattern.match(line)
        if not r_match or current_pillar not in allowed:
            continue

        prefix = r_match.group(1)
        files_col = r_match.group(2)
        file_parts = re.findall(r"`([^`]+\.md)`", files_col)
        for file_name in file_parts:
            if not file_name.endswith(".md"):
                continue
            allowed[current_pillar].add(f"{prefix}{file_name}")

    return allowed


def lint_context(strict: bool = True) -> Tuple[int, int, List[str]]:
    errors = 0
    warnings = 0
    output: List[str] = []

    if not os.path.isdir(CONTEXT_DIR):
        return 1, 0, [f"[ERROR] Missing context directory: {CONTEXT_DIR}"]

    allowed_from_registry = parse_registry(REGISTRY_FILE)

    # Check root files under context/
    root_files = [f for f in os.listdir(CONTEXT_DIR) if os.path.isfile(os.path.join(CONTEXT_DIR, f))]
    for f in sorted(root_files):
        if f not in ROOT_ALLOWED:
            errors += 1
            output.append(
                f"[ERROR] context/{f} is not allowed at context root. "
                f"Allowed root files: {', '.join(sorted(ROOT_ALLOWED))}"
            )

    for pillar, master in PILLAR_MASTERS.items():
        pillar_path = os.path.join(CONTEXT_DIR, pillar)
        if not os.path.isdir(pillar_path):
            errors += 1
            output.append(f"[ERROR] Missing required pillar directory: context/{pillar}")
            continue

        files = [f for f in os.listdir(pillar_path) if os.path.isfile(os.path.join(pillar_path, f))]
        if master not in files:
            errors += 1
            output.append(f"[ERROR] Missing required master file: context/{pillar}/{master}")

        allowed = set(allowed_from_registry.get(pillar, set()))
        allowed.add(master)
        allowed.update(TRANSITIONAL_ALLOWED.get(pillar, set()))

        for f in sorted(files):
            if f in allowed:
                if f in TRANSITIONAL_ALLOWED.get(pillar, set()):
                    warnings += 1
                    output.append(
                        f"[WARNING] Transitional file kept for compatibility: context/{pillar}/{f}"
                    )
                continue

            if strict:
                errors += 1
                output.append(
                    f"[ERROR] Non-registry file in context/{pillar}: {f}. "
                    f"Use 82-file registry names from SAAS_STARTUP_STRUCTURE.md"
                )
            else:
                warnings += 1
                output.append(
                    f"[WARNING] Non-registry file in context/{pillar}: {f}. "
                    f"Use 82-file registry names from SAAS_STARTUP_STRUCTURE.md"
                )

    return errors, warnings, output


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint context naming against 82-file registry.")
    parser.add_argument("--non-strict", action="store_true", help="Downgrade non-registry files to warnings.")
    args = parser.parse_args()

    strict = not args.non_strict
    print("Running Context Naming Lint (82-file registry + master anchors)...")

    try:
        errors, warnings, output = lint_context(strict=strict)
    except Exception as ex:
        print(f"[ERROR] Lint failed unexpectedly: {ex}")
        sys.exit(1)

    for line in output:
        print(line)

    if errors:
        print(f"\nContext naming lint failed: {errors} error(s), {warnings} warning(s).")
        sys.exit(1)

    print(f"\nContext naming lint passed: 0 error(s), {warnings} warning(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
