---
description: Python presentation patterns, structured error envelopes, and CLI / API UI contracts.
ecosystem: python
---

# Python UI & Presentation Patterns

Python services present interfaces either through REST/HTTP APIs or command-line (CLI) interfaces. Both require structured, predictable output contracts.

## 1. Structured API Error Envelope
Never return unhandled tracebacks or raw exception strings to clients. Implement a standard envelope:

```python
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str


class ErrorEnvelope(BaseModel):
    code: str
    message: str
    details: List[ErrorDetail] = []


def create_error_response(status_code: int, code: str, message: str, details: List[ErrorDetail] = None) -> JSONResponse:
    content = {
        "error": {
            "code": code,
            "message": message,
            "details": [d.model_dump() for d in (details or [])],
        }
    }
    return JSONResponse(status_code=status_code, content=content)
```

## 2. CLI Presentation Contract (Terminal UI)
For interactive Python scripts or tools, follow these ergonomics:
- **ANSI Stripping**: Check `sys.stdout.isatty()` before outputting terminal color codes.
- **Fail-Fast Exit Codes**: Exit `0` for complete success, `1` for validation/environment errors, `2` for syntax/CLI arg errors.
- **Progressive Output**: Use plain text tables or structured key-value lines (`[PASS] Component: Status`).

```python
import sys


def format_status(label: str, status: str, is_error: bool = False) -> str:
    use_color = sys.stdout.isatty()
    if use_color:
        color = "\033[91m" if is_error else "\033[92m"
        reset = "\033[0m"
        return f"[{color}{status}{reset}] {label}"
    return f"[{status}] {label}"
```

## 3. OpenAPI Schema Cleanliness
- Annotate every route with `response_model`, `summary`, and explicit `status_code`.
- Document query parameters with `Field(description="...")`.
- Group endpoints logically using `tags=["domain-name"]`.
