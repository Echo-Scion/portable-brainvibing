# -*- coding: utf-8 -*-
"""
Platform & Environment Capability Discovery Engine for .agents.
Zero-pip, 100% Python standard library implementation.

Detects the active host AI platform (Google Antigravity, Claude Code, Cursor,
Android Studio, VS Code, Headless CLI), catalogs native tools and slash commands,
and provides JIT proactive recommendations for users and agents.
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

_WINDOWLESS_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if sys.platform == "win32" else 0

# ---------------------------------------------------------------------------
# Platform Superpower Specifications
# ---------------------------------------------------------------------------

PLATFORM_CAPABILITIES: Dict[str, Dict[str, Any]] = {
    "antigravity": {
        "name": "Google Antigravity",
        "description": "Next-gen agentic coding IDE powered by Gemini with autonomous subagent mesh and sidecars.",
        "slash_commands": [
            {
                "command": "/plan",
                "purpose": "Step-by-step implementation plan artifact before execution",
                "trigger": "Complex tasks, multi-file changes, architectural refactors"
            },
            {
                "command": "/grill-me",
                "purpose": "Interactive interview to resolve ambiguous decisions and uncover edge cases",
                "trigger": "Unclear requirements, 50/50 architecture forks, trade-offs"
            },
            {
                "command": "/teamwork",
                "purpose": "Orchestrates a team of autonomous subagents on isolated git worktrees",
                "trigger": "Large multi-domain projects, concurrent parallel tasks"
            },
            {
                "command": "/boost",
                "purpose": "Maximum reasoning budget, deep multi-perspective analysis, and strict verification",
                "trigger": "Hard bugs, complex math/algorithms, deep code review"
            },
            {
                "command": "/schedule",
                "purpose": "Autonomous recurring cron job or one-shot delayed wakeup timer",
                "trigger": "Periodic monitoring, timed checks, delayed notifications"
            },
            {
                "command": "/goal",
                "purpose": "Long-running autonomous task execution that refuses to halt until verified",
                "trigger": "Overnight feature construction, exhaustive test suites"
            },
            {
                "command": "/browser",
                "purpose": "Interactive headless or visual browser automation and web scraping",
                "trigger": "Web UI testing, scraping dynamic documentation"
            },
            {
                "command": "/compact",
                "purpose": "Summarizes conversation context to free token budget and preserve cache",
                "trigger": "Context window > 80k tokens, long chat sessions"
            },
            {
                "command": "/learn",
                "purpose": "Reflects and persists behavioral corrections into long-term agent memory",
                "trigger": "After fixing repeated errors, user corrections"
            },
            {
                "command": "/automation",
                "purpose": "Interactive guide to design and author scheduled background automations",
                "trigger": "Creating recurring developer workflows or cron jobs"
            }
        ],
        "native_tools": [
            {"name": "ask_question", "kind": "UI Dialog", "description": "Interactive multiple-choice prompt in IDE"},
            {"name": "schedule", "kind": "Timer", "description": "Autonomous cron and one-shot wakeup scheduler"},
            {"name": "invoke_subagent", "kind": "Subagent", "description": "Spawns autonomous child agent"},
            {"name": "define_subagent", "kind": "Subagent", "description": "Registers dynamic custom subagent role"},
            {"name": "search_marketplace", "kind": "Ecosystem", "description": "Searches and surfaces plugin/skill cards"},
            {"name": "write_file", "kind": "Filesystem", "description": "Creates file or Markdown Artifact"},
            {"name": "edit_file", "kind": "Filesystem", "description": "Exact contiguous string surgical replacement"},
            {"name": "run_command", "kind": "Terminal", "description": "Executes shell commands in workspace"}
        ],
        "sidecars": ["Android Compose Preview", "Android Device Hub", "Figma Weave", "StitchMCP"]
    },
    "claude": {
        "name": "Claude Code",
        "description": "High-velocity CLI coding agent with pre-tool execution hooks and token compression.",
        "slash_commands": [
            {"command": "/compact", "purpose": "Summarize session history to reduce token load", "trigger": "Context bloat"},
            {"command": "/cost", "purpose": "Display token usage and billing analytics", "trigger": "Cost tracking"},
            {"command": "/doctor", "purpose": "Validate installation and environment health", "trigger": "Setup diagnosis"},
            {"command": "/review", "purpose": "Run code review on working git diff", "trigger": "Pre-commit review"},
            {"command": "/init", "purpose": "Initialize CLAUDE.md project guide", "trigger": "Onboarding"}
        ],
        "native_tools": [
            {"name": "Bash", "kind": "Terminal", "description": "Direct shell execution with rtk hook interception"},
            {"name": "Read", "kind": "Filesystem", "description": "File reader with line pagination"},
            {"name": "Edit", "kind": "Filesystem", "description": "Exact string replacement"},
            {"name": "Write", "kind": "Filesystem", "description": "File creator"},
            {"name": "Glob", "kind": "Filesystem", "description": "Pattern matching file scanner"},
            {"name": "Grep", "kind": "Search", "description": "Regex text searcher"}
        ],
        "sidecars": ["RTK Token Killer Proxy"]
    },
    "cursor": {
        "name": "Cursor",
        "description": "AI-first IDE with Composer, Agent Mode, and indexed multi-file code editing.",
        "slash_commands": [
            {"command": "@codebase", "purpose": "Semantic vector search across entire project", "trigger": "Broad queries"},
            {"command": "@docs", "purpose": "Query indexed third-party documentation", "trigger": "Library lookups"},
            {"command": "@git", "purpose": "Inspect recent commits and git deltas", "trigger": "Reviewing changes"}
        ],
        "native_tools": [
            {"name": "Composer", "kind": "Multi-file Edit", "description": "Simultaneous multi-file editing interface"},
            {"name": "Agent Mode", "kind": "Autonomous", "description": "Autonomous multi-step execution loop"}
        ],
        "sidecars": ["Cursor Rules Engine (.cursorrules)"]
    },
    "generic": {
        "name": "Universal CLI / Headless Agent",
        "description": "Standard sovereign terminal environment operating via POSIX/PowerShell CLI.",
        "slash_commands": [
            {"command": "/plan", "purpose": "Draft step-by-step implementation plan before execution", "trigger": "Complex tasks"},
            {"command": "/grill-me", "purpose": "Socratic interview to align on design decisions", "trigger": "Ambiguous requirements"},
            {"command": "/teamwork", "purpose": "Coordinate multi-agent or partitioned execution", "trigger": "Large projects"},
            {"command": "/boost", "purpose": "Deep reasoning and multi-perspective audit", "trigger": "Hard bugs, complex math"},
            {"command": "/compact", "purpose": "Summarize session history to reduce token budget", "trigger": "Context bloat"}
        ],
        "native_tools": [
            {"name": "python", "kind": "Runtime", "description": "Python 3.10+ standard library"},
            {"name": "git", "kind": "VCS", "description": "Git version control operations"}
        ],
        "sidecars": []
    }
}


# ---------------------------------------------------------------------------
# Host Environment & Platform Detection
# ---------------------------------------------------------------------------

def detect_host_platform(workspace_dir: Optional[str] = None) -> str:
    """
    Detects which AI platform or IDE is currently hosting this agent turn.
    Returns: 'antigravity', 'claude', 'cursor', or 'generic'.
    """
    ws = workspace_dir or os.getcwd()

    # 1. Google Antigravity detection
    if os.environ.get("ANTIGRAVITY_CONVERSATION_ID") or os.environ.get("ANTIGRAVITY_AGENT"):
        return "antigravity"
    ag_plugin = os.path.join(ws, ".antigravity-plugin", "plugin.json")
    if os.path.exists(ag_plugin):
        return "antigravity"
    app_data = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    if os.path.exists(os.path.join(app_data, ".gemini", "antigravity")):
        return "antigravity"

    # 2. Claude Code detection
    if os.environ.get("CLAUDE_CODE") or os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CLAUDE_SESSION_ID"):
        return "claude"
    if os.path.exists(os.path.join(ws, ".claude-plugin", "plugin.json")):
        return "claude"

    # 3. Cursor detection
    if os.environ.get("CURSOR_PROJECT_DIR") or os.path.exists(os.path.join(ws, ".cursorrules")):
        return "cursor"
    if os.path.exists(os.path.join(ws, ".cursor-plugin", "plugin.json")):
        return "cursor"

    # 4. Fallback: check active process tree (optional heuristic)
    try:
        # If ANTIGRAVITY is in environment anywhere
        for k in os.environ:
            if "ANTIGRAVITY" in k.upper():
                return "antigravity"
    except Exception:
        pass

    return "generic"


def get_environment_summary(workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Gathers comprehensive host environment, toolchain status, and native platform superpowers.
    """
    ws = workspace_dir or os.getcwd()
    platform_key = detect_host_platform(ws)
    platform_data = PLATFORM_CAPABILITIES.get(platform_key, PLATFORM_CAPABILITIES["generic"])

    os_system = platform.system()
    os_label = "Windows" if os_system == "Windows" else ("macOS" if os_system == "Darwin" else "Linux")
    is_windows = (os_system == "Windows")

    # Shell detection
    shell_label = "PowerShell 5.1/7+" if is_windows else "POSIX (bash/zsh)"

    # Python info
    py_ver = sys.version.split()[0]
    py_exec = sys.executable

    # Accelerators & 4-Pillars status
    accelerators_manifest = {}
    accelerators_active = 0
    try:
        from core.accelerators import get_active_accelerator_manifest
        accelerators_manifest = get_active_accelerator_manifest()
        accelerators_active = sum(1 for v in accelerators_manifest.values() if v.get("status") == "active")
    except Exception:
        pass

    # Tool presence checks
    tools_installed = {
        "python": True,
        "git": shutil.which("git") is not None,
        "rtk": shutil.which("rtk") is not None,
        "ast_grep": shutil.which("ast-grep") is not None or shutil.which("sg") is not None,
        "bun": shutil.which("bun") is not None,
        "ollama": shutil.which("ollama") is not None,
        "difft": shutil.which("difft") is not None,
    }

    return {
        "host_platform_key": platform_key,
        "host_platform_name": platform_data["name"],
        "host_platform_description": platform_data["description"],
        "os": os_label,
        "os_version": platform.version(),
        "arch": platform.machine(),
        "shell": shell_label,
        "python": {
            "version": py_ver,
            "executable": py_exec
        },
        "four_pillars": {
            "p1_python_stdlib": True,
            "p2_rust_accelerators": f"{accelerators_active}/7 Active",
            "p3_ollama_local_ai": tools_installed["ollama"],
            "p4_bun_runtime": tools_installed["bun"]
        },
        "tools_installed": tools_installed,
        "slash_commands": platform_data["slash_commands"],
        "native_tools": platform_data["native_tools"],
        "sidecars": platform_data.get("sidecars", [])
    }


