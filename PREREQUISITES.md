# Foundation Prerequisites & Fallback Mechanics

This framework is **plug-and-play**. All dependencies except Python are **completely optional** and have automatic fallbacks.

## 🏁 The Absolute Minimum (Zero-Configuration Fallback)
If you only have Python, the system falls back gracefully:
- **No Ollama**: The context engine (`orion.py`) searches files via SQLite FTS5 lexical matching instead of semantic vector embeddings.
- **No RTK / ast-grep**: Commands execute normally without CLI output compression; structural queries fallback to Python stdlib `ast` and regex.
- **No Bun**: Dynamic TypeScript execution and MCP servers fallback to system Node/npx or pure Python stdlib.
- **Zero Interruptions**: Integrity tests (`verify_agents.py`) pass cleanly (`Exit Code 0`).

To unlock full capabilities across all four anchored foundation pillars, install the static utilities below.


## 1. Pillar 1: Python 3.10+ (Zero-Pip Master Orchestrator)
Used for Context & Brain Engine (`orion.py`), SQLite3 FTS5 GraphRAG, and validation gates (`verify_agents.py`).
- **Windows**: `winget install Python.Python.3.12` or download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python`
- **Linux (Debian/Ubuntu)**: `sudo apt install python3`
- *Mandate*: Zero-Pip — all core algorithms run on pure standard library.

## 2. Pillar 2: Cargo Rust Systems Engine (`rtk` + `ast-grep`)
Used for token-optimized CLI proxying (60-90% token reduction) and polyglot Concrete Syntax Tree (CST) structural code intelligence.
- **Install Rust toolchain**:
  - `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- **Install RTK**:
  - `cargo install --git https://github.com/rtk-ai/rtk`
- **Install ast-grep (`sg`)**:
  - `cargo install ast-grep --locked` or `winget install ast-grep`

## 3. Pillar 3: Local Neural Coprocessor (Ollama / llama.cpp / OpenAI-Compatible)

Used for zero-cloud local vector embeddings (`nomic-embed-text`) and heuristic SLM evaluation.
Supports multiple runtimes:
- **Ollama** (Default daemon on `127.0.0.1:11434`): Download from [ollama.com](https://ollama.com/download)
- **llama.cpp (`llama-server`)** (Standalone single binary on `127.0.0.1:8080`): Download official release executable from [github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp/releases) and place in PATH or `.agents/bin/`
- **LM Studio / vLLM / LocalAI** (OpenAI-compatible server on `127.0.0.1:1234` or `127.0.0.1:8000`)
- **Install Embedding Model**: `ollama pull nomic-embed-text`
- **Install Coder Model**: `ollama pull qwen2.5-coder:1.5b` (or `7b` for higher VRAM)

## 4. Pillar 4: Bun Static Runtime Engine (`bun`)
Used for zero-compile TypeScript execution, instant zero-install Model Context Protocol (MCP) server launching (`bun x -y`), microsecond mutation test execution (`bun test` in <4ms), and headless UI contract evaluation without heavy `node_modules` pollution.
- **Windows**: `powershell -c "irm bun.sh/install.ps1 | iex"` or place `bun.exe` into `.agents/bin/`
- **macOS / Linux**: `curl -fsSL https://bun.sh/install | bash`
- **Verify**: `bun --version` or `python .agents/scripts/orion.py bun status`

## 5. Ecosystem-Specific (Optional)
Depending on your target project, ensure the appropriate SDK is installed:

### Flutter & Android (If building Mobile Apps)
- **Flutter SDK**: Follow the official guide at [flutter.dev](https://docs.flutter.dev/get-started/install)
- **Android SDK & Command-Line Tools**: Configured via Android Studio or command-line SDK manager.
