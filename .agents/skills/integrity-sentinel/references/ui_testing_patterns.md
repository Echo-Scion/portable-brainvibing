# UI & Component Testing Patterns (TDD + BDD)

> **Purpose**: Cross-framework test recipes for ensuring UI stability, preventing flickering/flakiness, and isolating UI states across stacks.

---

## 1. Web / React (React Testing Library & Playwright)
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

test('Submit button triggers async action safely', async () => {
  render(<FeedbackForm />);
  const submitButton = screen.getByTestId('submit-btn');
  
  fireEvent.click(submitButton);
  
  await waitFor(() => {
    expect(screen.getByText('Success')).toBeInTheDocument();
  });
});
```

---

## 2. Flutter / Dart (Widget Testing)
```dart
testWidgets('Submit button triggers logic', (tester) async {
  await tester.pumpWidget(const MyApp());
  final button = find.byKey(const Key('submit-btn'));
  await tester.tap(button);
  await tester.pumpAndSettle(); // Wait for animations
  expect(find.text('Success'), findsOneWidget);
});
```

---

## 3. Python (FastAPI / Playwright / Pytest)
```python
def test_submit_action(client):
    response = client.post("/api/v1/submit", json={"action": "test"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

---

## 4. Universal QA Validations
- **Anti-Flake Wait Protocols**: NEVER use static `sleep()` or arbitrary timeouts. Always use condition-based polling or event-driven waiting (`waitFor`, `pumpAndSettle`).
- **Stable Selectors**: ALWAYS prefer data attributes (`data-testid="submit-btn"`) or explicit semantic keys over fragile CSS classes or text matches.
- **Teardown & Isolation**: Ensure database and local state mocks are cleared in `beforeEach` / `tearDown` to guarantee test idempotency.
