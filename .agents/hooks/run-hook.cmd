@echo off
REM Cross-platform Polyglot Hook Dispatcher (Zero-Bash Python Launcher)
python "%~dp0pre-agent-wake.py" %*
if %ERRORLEVEL% NEQ 0 (
    python3 "%~dp0pre-agent-wake.py" %*
)
