# Refactor brain.py

Files to modify: `.agents/scripts/commands/brain.py`

## Changes
1. Use `os.environ.get("ORION_LLM_URL", "http://localhost:11434/api/generate")` for `self.endpoint`.
2. Modify `generate()` to print/log the exact exception instead of silently returning `None`.
3. Improve `ping()` to use `os.environ.get("ORION_OLLAMA_URL", "http://localhost:11434/")`.
