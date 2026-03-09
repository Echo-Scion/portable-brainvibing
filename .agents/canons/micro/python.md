---
name: python-micro
description: Micro-canon cheat sheet for Python 3.10+ typing, Pydantic v2, FastAPI, SQLite WAL, and pytest.
version: 1.0.0
---

# Python Micro-Canon & Syntax Cheat Sheet

## 1. Pydantic v2 Immutable DTO
```python
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field

class ItemDTO(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1)
```

## 2. SQLite WAL Connection Primitive
```python
import sqlite3
def get_db(path: str = "data.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn
```

## 3. FastAPI Route Pattern
```python
from fastapi import APIRouter, HTTPException, status
router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_model=list[ItemDTO])
def get_all():
    return [ItemDTO(name="Sample")]
```

## 4. Pytest Atomic Fixture
```python
import pytest
@pytest.fixture
def clean_db(tmp_path):
    db_file = str(tmp_path / "test.db")
    with get_db(db_file) as conn:
        conn.execute("CREATE TABLE items (id TEXT PRIMARY KEY, name TEXT);")
    return db_file
```
