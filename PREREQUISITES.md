# Foundation Prerequisites & Fallback Mechanics

This framework is **plug-and-play**. All dependencies except Python are **completely optional** and have automatic fallbacks.

## 🏁 The Absolute Minimum (Zero-Configuration Fallback)
If you only have Python, the system falls back gracefully:
- **No Ollama**: The context engine (`brain.py`) searches files via keyword matching instead of semantic GraphRAG triplets.
- **No RTK**: Commands execute normally directly in the terminal without output compression.
- **Zero Interruptions**: Integrity tests (`verify_agents.py`) will issue a warning but still output `[PASS]` (`Exit Code 0`).

To unlock full capabilities, install the optional dependencies below.


## 1. Python 3.10+
Used for the Neuro-Link Engine (`brain.py`) and foundation validation scripts (e.g., `verify_agents.py`).
- **Windows**: `winget install Python.Python.3.12` or download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python`
- **Linux (Debian/Ubuntu)**: `sudo apt install python3 python3-pip`

## 2. Node.js (npm)
Used for the project ecosystem if applicable.
- **Windows**: `winget install OpenJS.NodeJS`
- **macOS**: `brew install node`
- **Linux**: `sudo apt install nodejs npm`

## 3. Rust (RTK Token Killer)
Used for token-optimized CLI proxying (60-90% savings).
- **All OS**: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- **Install RTK**: (Ensure you install the correct RTK binary, not the Rust Type Kit)

## 4. Nano Brain (Ollama)

> [!WARNING]
> **Manual OS-Level Installation Required**: NanoBrain (Ollama) is a separate OS-level binary. The `.agents` framework cannot auto-install it. You MUST install Ollama globally from ollama.com and ensure it is in your Windows (or host OS) PATH before it can be used.

Used for GraphRAG operations, Caveman Compression, and instant context processing without burning token budgets.
- **Windows / macOS**: Download from [ollama.com](https://ollama.com/download)
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`
- **Install Nano Model**: `ollama pull qwen2.5:0.5b`

## 5. Ecosystem-Specific (Optional)
Depending on your target project, ensure the appropriate SDK is installed.

### Flutter (If building Flutter Apps)
- **Windows / macOS / Linux**: Follow the official guide at [flutter.dev](https://docs.flutter.dev/get-started/install)

### Node.js / React (If building Web Apps)
- Uses the Node.js installation from Step 2.
