# Condition-Based Waiting vs. Arbitrary Delay

> **Core Principle**: Wait for the actual condition or state transition you care about, not an arbitrary guess about wall-clock timing.

---

## 1. The Anti-Pattern: Arbitrary Sleeps

Flaky tests often guess at timing with arbitrary delays (`time.sleep(1.0)`, `setTimeout(..., 50)`, `await Task.delay(100)`).
- On fast developer laptops, the test passes.
- Under heavy load, in CI runners, or across platforms, the test fails intermittently.

```python
# ❌ BEFORE: Guessing at timing
time.sleep(0.5)
assert queue.is_empty() is True

# ✅ AFTER: Polling condition with timeout
assert wait_for(lambda: queue.is_empty(), timeout_s=5.0) is True
```

---

## 2. Universal Polling Implementation (Python Stdlib)

```python
import time
from typing import Callable, TypeVar, Optional

T = TypeVar("T")

def wait_for(
    condition: Callable[[], T],
    description: str = "condition",
    timeout_s: float = 5.0,
    poll_interval_s: float = 0.02,
) -> T:
    """Poll condition until truthy or timeout expires."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        res = condition()
        if res:
            return res
        time.sleep(poll_interval_s)
    raise TimeoutError(f"Timed out after {timeout_s}s waiting for {description}")
```

---

## 3. When Fixed Timeout IS Correct

Fixed delays are justified **only** when asserting actual timing behavior:
- Verifying that a debounce or throttle window rejects calls within the first $N$ ms.
- Protocol: First wait for the start condition using `wait_for()`, and only then execute the fixed delay to verify debounce behavior. Always document `WHY` in the test comment.