# ---------------------------------------------------------------------------
# Formatting & CLI Output
# ---------------------------------------------------------------------------

def format_markdown_report(env: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 🌐 Host Platform & Environment Capabilities")
    lines.append("")
    lines.append(f"**Active Host Platform**: `{env['host_platform_name']}`")
    lines.append(f"**Environment**: `{env['os']} ({env['arch']})` | **Shell**: `{env['shell']}` | **Python**: `{env['python']['version']}`")
    lines.append(f"**4-Pillars Acceleration**: `{env['four_pillars']['p2_rust_accelerators']}`")
    lines.append("")

    if env["slash_commands"]:
        lines.append("## ⚡ Native Slash Commands (Available in Chat UI)")
        lines.append("")
        lines.append("| Slash Command | When to Trigger | What It Does |")
        lines.append("| :--- | :--- | :--- |")
        for sc in env["slash_commands"]:
            lines.append(f"| `{sc['command']}` | {sc['trigger']} | {sc['purpose']} |")
        lines.append("")

    if env["native_tools"]:
        lines.append("## 🛠️ Native Platform Tools")
        lines.append("")
        lines.append("| Tool Name | Kind | Purpose |")
        lines.append("| :--- | :--- | :--- |")
        for nt in env["native_tools"]:
            lines.append(f"| `{nt['name']}` | `{nt['kind']}` | {nt['description']} |")
        lines.append("")

    if env.get("sidecars"):
        lines.append(f"**Active Sidecars**: {', '.join(env['sidecars'])}")
        lines.append("")

    lines.append("## 💡 JIT Proactive Recommendations")
    lines.append("- Planning a non-trivial feature or refactor? Type `/plan`")
    lines.append("- Exploring design options or trade-offs? Type `/grill-me`")
    lines.append("- Multi-module or large project? Type `/teamwork`")
    lines.append("- Deep research or tricky bug? Type `/boost`")
    lines.append("- Session getting long (>80k tokens)? Type `/compact`")
    return "\n".join(lines)


def get_jit_recommendation(prompt: str = "") -> str:
    """
    Evaluates turn intent and returns a concise 1-line slash command recommendation.
    """
    p_lower = prompt.lower()
    if any(k in p_lower for k in ["refactor", "architect", "overhaul", "redesign", "scaffold", "new feature"]):
        return "Recommend `/plan` before execution."
    if any(k in p_lower for k in ["pilih", "choose", "option", "decision", "trade-off", "vs", "which"]):
        return "Recommend `/grill-me` to interview design decisions."
    if any(k in p_lower for k in ["concurrent", "parallel", "multi-agent", "team", "subagent", "massive"]):
        return "Recommend `/teamwork` for multi-agent delegation."
    if any(k in p_lower for k in ["deep", "hard bug", "crash", "algorithm", "audit security"]):
        return "Recommend `/boost` for maximum reasoning effort."
    if any(k in p_lower for k in ["schedule", "timer", "cron", "recurring", "every"]):
        return "Recommend `/schedule` for background timers."
    return "None"


def main():
    parser = argparse.ArgumentParser(description="Host Platform & Environment Discovery Engine")
    parser.add_argument("--platform", action="store_true", help="Print platform superpowers and slash command cheat sheet")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--jit", type=str, default="", help="Evaluate prompt text and output recommended slash command")
    parser.add_argument("--workspace", type=str, default=None, help="Target workspace root directory")

    args = parser.parse_args()

    if args.jit:
        rec = get_jit_recommendation(args.jit)
        print(rec)
        return

    env = get_environment_summary(args.workspace)

    if args.json:
        print(json.dumps(env, indent=2))
    else:
        print(format_markdown_report(env))


if __name__ == "__main__":
    main()
