#!/usr/bin/env sh
# Cross-platform Unix/macOS Hook Dispatcher (Zero-Bash Python Launcher)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v python >/dev/null 2>&1; then
    python "$SCRIPT_DIR/pre-agent-wake.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    python3 "$SCRIPT_DIR/pre-agent-wake.py" "$@"
fi
