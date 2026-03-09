# Flutter Feature Recipe

When generating a new feature, ALWAYS use this standard Riverpod + Freezed architecture. Do not hallucinate different file structures.

## 1. Domain/Model Layer (`lib/features/[name]/data/models/[name].dart`)
Always use `@freezed` for models.

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part '[name].freezed.dart';
part '[name].g.dart';

@freezed
class [Name] with _$[Name] {
  const factory [Name]({
    required String id,
    required String title,
    @Default(false) bool isCompleted,
    DateTime? createdAt,
  }) = _[Name];

  factory [Name].fromJson(Map<String, dynamic> json) => _$[Name]FromJson(json);
}
```

## 2. Data/Repository Layer (`lib/features/[name]/data/repositories/[name]_repository.dart`)
Handle external data sources here. Use `riverpod_annotation`.

```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/[name].dart';

part '[name]_repository.g.dart';

@riverpod
[Name]Repository [name]Repository([Name]RepositoryRef ref) {
  return [Name]Repository();
}

class [Name]Repository {
  Future<List<[Name]>> fetchAll() async {
    // TODO: Implement actual fetch logic (Supabase, API, etc.)
    await Future.delayed(const Duration(seconds: 1));
    return [];
  }
}
```

## 3. Presentation/Provider Layer (`lib/features/[name]/presentation/providers/[name]_provider.dart`)
Manage state using `AsyncNotifier`.

```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../data/models/[name].dart';
import '../../data/repositories/[name]_repository.dart';

part '[name]_provider.g.dart';

@riverpod
class [Name]List extends _$[Name]List {
  @override
  FutureOr<List<[Name]>> build() async {
    return ref.watch([name]RepositoryProvider).fetchAll();
  }

  Future<void> add([Name] item) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      // TODO: Add to repository
      final current = state.valueOrNull ?? [];
      return [...current, item];
    });
  }
}
```

## 4. Presentation/Screen Layer (`lib/features/[name]/presentation/screens/[name]_screen.dart`)
Implement the 5-state rule (Loading, Error, Success, Empty).

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/[name]_provider.dart';

class [Name]Screen extends ConsumerWidget {
  const [Name]Screen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch([name]ListProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('[Name]')),
      body: state.when(
        data: (items) {
          if (items.isEmpty) {
            return const Center(child: Text('No items found.'));
          }
          return ListView.builder(
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              return ListTile(title: Text(item.title));
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(child: Text('Error: $err')),
      ),
    );
  }
}
```

## 5. Generator Execution
After writing the above files, ALWAYS run:
```bash
dart run build_runner build -d
```
