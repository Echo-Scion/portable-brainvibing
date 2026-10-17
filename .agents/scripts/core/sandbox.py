import os
import sys
import shutil
import tempfile
import subprocess
import argparse
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, Any, Tuple, Optional, Generator, Set

try:
    from core import log_telemetry as _log_telemetry
except ImportError:
    def _log_telemetry(err: Exception = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")


if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception as _e:
        _log_telemetry(_e, 'sandbox.py:reconfigure')


SAFE_ENV_VARS: Set[str] = {
    "PATH", "SYSTEMROOT", "TMP", "TEMP", "USERPROFILE",
    "HOME", "PYTHONPATH", "COMSPEC", "PATHEXT", "LANG", "LC_ALL"
}


class SovereignSandbox:
    """
    Pillar 1: Ephemeral Workspace Runner & Process Execution Environment.
    Provides clean-room execution with credential stripping, strict timeouts,
    and ephemeral workspace directory teardown without Docker/microVM requirements.
    Notice: This is an Ephemeral Workspace Runner and environment sanitizer,
    not an OS-level kernel namespace/chroot/seccomp hermetic jail.
    """

    @staticmethod
    @contextmanager
    def ephemeral_workspace(prefix: str = "sovereign_sb_") -> Generator[str, None, None]:
        """
        Creates an isolated temporary directory that is guaranteed to be deleted on exit.
        """
        with tempfile.TemporaryDirectory(prefix=prefix) as tmp_dir:
            yield tmp_dir

    @staticmethod
    def _install_runtime_audit_jail(sandbox_dir: str) -> None:
        """Writes a PEP 578 sitecustomize.py into sandbox_dir to block external writes and sockets at runtime."""
        jail_code = (
            "import os, sys\n"
            f"_JAIL_ROOT = os.path.realpath({sandbox_dir!r})\n"
            "def _orion_mac_hook(event, args):\n"
            "    if event == 'open' and len(args) >= 2:\n"
            "        path, mode = args[0], str(args[1] or 'r')\n"
            "        if any(m in mode for m in ('w', 'a', 'x', '+')) and isinstance(path, (str, bytes)):\n"
            "            try:\n"
            "                real_p = os.path.realpath(os.fsdecode(path))\n"
            "                if not real_p.startswith(_JAIL_ROOT) and not real_p.startswith('/dev/') and not real_p.startswith('\\\\\\\\.\\\\nul') and real_p.lower() != 'nul':\n"
            "                    raise PermissionError(f'[ORION MAC JAIL] Write blocked outside sandbox: {real_p}')\n"
            "            except (ValueError, TypeError):\n"
            "                pass\n"
            "    elif event == 'socket.connect' and len(args) >= 2:\n"
            "        addr = args[1]\n"
            "        host = addr[0] if isinstance(addr, tuple) and addr else ''\n"
            "        if host not in ('127.0.0.1', 'localhost', '::1'):\n"
            "            raise PermissionError(f'[ORION MAC JAIL] External socket blocked: {host}')\n"
            "try:\n"
            "    sys.addaudithook(_orion_mac_hook)\n"
            "except Exception:\n"
            "    pass\n"
        )
        site_path = os.path.join(sandbox_dir, "sitecustomize.py")
        with open(site_path, "w", encoding="utf-8") as f:
            f.write(jail_code)

    @classmethod
    def execute_snippet(
        cls,
        code: str,
        extension: str = ".py",
        timeout: float = 30.0,
        extra_env: Optional[Dict[str, str]] = None
    ) -> Tuple[int, str, str]:
        """
        Executes code snippet in an ephemeral, sanitized workspace.
        Returns: (exit_code, stdout, stderr)
        """
        with cls.ephemeral_workspace() as ws:
            file_name = f"snippet{extension}"
            file_path = os.path.join(ws, file_name)
            with open(file_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(code)

            # 1. Pre-execution Static AST Security Gate
            try:
                from core.security import SecurityAuditor
                auditor = SecurityAuditor(ws)
                findings = [
                    f for f in auditor.scan_file(file_path)
                    if f.get("severity") in ("CRITICAL", "HIGH")
                ]
                if findings:
                    reasons = "; ".join(f"{f['category']}: {f['message']}" for f in findings)
                    return 126, "", f"[SANDBOX AST GATE BLOCKED] Unsafe operation in snippet: {reasons}"
            except Exception as _se:
                _log_telemetry(_se, "SovereignSandbox:ast_gate")

            # 2. Hermetic Environment & Home-Directory Jail with PEP 578 Runtime MAC Hook
            clean_env = {k: v for k, v in os.environ.items() if k.upper() in SAFE_ENV_VARS}
            clean_env.update({
                "HOME": ws,
                "USERPROFILE": ws,
                "TMP": ws,
                "TEMP": ws,
                "APPDATA": ws,
                "LOCALAPPDATA": ws,
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONPATH": ws + (os.pathsep + clean_env["PYTHONPATH"] if "PYTHONPATH" in clean_env else ""),
            })
            if extra_env:
                clean_env.update(extra_env)

            # Determine runtime command
            ext_lower = extension.lower()
            if ext_lower == ".py":
                cls._install_runtime_audit_jail(ws)
                cmd = [sys.executable or "python", file_name]
            elif ext_lower in (".js", ".ts"):
                # Try Bun first, fallback to node
                bun_bin = shutil.which("bun") or shutil.which("bun.exe")
                if bun_bin:
                    cmd = [bun_bin, "run", file_name]
                else:
                    cmd = ["node", file_name]
            elif ext_lower == ".sh":
                cmd = ["bash", file_name]
            elif ext_lower == ".ps1":
                cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", file_name]
            else:
                cmd = [file_name]

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=ws,
                    env=clean_env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout
                )
                return proc.returncode, proc.stdout, proc.stderr
            except subprocess.TimeoutExpired:
                return 124, "", f"TimeoutExpired: Execution exceeded {timeout}s limit"
            except Exception as e:
                _log_telemetry(e, f"SovereignSandbox:execute_snippet:{extension}")
                return 1, "", str(e)


def validate_loopback_url(url: str) -> bool:
    """Validate that a URL strictly targets localhost or loopback interface."""
    import ipaddress
    from urllib.parse import urlsplit
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return False
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            return False
        if parsed.hostname.lower() == "localhost":
            return True
        return ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError:
        return False


def parse_jsonrpc_request(line: str) -> Optional[Dict[str, Any]]:
    """Parse and validate an incoming JSON-RPC 2.0 request or notification."""
    stripped = line.strip()
    if not stripped:
        return None
    try:
        import json
        data = json.loads(stripped)
        if not isinstance(data, dict):
            return None
        if data.get("jsonrpc") != "2.0":
            return None
        if "method" not in data or not isinstance(data["method"], str):
            return None
        return data
    except Exception as _e:
        _log_telemetry(_e, "sandbox.py:parse_jsonrpc_request")
        return None


def format_jsonrpc_response(req_id: Any, result: Any = None, error: Optional[Dict[str, Any]] = None) -> str:
    """Format a standard JSON-RPC 2.0 response."""
    import json
    payload: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": req_id
    }
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    return json.dumps(payload)


