# Flutter Test Recipes

When running tests, use these exact templates. Place tests in the `test/` folder mirroring the `lib/` directory structure.

## 1. Provider / Unit Test
Tests business logic in Riverpod providers without UI.

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('Initial state is correct', () {
    // 1. Create a ProviderContainer
    final container = ProviderContainer(
      overrides: [
        // TODO: Override repositories with mock data here if needed
        // myRepositoryProvider.overrideWithValue(MockRepository()),
      ],
    );
    addTearDown(container.dispose);

    // 2. Read the provider
    // final value = container.read(myProvider);
    
    // 3. Assert
    // expect(value, equals(expectedValue));
  });
}
```

## 2. Widget Test (Riverpod + GoRouter)
Tests a specific screen or widget, providing the necessary Riverpod and Router context.

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('MyScreen renders correctly', (WidgetTester tester) async {
    // 1. Setup the widget inside a ProviderScope and MaterialApp
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          // Override providers to supply test state
        ],
        child: const MaterialApp(
          home: MyScreen(),
        ),
      ),
    );

    // 2. Wait for async operations to complete if necessary
    await tester.pumpAndSettle();

    // 3. Verify elements exist
    expect(find.text('Expected Text'), findsOneWidget);
    
    // 4. Test interactions
    // await tester.tap(find.byType(ElevatedButton));
    // await tester.pumpAndSettle();
    // expect(find.text('New Text'), findsOneWidget);
  });
}
```

## 3. Running Tests
Command to execute tests and check coverage:
```bash
flutter test --coverage
```
