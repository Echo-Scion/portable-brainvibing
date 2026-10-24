@echo off
REM Cross-platform Polyglot Hook Dispatcher (Zero-Bash Python Launcher)
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python "%~dp0pre-agent-wake.py" %*
    exit /b %ERRORLEVEL%
)
python3 "%~dp0pre-agent-wake.py" %*
