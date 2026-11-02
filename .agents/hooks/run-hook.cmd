@echo off
REM Cross-platform Polyglot Hook Dispatcher (Zero-Bash Python Launcher)
where pythonw >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    pythonw "%~dp0pre-agent-wake.py" %*
    exit /b %ERRORLEVEL%
)
python3 "%~dp0pre-agent-wake.py" %*