def format_jsonrpc_error(req_id: Any, code: int, message: str, data: Any = None) -> str:
    """Format a standard JSON-RPC 2.0 error response."""
    err: Dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return format_jsonrpc_response(req_id, error=err)


def format_jsonrpc_notification(method: str, params: Any = None) -> str:
    """Format a standard JSON-RPC 2.0 notification (without id)."""
    import json
    payload: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "method": method
    }
    if params is not None:
        payload["params"] = params
    return json.dumps(payload)


def main():
    parser = argparse.ArgumentParser(description="Pillar 1: Sovereign Ephemeral Process Sandbox")
    parser.add_argument("--code", type=str, help="Inline code snippet to execute")
    parser.add_argument("--file", type=str, help="Path to code file to execute inside sandbox")
    parser.add_argument("--ext", type=str, default=".py", help="File extension (.py, .js, .ts, .sh, .ps1)")
    parser.add_argument("--timeout", type=float, default=30.0, help="Execution timeout in seconds")
    args = parser.parse_args()

    content = ""
    if args.code:
        content = args.code
    elif args.file and os.path.isfile(args.file):
        with open(args.file, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

    if not content:
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(0)
        print("Error: No code provided via --code or --file.", file=sys.stderr)
        sys.exit(1)

    code_exit, stdout, stderr = SovereignSandbox.execute_snippet(content, extension=args.ext, timeout=args.timeout)
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)
    sys.exit(code_exit)


if __name__ == "__main__":
    main()
