---
name: python-init
description: Scaffolding and project initialization protocol for Python services and CLI tools.
activation: manual
---

# Python Project Initialization Protocol

Follow this workflow when scaffolding a new Python project, backend service, or CLI tool.

## 1. Environment & Package Management
Prefer modern Python tooling (`uv` or `poetry`):
```bash
# Option A: uv (Fastest)
uv init <project_name>
cd <project_name>
uv add --dev pytest ruff mypy

# Option B: Standard venv + pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -U pip pytest ruff mypy
```

## 2. Directory Structure
Adhere to standard `src/` package layout:
```text
project_root/
├── src/
│   └── <package_name>/
│       ├── __init__.py
│       ├── core/
│       │   ├── config.py
│       │   └── exceptions.py
│       ├── api/ or cli/
│       └── services/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── README.md
```

## 3. Tooling Configuration (`pyproject.toml`)
Ensure linting and testing defaults are formalized:
```toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```
