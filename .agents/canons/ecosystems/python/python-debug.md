---
description: Systematic debugging workflows for Python applications, concurrency, and SQLite locks.
ecosystem: python
---

# Python Debugging Workflow

Follow this procedure when diagnosing Python crashes, unhandled tracebacks, or concurrency locks.

## 1. Traceback Isolation & Root-Cause Parsing
1. **Find the Origin Frame**: Trace to the bottom-most file path inside project directories (`src/`), ignoring standard library or virtualenv wrapper frames.
2. **Type Discrepancy Checks**: Check for `NoneType` attribute access (`'NoneType' object has no attribute '...'`) caused by unverified dict gets or missing repository returns.
3. **Pydantic Validation Failures**: Inspect `ValidationError.errors()` to locate missing required keys or string-to-UUID parsing mismatches.

## 2. SQLite Concurrency & Lock Debugging
**Symptom**: `sqlite3.OperationalError: database is locked`.

### Diagnostic Steps:
1. **Verify WAL Mode**: Run `PRAGMA journal_mode;` on the database file. If output is `delete`, immediately execute `PRAGMA journal_mode=WAL;`.
2. **Enforce Busy Timeout**: Ensure all connections set `PRAGMA busy_timeout=5000;`. Connections without this fail immediately on transient write locks.
3. **Close Leaked Cursors/Connections**: Audit code for unmanaged `sqlite3.connect` calls outside context managers (`with conn:`).

## 3. Asyncio Event Loop Profiling
**Symptom**: Server stops responding or latency spikes under light load.

### Diagnostic Steps:
1. **Blocking Synchronous Calls**: Check for synchronous I/O (`time.sleep()`, synchronous `requests.get()`, heavy disk writes) executed inside `async def` routes.
2. **Fix**: Wrap synchronous blocking calls in `asyncio.to_thread()` or switch to native async equivalents (`asyncio.sleep()`, `httpx.AsyncClient`).
3. **Unhandled Tasks**: Ensure all spawned background tasks (`asyncio.create_task()`) are held in a reference set to prevent garbage collection before completion.
