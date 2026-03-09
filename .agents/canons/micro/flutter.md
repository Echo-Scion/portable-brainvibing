---
name: flutter-micro
description: Micro-canon cheat sheet for Flutter Riverpod 2.x, Freezed, GoRouter, and common syntax traps.
version: 1.0.0
---

# Flutter Micro-Canon & Syntax Cheat Sheet

## 1. Riverpod 2.x Syntax

### AsyncNotifier Pattern
```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'item_provider.g.dart';

@riverpod
class ItemListNotifier extends _$ItemListNotifier {
  @override
  FutureOr<List<Item>> build() async {
    return _fetchItems();
  }

  Future<void> addItem(Item item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await ref.read(itemRepositoryProvider).add(item);
      return _fetchItems();
    });
  }
}
```

### UI Consumption
```dart
class ItemListView extends ConsumerWidget {
  const ItemListView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final itemsAsync = ref.watch(itemListNotifierProvider);

    return itemsAsync.when(
      data: (items) => items.isEmpty 
          ? const EmptyStateWidget(message: "No items found") 
          : ListView.builder(
              itemCount: items.length,
              itemBuilder: (ctx, i) => ItemTile(item: items[i]),
            ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, stack) => ErrorRetryWidget(
        error: err.toString(),
        onRetry: () => ref.invalidate(itemListNotifierProvider),
      ),
    );
  }
}
```

## 2. GoRouter Route Configuration
```dart
final goRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authNotifierProvider);

  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final isLoggedIn = authState.asData?.value != null;
      final isLoggingIn = state.matchedLocation == '/login';

      if (!isLoggedIn && !isLoggingIn) return '/login';
      if (isLoggedIn && isLoggingIn) return '/';
      return null;
    },
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
    ],
  );
});
```

## 3. Common Syntax Traps
- **No `setState` in ConsumerWidget**: Always update state via `Notifier` or `ref.read(provider.notifier)`.
- **ListView in Column**: Always wrap in `Expanded` or specify `shrinkWrap: true`.
- **Heavy JSON Parsing**: Always dispatch to `compute(parseJson, rawData)` to prevent dropping frames.
- **Context across async gaps**: Always check `if (!context.mounted) return;` after `await`.
