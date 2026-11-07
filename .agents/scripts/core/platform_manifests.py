# -*- coding: utf-8 -*-
"""
Platform Manifest Registry and Dispatcher for 19 Multi-IDE & CLI Agents.
Enables one-command deployment to all supported agent platforms.
"""

import json
import os
import shutil
from pathlib import Path

PLATFORM_SPECS = {
    "antigravity": {
        "target_rel": ".antigravity-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "claude": {
        "target_rel": ".claude-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "cursor": {
        "target_rel": ".cursor-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "codex_app": {
        "target_rel": ".codex-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "codex_cli": {
        "target_rel": ".codex-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "devin": {
        "target_rel": ".devin-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "gemini": {
        "target_rel": "gemini-extension.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "contextFileName": "AGENTS.md"
        }
    },
    "android_studio": {
        "target_rel": ".idea/gemini.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "contextFileName": "AGENTS.md"
        }
    },
    "copilot": {
        "target_rel": ".copilot-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "instructions": ".github/copilot-instructions.md"
        }
    },
    "kimi": {
        "target_rel": ".kimi-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "hermes": {
        "target_rel": ".hermes-plugin/plugin.yaml",
        "format": "raw",
        "content": (
            "name: orioncortex\n"
            "version: 0.1.0\n"
            "description: Turnkey Auto-Vibe Coding Brain Ecosystem\n"
            "skills_dir: .agents/skills\n"
        )
    },
    "muse": {
        "target_rel": ".muse-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "droid": {
        "target_rel": ".droid-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "grok": {
        "target_rel": ".grok-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "opencode": {
        "target_rel": ".opencode/INSTALL.md",
        "format": "raw",
        "content": (
            "# OpenCode & Autonomous Harness Integration\n\n"
            "Add skills from `.agents/skills` to your local agent configuration.\n\n"
            "## Dual-Engine Second Worker & Multi-Model Harness Setup\n"
            "1. Copy `.env.example` to `.env` and set `ORION_API_KEY` to your API worker key.\n"
            "2. Verify 10-Role Swarm routing via `python .agents/scripts/orion.py worker status`.\n"
            "3. Dispatch specialized roles directly: `python .agents/scripts/orion.py worker dispatch --role <role> --prompt \"<task>\"`.\n"
            "4. Execute automated multi-role pipelines: `python .agents/scripts/orion.py worker auto \"<goal>\"`.\n"
            "5. Run stateless 5-Lens Swarm reviews: `python .agents/scripts/orion.py worker goldfish --spec implementation_plan.md`.\n"
        )
    },
    "pi": {
        "target_rel": ".pi-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "qwen": {
        "target_rel": ".qwen-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "minimax": {
        "target_rel": ".minimax-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    },
    "mimo": {
        "target_rel": ".mimo-plugin/plugin.json",
        "format": "json",
        "data": {
            "name": "orioncortex",
            "version": "0.1.0",
            "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
            "skills": ".agents/skills"
        }
    }
}


def is_flutterin_installed(target_root: str = "") -> bool:
    """5-Tier discovery check for flutterin suite across target workspace, sibling dir, plugin dir, or PATH."""
    if target_root:
        root_path = Path(target_root).resolve()
        if (root_path / "src" / "mcp" / "index.ts").is_file() or (root_path / ".flutterin").exists():
            return True
        sibling = root_path.parent / "flutterin" / "dist" / "mcp" / "index.js"
        if sibling.is_file():
            return True
    home_plugin = Path.home() / ".gemini" / "config" / "plugins" / "flutterin"
    if home_plugin.exists():
        return True
    return shutil.which("flutterin") is not None


def deploy_platform_manifest(
    target_root: str,
    platform_key: str,
    dry_run: bool = False,
    include_flutterin: bool | None = None,
) -> str | None:
    """Deploy a single platform plugin manifest to target_root."""
    spec = PLATFORM_SPECS.get(platform_key)
    if not spec:
        return None

    target_path = os.path.join(target_root, spec["target_rel"])
    if dry_run:
        return target_path

    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    if spec["format"] == "json":
        data = dict(spec["data"])
        if include_flutterin is True:
            data["mcpServers"] = {
                "flutterin": {
                    "command": "flutterin",
                    "args": ["mcp"],
                }
            }
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
    else:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(spec["content"])

    return target_path


def deploy_all_platform_manifests(
    target_root: str,
    dry_run: bool = False,
    include_flutterin: bool | None = None,
) -> list[str]:
    """Deploy all platform manifests into target_root."""
    created = []
    for platform_key in PLATFORM_SPECS:
        p = deploy_platform_manifest(
            target_root,
            platform_key,
            dry_run=dry_run,
            include_flutterin=include_flutterin,
        )
        if p and p not in created:
            created.append(p)
    return created


NATIVE_SUBAGENT_PLATFORMS = {"antigravity", "claude", "codex_app", "codex_cli"}


def get_platform_delegation_policy(platform_key: str) -> dict:
    """
    Returns deterministic subagent & CLI delegation capabilities for the given host platform.
    Enforces the Second-Worker-First Law across all 19 platforms to prevent primary IDE quota burn.
    """
    key = (platform_key or "generic").lower().strip()
    supports_native = key in NATIVE_SUBAGENT_PLATFORMS
    return {
        "platform": key,
        "supports_native_subagents": supports_native,
        "native_model_locked_to_session": key == "antigravity",
        "max_native_parallel": 2 if supports_native else 0,
        "preferred_delegation_engine": "orion_cli_worker",
        "fallback_engine": "native_subagent_bounded" if supports_native else "tier0_mechanical_scout",
    }

