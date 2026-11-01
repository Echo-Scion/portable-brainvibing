# Canon: Standalone CLI Bot Architecture

> ⚠️ CRITICAL COUPLING: This canon defines the non-negotiable architectural invariants for all headless bots, daemons, workers, and command-line automation utilities across all programming languages.

## 1. Overview
Standalone CLI bots run unattended in headless environments (cron, systemd, Docker, Kubernetes, CI/CD runners, Windows Task Scheduler). Unlike interactive UI applications, CLI bots communicate with operating system process managers, pipes, and downstream consumers. 

This canon establishes 5 foundational invariants for building robust, defensible, and observable CLI bots.

---

## 2. Invariant 1: Headless Execution & Non-Interactive Safety

CLI bots must never stall waiting for interactive input when executing unattended.

1. **TTY Detection**:
   - Detect whether `stdin` is connected to an interactive terminal (`stdin.hasTerminal` in Dart, `sys.stdin.isatty()` in Python, `process.stdin.isTTY` in Node).
   - If `stdin` is NOT a TTY and required input is missing, fail fast immediately. Never block execution.
2. **Flag Overrides**:
   - Support a `--non-interactive` (or `-y` / `--yes`) flag to suppress interactive confirmations.
3. **Execution Timeout**:
   - Every blocking I/O operation (network fetch, child process spawn, file lock acquisition) must enforce an explicit deadline/timeout.

```dart
// Example: Dart TTY Safety Check
import 'dart:io';

void assertNonInteractiveSafe({required bool nonInteractiveFlag}) {
  final isInteractive = stdin.hasTerminal && !nonInteractiveFlag;
  if (!isInteractive && stdinRequiresPrompt()) {
    stderr.writeln('ERROR: Missing required arguments in non-interactive environment.');
    exit(2); // Configuration/Input error
  }
}
```

---

## 3. Invariant 2: Stream Routing & Machine Observability

CLI bots adhere to strict stream separation to allow composition via Unix pipes (`bot | jq .`):

| Stream | Allowed Content | Prohibited Content |
| :--- | :--- | :--- |
| `stdout` | **Pure Machine Data Only**: JSON, NDJSON, CSV, or raw binary payloads. | Progress spinners, ANSI colors, log timestamps, warnings. |
| `stderr` | **Telemetry & Diagnostics**: Structured logs, debug traces, progress bars, errors. | Machine-consumed output payloads. |

### NDJSON Event Streaming Pattern
For long-running bots emitting event streams, write newline-delimited JSON (NDJSON) to `stdout`:
```json
{"timestamp":"2026-11-01T04:00:00Z","type":"heartbeat","status":"healthy"}
{"timestamp":"2026-11-01T04:00:05Z","type":"task_completed","task_id":"sync_42","records":120}
```

---

## 4. Invariant 3: Lifecycle & Graceful Signal Handling

Processes running as daemons or scheduled tasks receive OS termination signals (`SIGINT`, `SIGTERM`). Bots must capture these signals, drain in-flight operations, and exit cleanly.

### Mandatory Teardown Sequence:
1. **Intercept Signal**: Register signal handlers immediately upon startup.
2. **Stop Ingestion**: Cease polling new work from message queues or file watchers.
3. **Drain Active Unit of Work**: Allow currently executing atomic step to complete (within grace period).
4. **Flush Buffers & Release Locks**: Flush file buffers, commit or rollback SQLite/DB transactions, and delete lock files.
5. **Hard Timeout Fallback**: If graceful shutdown exceeds deadline (default: 5–10s), force terminate with exit code 1.

```dart
// Example: Dart Signal Handling and Graceful Drain
import 'dart:async';
import 'dart:io';

class BotRunner {
  bool _isShuttingDown = false;
  Completer<void>? _activeTask;

  void initLifecycle() {
    ProcessSignal.sigint.watch().listen((_) => _shutdown('SIGINT', 130));
    ProcessSignal.sigterm.watch().listen((_) => _shutdown('SIGTERM', 143));
  }

  Future<void> _shutdown(String signal, int exitCode) async {
    if (_isShuttingDown) return;
    _isShuttingDown = true;
    stderr.writeln('\n[BOT] Received $signal. Initiating graceful shutdown...');

    try {
      // Wait up to 5 seconds for active task to drain
      await _activeTask?.future.timeout(const Duration(seconds: 5));
      await _releaseResources();
      stderr.writeln('[BOT] Clean shutdown complete.');
      exit(exitCode);
    } catch (e) {
      stderr.writeln('[BOT] Forced termination during shutdown: $e');
      exit(1);
    }
  }

  Future<void> _releaseResources() async {
    // Release file locks, close DB connections, flush streams
  }
}
```

---

## 5. Invariant 4: Deterministic Exit Code Matrix

Processes must communicate execution status deterministically via standardized POSIX-compliant exit codes:

| Exit Code | Meaning | Typical Scenarios |
| :---: | :--- | :--- |
| **`0`** | **Success** | Task completed successfully without errors. |
| **`1`** | **General Operational Error** | Unhandled runtime exception, unrecoverable data error. |
| **`2`** | **Invalid Usage / Configuration** | Missing required CLI flag, malformed JSON input, non-TTY stall. |
| **`3`** | **External Dependency Failure** | Network timeout, database down, upstream API 5xx, circuit breaker tripped. |
| **`130`** | **Terminated by `SIGINT`** | Interrupted by user keyboard (`Ctrl+C`, 128 + 2). |
| **`143`** | **Terminated by `SIGTERM`** | Stopped by daemon supervisor / systemd / container manager (128 + 15). |

---

## 6. Invariant 5: Unattended Automation & Concurrency Guards

When running on schedules (cron / systemd timers):

1. **Single-Instance Concurrency Guard**:
   - Use atomic file locks (`flock`, lockfiles) to prevent duplicate runs from overlapping when a job takes longer than its schedule interval.
2. **Circuit Breakers & Exponential Backoff**:
   - If downstream services fail consecutively, back off exponentially ($2^n \times \text{base delay}$) up to a max cap.
   - Stop execution after 3-5 consecutive failures and alert via `stderr`.
3. **Environment & Secrets Precedence**:
   - Configuration priority: CLI Flags > Environment Variables (`APP_*`) > Local `.env` (development only) > Default Fallbacks.
   - Never log secrets, auth tokens, or private keys to `stderr` or `stdout`.

---
*Global Foundation Protocol - Autonomous Execution Engine*
