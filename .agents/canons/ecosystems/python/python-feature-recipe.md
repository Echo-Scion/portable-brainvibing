---
description: Standard Python / FastAPI feature architecture using Pydantic v2, Service Layer, and Repository pattern.
ecosystem: python
---

# Python Feature Recipe

When generating a new Python backend module or feature, ALWAYS follow this 3-layer architecture. Maintain strict type hints (`typing` / `mypy` compliant) and immutable DTOs.

## 1. Domain & DTO Layer (`src/[feature]/domain/models.py`)
Use Pydantic v2 for data transfer objects with runtime validation:

```python
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=120)
    is_completed: bool = False


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## 2. Repository Layer (`src/[feature]/infrastructure/repository.py`)
Encapsulate all database / I/O access behind an explicit interface:

```python
import sqlite3
from typing import List, Optional
from uuid import UUID
from ..domain.models import ItemRead, ItemCreate


class ItemRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def list_all(self) -> List[ItemRead]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT id, title, is_completed, created_at FROM items ORDER BY created_at DESC")
            return [
                ItemRead(
                    id=row[0],
                    title=row[1],
                    is_completed=bool(row[2]),
                    created_at=row[3],
                )
                for row in cursor.fetchall()
            ]

    def create(self, item: ItemCreate) -> ItemRead:
        record = ItemRead(**item.model_dump())
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO items (id, title, is_completed, created_at) VALUES (?, ?, ?, ?)",
                (str(record.id), record.title, int(record.is_completed), record.created_at.isoformat()),
            )
            conn.commit()
        return record
```

## 3. Service Layer (`src/[feature]/application/service.py`)
Place core business logic here. Services orchestrate repositories and domain validation:

```python
from typing import List
from ..domain.models import ItemCreate, ItemRead
from ..infrastructure.repository import ItemRepository


class ItemService:
    def __init__(self, repository: ItemRepository):
        self.repository = repository

    def get_items(self) -> List[ItemRead]:
        return self.repository.list_all()

    def create_item(self, item_input: ItemCreate) -> ItemRead:
        # Business logic / domain checks
        cleaned_title = item_input.title.strip()
        if not cleaned_title:
            raise ValueError("Item title cannot be blank.")
        return self.repository.create(item_input)
```

## 4. API Presentation Layer (`src/[feature]/presentation/router.py`)
Expose clean FastAPI / CLI endpoints:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..domain.models import ItemCreate, ItemRead
from ..application.service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


def get_item_service() -> ItemService:
    # Factory / dependency injection point
    from ..infrastructure.repository import ItemRepository
    return ItemService(ItemRepository("data.db"))


@router.get("", response_model=List[ItemRead])
def list_items(service: ItemService = Depends(get_item_service)):
    return service.get_items()


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, service: ItemService = Depends(get_item_service)):
    try:
        return service.create_item(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```
