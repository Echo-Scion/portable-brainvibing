---
name: python-standards
description: Python code standards, type annotations, error handling, and testing guidelines.
activation: glob
globs: *.py
---

# Python Development Standards & Guidelines

## 1. Type Annotations & Static Analysis
- Annotate all function signatures and public APIs with strict Python type hints (`typing` / built-ins in Python 3.10+).
- Use `mypy` or `pyright` for static type verification.
- Use `dataclasses` or `pydantic` models for structured data transfer objects. Avoid raw untyped dictionaries for internal contracts.

## 2. Formatting & Linting
- Enforce `ruff` for linting and formatting (replaces flake8, isort, and black).
- Maximum line length: 88 characters.
- Use explicit exception types. Never catch bare `except:`.

## 3. Asynchronous Code (`asyncio`)
- Never run blocking I/O calls (e.g. `time.sleep()`, synchronous `requests.get()`, heavy disk writes) inside async event loops.
- Use `asyncio.to_thread` for CPU-bound or legacy synchronous library integrations.
- Always set explicit timeouts on network connections (`httpx.AsyncClient(timeout=10.0)`).

## 4. Testing & Verification
- Organize tests using `pytest`. Place fixtures in `tests/conftest.py`.
- Target >= 80% test coverage on business logic.
- Mock external APIs and databases in unit tests using `pytest-mock` or `unittest.mock`.
