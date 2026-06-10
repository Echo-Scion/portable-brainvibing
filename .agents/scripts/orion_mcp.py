#!/usr/bin/env python
import sys
import json
import traceback
import subprocess
import os

def log(msg):
    # Logging MUST go to stderr, stdout is strictly for JSON-RPC
    print(msg, file=sys.stderr, flush=True)

# Find the path to orion.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ORION_PY = os.path.join(SCRIPT_DIR, "orion.py")
PYTHON_EXEC = sys.executable or "python"

def run_orion_cmd(args):
    cmd = [PYTHON_EXEC, ORION_PY] + args
    try:
        project_root = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, check=True)
        return {"content": [{"type": "text", "text": result.stdout}], "isError": False}
    except subprocess.CalledProcessError as e:
        return {"content": [{"type": "text", "text": f"Error: {e.stderr or e.stdout}"}], "isError": True}

TOOLS = [
    {
        "name": "orion_ingest",
        "description": "Ingest files or directories into the Orion Brain Graph.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file or directory paths to ingest"
                },
                "autonomy": {
                    "type": "string",
                    "enum": ["balanced", "high", "strict"],
                    "description": "Autonomy level for ingestion"
                }
            },
            "required": ["paths"]
        }
    },
    {
        "name": "orion_resolve",
        "description": "Resolve a node in the Orion Brain Graph and retrieve context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "node": {
                    "type": "string",
                    "description": "Node name to resolve"
                }
            },
            "required": ["node"]
        }
    },
    {
        "name": "orion_verify",
        "description": "Run the Orion mechanical verification and AST drift check.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "orion_brain",
        "description": "Execute Neuro-Link Brain Engine sync or pagination.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_deploy",
        "description": "Deploy Foundation to a target project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_path": { "type": "string", "description": "Path to target project" }
            },
            "required": ["target_path"]
        }
    },
    {
        "name": "orion_scan",
        "description": "Run Ghost Token Auditor & Code Mapper.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_compress",
        "description": "Compress episodic memory to Caveman mode.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_nano",
        "description": "Use Nano LLM local compressor.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_swarm",
        "description": "Trigger Micro-Fix Swarm Delegation.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_amnesia",
        "description": "Trigger Rule Eviction & Token Bloat Control.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_scaffold",
        "description": "Run the SaaS Scaffolder.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_preflight",
        "description": "Run Self-Healing Routing Diagnostic.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_budget",
        "description": "Track budget and tier telemetry.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_compile",
        "description": "Compile Markdown rules into static output (matrix).",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_context_lint",
        "description": "Validate context/ naming conventions.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "orion_evolve",
        "description": "Self-Evolve Ecosystem Manager (bench, mine-friction, drift-scan).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subcommand": {
                    "type": "string",
                    "description": "Subcommand to run: bench, drift-scan, or mine-friction"
                },
                "skill": {
                    "type": "string",
                    "description": "Skill name for the bench subcommand"
                }
            },
            "required": ["subcommand"]
        }
    },
    {
        "name": "orion_push_upstream",
        "description": "Sync local project changes back to Foundation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_path": { "type": "string", "description": "Path to target project" }
            },
            "required": ["target_path"]
        }
    }
]

def handle_initialize(msg_id, params):
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "orion-mcp-server", "version": "1.0.0"}
        }
    }

def handle_tools_list(msg_id):
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "tools": TOOLS
        }
    }

def handle_tools_call(msg_id, params):
    name = params.get("name")
    args = params.get("arguments", {})
    
    if name == "orion_ingest":
        paths = args.get("paths", [])
        autonomy = args.get("autonomy", "balanced")
        cmd_args = ["orion_ops", "ingest", "--autonomy", autonomy] + paths
        result = run_orion_cmd(cmd_args)
    elif name == "orion_resolve":
        node = args.get("node", "")
        cmd_args = ["orion_ops", "resolve", node]
        result = run_orion_cmd(cmd_args)
    elif name == "orion_verify":
        result = run_orion_cmd(["verify"])
    elif name == "orion_brain":
        result = run_orion_cmd(["brain"])
    elif name == "orion_deploy":
        result = run_orion_cmd(["deploy", args.get("target_path", "")])
    elif name == "orion_scan":
        result = run_orion_cmd(["scan"])
    elif name == "orion_compress":
        result = run_orion_cmd(["compress"])
    elif name == "orion_nano":
        result = run_orion_cmd(["nano"])
    elif name == "orion_swarm":
        result = run_orion_cmd(["swarm"])
    elif name == "orion_amnesia":
        result = run_orion_cmd(["amnesia"])
    elif name == "orion_scaffold":
        result = run_orion_cmd(["scaffold"])
    elif name == "orion_preflight":
        result = run_orion_cmd(["preflight"])
    elif name == "orion_budget":
        result = run_orion_cmd(["budget"])
    elif name == "orion_compile":
        result = run_orion_cmd(["compile"])
    elif name == "orion_context_lint":
        result = run_orion_cmd(["context-lint"])
    elif name == "orion_evolve":
        subcmd = args.get("subcommand", "")
        cmd_args = ["evolve", subcmd]
        if subcmd == "bench" and args.get("skill"):
            cmd_args.extend(["--skill", args.get("skill")])
        result = run_orion_cmd(cmd_args)
    elif name == "orion_push_upstream":
        result = run_orion_cmd(["push-upstream", args.get("target_path", "")])
    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Tool not found: {name}"}
        }
        
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": result
    }

def main():
    log("Orion MCP Server started on stdio")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            params = req.get("params", {})
            
            # Note: notifications (requests without 'id') should not return a response
            if method == "initialize":
                res = handle_initialize(msg_id, params)
            elif method == "notifications/initialized":
                continue # No response needed
            elif method == "tools/list":
                res = handle_tools_list(msg_id)
            elif method == "tools/call":
                res = handle_tools_call(msg_id, params)
            elif method == "ping":
                res = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            else:
                if msg_id is not None:
                    res = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}
                else:
                    continue
            
            if msg_id is not None:
                # Write to stdout with newline
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
                
        except Exception as e:
            log(f"Error processing message: {e}\n{traceback.format_exc()}")
            if 'req' in locals() and req.get("id") is not None:
                error_res = {
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "error": {"code": -32603, "message": "Internal error"}
                }
                sys.stdout.write(json.dumps(error_res) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    main()
