# Flutter Testing Patterns (TDD + BDD)

## 🏗️ Widget Interaction Template
```dart
testWidgets('Submit button triggers logic', (tester) async {
  await tester.pumpWidget(const MyApp());
  final button = find.byKey(const Key('submit-btn'));
  await tester.tap(button);
  await tester.pumpAndSettle(); // Wait for animations
  expect(find.text('Success'), findsOneWidget);
});
```

## 🧹 Environment Teardown
```dart
setUp(() async {
  await database.clear();
  await database.seed(testUser);
});
```

## 🛡️ QA Engineer Validations
- **Wait Protocols**: NEVER use static `sleep()` or `Future.delayed()`. Static waits cause flaky tests.
- **Condition-Based Polling**: For asynchronous states, use an active polling loop to wait for a specific condition (e.g., a widget appearing or a loading state finishing).
    ```dart
    // Example: Polling for visibility
    int retry = 0;
    while (find.byType(CircularProgressIndicator).evaluate().isNotEmpty && retry < 10) {
      await tester.pump(const Duration(milliseconds: 100));
      retry++;
    }
    ```
- **Explicit Selectors**: ALWAYS use `data-testid` or explicit `key` values for reliable automation.

---
*Preserved from Portable Brainvibing Infrastructure - Quality Suite (Upgraded with Anti-Flake Protocols)*
