"""
Intent Queue & Zero-Dependency Stdio JSON-RPC 2.0 MCP Staging Server.
Pure Python 3 standard library implementation.
Allows subagents to stage skill proposals without direct disk write permissions.
"""
import os
import sys
import json
import time
import uuid
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

try:
    from core.sandbox import parse_jsonrpc_request, format_jsonrpc_response, format_jsonrpc_error
except ImportError:
    _scripts_dir = str(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    from core.sandbox import parse_jsonrpc_request, format_jsonrpc_response, format_jsonrpc_error

try:
    from core.db import log_telemetry as _log_telemetry
except ImportError:
    from ..db import log_telemetry as _log_telemetry

VALID_ACTIONS = ("create", "update", "patch", "remove_file", "delete")
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class StagingError(Exception):
    """Raised when intent parameters violate structural or schema constraints."""
    pass


@dataclass
class StagedIntent:
    id: str
    action: str
    name: str
    reason: str
    evidence: str
    level: str = "project"  # "project" or "global"
    body: Optional[str] = None
    old_string: Optional[str] = None
    new_string: Optional[str] = None
    path: Optional[str] = None
    files: Optional[Dict[str, str]] = None
    absorbed_into: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StagedIntent":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class IntentQueue:
    """Persistent filesystem-backed FIFO intent queue for skill proposals."""

    def __init__(self, queue_dir: str):
        self.queue_dir = queue_dir
        os.makedirs(self.queue_dir, exist_ok=True)

    def enqueue(self, intent: StagedIntent) -> str:
        fn = f"{int(intent.timestamp * 1000)}_{intent.id}.json"
        target_path = os.path.join(self.queue_dir, fn)
        tmp_path = f"{target_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}"
        
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(intent.to_dict(), f, indent=2)
        os.replace(tmp_path, target_path)
        return target_path

    def peek(self) -> List[StagedIntent]:
        intents = []
        if not os.path.exists(self.queue_dir):
            return intents
            
        for fn in sorted(os.listdir(self.queue_dir)):
            if fn.endswith(".json") and ".tmp" not in fn:
                fp = os.path.join(self.queue_dir, fn)
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        intents.append(StagedIntent.from_dict(data))
                except Exception as _e:
                    _log_telemetry(_e, "staging.py:peek_intent")
        return intents

    def drain(self) -> List[Tuple[str, StagedIntent]]:
        """Returns list of (filepath, intent) and leaves them in place until cleared."""
        items = []
        if not os.path.exists(self.queue_dir):
            return items
            
        for fn in sorted(os.listdir(self.queue_dir)):
            if fn.endswith(".json") and ".tmp" not in fn:
                fp = os.path.join(self.queue_dir, fn)
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        items.append((fp, StagedIntent.from_dict(data)))
                except Exception as _e:
                    _log_telemetry(_e, "staging.py:drain_intent")
        return items

    def clear(self, filepaths: Optional[List[str]] = None) -> int:
        cleared = 0
        if filepaths:
            for fp in filepaths:
                if os.path.exists(fp):
                    try:
                        os.remove(fp)
                        cleared += 1
                    except Exception as _e:
                        _log_telemetry(_e, "staging.py:clear_fp")
        else:
            for fn in os.listdir(self.queue_dir):
                fp = os.path.join(self.queue_dir, fn)
                try:
                    if os.path.isfile(fp):
                        os.remove(fp)
                        cleared += 1
                except Exception as _e:
                    _log_telemetry(_e, "staging.py:clear_all")
        return cleared


def validate_intent_schema(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Fast in-flight schema validation of stage_skill parameters."""
    errors = []
    action = params.get("action")
    if action not in VALID_ACTIONS:
        errors.append(f"action must be one of {VALID_ACTIONS}, got {action!r}")

    name = params.get("name", "")
    if not isinstance(name, str) or not name.strip():
        errors.append("name is required and must be non-empty")
    elif not NAME_PATTERN.match(name.strip()):
        errors.append(f"name must be lowercase alphanumeric with hyphens, got {name!r}")

    if not params.get("reason"):
        errors.append("reason is required for ledger audit")
    if not params.get("evidence"):
        errors.append("evidence slice quote is required")

    if action in ("create", "update") and not params.get("body"):
        errors.append(f"body is required for action {action!r}")

    if action == "patch":
        if not params.get("old_string") or not params.get("new_string"):
            errors.append("patch requires both old_string and new_string")

    if action == "remove_file" and not params.get("path"):
        errors.append("remove_file requires relative path")

    paths_to_check = []
    if params.get("path"):
        paths_to_check.append(params.get("path"))
    files = params.get("files")
    if isinstance(files, list):
        paths_to_check.extend(files)
    elif isinstance(files, dict):
        paths_to_check.extend(files.keys())

    for p in paths_to_check:
        if not isinstance(p, str):
            errors.append(f"path must be a string, got {type(p).__name__}")
            continue
        norm_p = p.replace("\\", "/")
        if ".." in norm_p.split("/") or norm_p.startswith("/") or (len(norm_p) > 1 and norm_p[1] == ":"):
            errors.append(f"path must be relative and cannot contain traversal components ('..', leading '/', or drive letters): {p!r}")

    return len(errors) == 0, errors


class StagingServer:
    """Handles stage_skill calls and provides stdio MCP JSON-RPC 2.0 interface."""

    def __init__(self, queue: IntentQueue):
        self.queue = queue

    def stage_skill(self, params: Dict[str, Any]) -> Dict[str, Any]:
        is_valid, errors = validate_intent_schema(params)
        if not is_valid:
            return {
                "ok": False,
                "status": "rejected",
                "errors": errors
            }

        intent_id = str(uuid.uuid4())[:8]
        intent = StagedIntent(
            id=intent_id,
            action=params["action"],
            name=params["name"].strip(),
            reason=params["reason"].strip(),
            evidence=params["evidence"].strip(),
            level=params.get("level", "project"),
            body=params.get("body"),
            old_string=params.get("old_string"),
            new_string=params.get("new_string"),
            path=params.get("path"),
            files=params.get("files"),
            absorbed_into=params.get("absorbed_into")
        )

        self.queue.enqueue(intent)
        return {
            "ok": True,
            "status": "staged",
            "intent_id": intent_id,
            "name": intent.name,
            "action": intent.action
        }

    def run_stdio_mcp(self) -> None:
        """Runs the JSON-RPC 2.0 stdio server for MCP agents."""
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')

        for line in sys.stdin:
            req = parse_jsonrpc_request(line)
            if not req:
                continue

            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                resp_str = format_jsonrpc_response(req_id, result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "sovereign-stage-skill", "version": "1.0.0"}
                })
            elif method == "tools/list":
                resp_str = format_jsonrpc_response(req_id, result={
                    "tools": [
                        {
                            "name": "stage_skill",
                            "description": "Stage a skill modification intent (create/update/patch/delete). Proposes only; evaluated by promoter.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": list(VALID_ACTIONS)},
                                    "name": {"type": "string"},
                                    "level": {"type": "string", "enum": ["project", "global"]},
                                    "body": {"type": "string"},
                                    "old_string": {"type": "string"},
                                    "new_string": {"type": "string"},
                                    "reason": {"type": "string"},
                                    "evidence": {"type": "string"},
                                    "files": {"type": "object"},
                                    "path": {"type": "string"},
                                    "absorbed_into": {"type": "string"}
                                },
                                "required": ["action", "name", "reason", "evidence"]
                            }
                        }
                    ]
                })
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})
                if tool_name == "stage_skill":
                    result = self.stage_skill(args)
                    resp_str = format_jsonrpc_response(req_id, result={
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    })
                else:
                    resp_str = format_jsonrpc_error(req_id, -32601, f"Method {tool_name} not found")
            else:
                resp_str = format_jsonrpc_response(req_id, result={})

            sys.stdout.write(resp_str + "\n")
            sys.stdout.flush()
