---
description: Concrete steps to build, test, and release a Python application or service to production.
ecosystem: python
---

# Workflow: Python Production Release (`/python-release`)

Follow these concrete steps when preparing a Python package, microservice, or CLI tool for release.

## 1. Pre-Flight Verification Gate
Execute all verification commands sequentially. Every check must exit with code 0:

```bash
# 1. Formatting and linting checks
ruff check .
ruff format --check .

# 2. Strict type checking
mypy src

# 3. Complete test suite with coverage
pytest --cov=src --cov-report=term-missing

# 4. Dependency vulnerability scan
pip-audit
```

If any command fails, halt the release immediately and resolve errors.

## 2. Artifact Build

### Target A: Python Package (Wheel / Source Distribution)
```bash
python -m build
```
*Output: `dist/*.whl` and `dist/*.tar.gz`*
Verify with `twine check dist/*`.

### Target B: Production Docker Container
```bash
docker build -t service:latest -f Dockerfile .
docker run --rm service:latest pytest
```

## 3. Production Deployment Notes
- Ensure environment variables are loaded via `.env` or cloud secret managers, never committed to git.
- Verify production logging emits structured JSON or timestamped streams.
- If using SQLite in production, ensure WAL mode is permanently enabled and backup snapshots use the SQLite Online Backup API.
