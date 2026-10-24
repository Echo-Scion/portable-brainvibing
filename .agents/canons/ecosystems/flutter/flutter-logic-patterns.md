# Flutter Data & Logic Patterns

## 📦 Immutable Model (Freezed)
```dart
@freezed
class FeatureModel with _$FeatureModel {
  const factory FeatureModel({
    required String id,
    required String title,
    @Default([]) List<String> tags,
  }) = _FeatureModel;

  factory FeatureModel.fromJson(Map<String, dynamic> json) => _$FeatureModelFromJson(json);
}
```

## ⚡ Reactive Notifier (Riverpod Generator)
```dart
// CRITICAL: Always use @riverpod (autoDispose by default) to save memory.
@riverpod
class FeatureNotifier extends _$FeatureNotifier {
  @override
  Future<FeatureModel> build() async {
    return ref.watch(repositoryProvider).fetch();
  }

  Future<void> updateTitle(String newTitle) async {
    // Optimistic UI pattern (Snappy Feel)
    final oldState = state;
    state = AsyncData(state.value!.copyWith(title: newTitle));
  }
}
```

## 🎯 Precise UI Consumption (No Jitters Rule)
```dart
// WRONG: Entire widget rebuilds when ANY field in FeatureModel changes.
final state = ref.watch(featureNotifierProvider);

// CORRECT: Widget ONLY rebuilds when 'title' changes.
final title = ref.watch(featureNotifierProvider.select((v) => v.value?.title));
```

## 🎛️ System Daemon & Overlay Behavioral Invariants
When developing or reverse-engineering native overlays, floating controls, or background daemons:
1. **Repeatable vs. Dismissive Actions**:
   - Actions representing incremental or continuous adjustments (Volume Up/Down, Brightness Up/Down, Media Seek) MUST NOT trigger auto-dismissal of radial or overlay menus. Suppress dismissal callbacks on repeatable actions so users can tap repeatedly without reopening.
   - Dismissive actions (Home, Recents, Back, Launch App) SHOULD dismiss or stash the overlay upon execution.
2. **Multi-Orientation Coordinate Preservation**:
   - Native overlays must handle `onConfigurationChanged`.
   - Store separate relative coordinates for Portrait and Landscape modes.
   - When orientation flips, re-clamp coordinates against the new display boundaries ($x_{\min}, x_{\max}, y_{\min}, y_{\max}$) with dampened springs to prevent the floating element from being cast off-screen.

---
## 🚀 Logic Performance Guardrails
- **Minimal Rebuilds**: Always use `.select()` in complex screens to keep the main thread lean.
- **Async Safety**: Use `.when()` or `AsyncValue` to handle loading/error states without blocking the UI.
- **Memory Hygiene**: Do NOT use `keepAlive: true` unless the provider holds critical global state (e.g., Auth Session).
- **Background Heavy-Lifting**: Use `compute()` for massive JSON parsing to keep the UI at 60FPS.
