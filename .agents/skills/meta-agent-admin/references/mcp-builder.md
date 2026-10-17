# 🔌 Model Context Protocol (MCP) Server Architecture

This document defines the production engineering standard for designing, authoring, and deploying Model Context Protocol (MCP) servers within the agent ecosystem.

---

## 1. Protocol Architecture & Transports

MCP establishes a standardized bidirectional bridge between LLM client runtimes and external tool systems via JSON-RPC 2.0.

### Supported Transports:
1. **Standard I/O (`stdio`)**: Primary local transport. The host agent spawns the MCP server as a subprocess, communicating through stdin/stdout. Zero network overhead, completely sandboxed.
2. **Streamable HTTP / SSE**: Remote transport for distributed microservices. Stateless request processing over standard HTTP POST with Server-Sent Events (SSE) for server-to-client notifications.

---

## 2. Server Capability Contracts

An MCP server advertises its capabilities during the `initialize` handshake:

```json
{
  "capabilities": {
    "tools": { "listChanged": true },
    "resources": { "subscribe": false, "listChanged": true },
    "prompts": { "listChanged": true }
  },
  "serverInfo": {
    "name": "ecosystem-mcp-server",
    "version": "1.0.0"
  }
}
```

---

## 3. Tool Specification Architecture

### 3.1 Input Schema Standard
Every tool MUST define an explicit JSON Schema defining accepted arguments:

```json
{
  "name": "query_knowledge_graph",
  "description": "Searches the semantic knowledge graph for relevant entity triplets and contextual documents.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query string or intent keywords."
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of results to return.",
        "default": 10,
        "minimum": 1,
        "maximum": 50
      }
    },
    "required": ["query"]
  }
}
```

### 3.2 Tool Annotations & Operational Hints
Declare behavioral hints on tools so client orchestrators understand safety boundaries:
- `readOnlyHint`: `true` if the tool strictly queries without mutating state.
- `destructiveHint`: `true` if the tool modifies, overwrites, or deletes persistent state.
- `idempotentHint`: `true` if repeated calls with identical arguments produce identical side-effects.

### 3.3 Output Content Envelopes
Tools respond with a structured content array:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Results formatted in readable markdown or serialized JSON"
    }
  ],
  "isError": false
}
```

---

## 4. Standard Python Stdio Server Template

Pure Python implementation pattern for local tool execution:

```python
import sys
import json
from typing import Dict, Any

def handle_request(req: Dict[str, Any]) -> Dict[str, Any]:
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": { "tools": {} },
                "serverInfo": { "name": "native-tools", "version": "1.0.0" }
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "ping",
                        "description": "Checks server connectivity and status.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        }

    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "ping":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": "PONG: Server active"}],
                    "isError": False
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": { "code": -32601, "message": f"Tool '{tool_name}' not found" }
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": { "code": -32601, "message": f"Method '{method}' not implemented" }
    }

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
```

---

## 5. Standard Error Handling Envelopes

MCP servers use standardized JSON-RPC 2.0 error codes:

| Code | Status | Meaning | Actionable Resolution |
| :--- | :--- | :--- | :--- |
| **`-32600`** | Invalid Request | Payload is not valid JSON-RPC 2.0 | Verify request structure and headers |
| **`-32601`** | Method Not Found | Requested method does not exist | Check tool name against `tools/list` |
| **`-32602`** | Invalid Params | Arguments failed JSON Schema | Provide required fields and correct types |
| **`-32603`** | Internal Error | Unhandled execution exception | Inspect error details in stderr |
| **`-32000`** | Execution Failure | Tool failed at runtime | Returned via `isError: true` with actionable message |

---

## 6. Security & Sandboxing Constraints

1. **Path Traversal Defense**: Validate all file paths against an approved base directory. Never allow `..` escapes.
2. **Command Injection Prevention**: Disallow raw shell execution without parameter whitelisting.
3. **Sensitive Key Redaction**: Mask API keys, tokens, and credentials in tool outputs.
