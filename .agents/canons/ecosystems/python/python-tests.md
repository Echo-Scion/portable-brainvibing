---
description: Python test recipes using pytest, fixtures, mocking, and async execution.
ecosystem: python
---

# Python Test Recipes

Write tests using `pytest`. Place test files in `tests/` mirroring the `src/` directory structure with `test_*.py` naming.

## 1. Unit & Service Test with Pytest Fixtures

```python
import pytest
from uuid import uuid4
from src.feature.domain.models import ItemCreate
from src.feature.application.service import ItemService
from src.feature.infrastructure.repository import ItemRepository


@pytest.fixture
def temp_db(tmp_path):
    db_file = str(tmp_path / "test.db")
    repo = ItemRepository(db_file)
    with repo._get_connection() as conn:
        conn.execute("""
            CREATE TABLE items (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                is_completed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );
        """)
        conn.commit()
    return db_file


@pytest.fixture
def item_service(temp_db):
    repo = ItemRepository(temp_db)
    return ItemService(repo)


def test_create_and_list_items(item_service):
    payload = ItemCreate(title="Test Task", is_completed=False)
    created = item_service.create_item(payload)

    assert created.title == "Test Task"
    assert created.is_completed is False

    items = item_service.get_items()
    assert len(items) == 1
    assert items[0].id == created.id


def test_create_blank_item_raises_error(item_service):
    with pytest.raises(ValueError, match="cannot be blank"):
        item_service.create_item(ItemCreate(title="   "))
```

## 2. API Route Test with FastAPI TestClient

```python
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.feature.presentation.router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_api_list_items_empty():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 3. Async Test Recipe (pytest-asyncio)

```python
import pytest


@pytest.mark.asyncio
async def test_async_worker_execution():
    async def sample_coro(val: int) -> int:
        return val * 2

    res = await sample_coro(21)
    assert res == 42
```
