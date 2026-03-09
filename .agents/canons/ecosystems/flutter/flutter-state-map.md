---
description: Flutter 4-state widget pattern using Riverpod AsyncValue. Referenced by universal skills via delegation.
ecosystem: flutter
---

# Flutter State Map (Riverpod AsyncValue)

> This is the **Flutter-specific** implementation of the universal 4-state mandate (Loading, Empty, Error, Success).

## Component State Map

When creating or auditing a Flutter widget that interacts with a backend, you MUST ensure all 4 states are handled:

```dart
// FLUTTER RIVERPOD PATTERN
Widget build(BuildContext context, WidgetRef ref) {
  final dataState = ref.watch(userDataProvider);

  return dataState.when(
    // 1. SUCCESS
    data: (user) {
      // 2. EMPTY
      if (user.isEmpty) return const EmptyStateWidget(message: 'No user found');
      return UserProfileCard(user: user);
    },
    // 3. ERROR
    error: (err, stack) => ErrorDisplayWidget(error: err),
    // 4. LOADING
    loading: () => const SkeletonProfileCard(),
  );
}
```

If you submit code that only handles the `data` state, you have failed.

## Micro-UX Checks (Flutter-Specific)
- **Actionable Error Clarity:** `ErrorDisplayWidget` must not show raw stack traces. Provide actionable steps (e.g., "Network error. Tap to retry.")
- **Disabled States:** If a submit button is disabled, visually indicate it.
- **Form Validation:** Inputs should display validation errors via `errorText` on `InputDecoration`. Ensure "required" indicators are present.
- **Destructive Actions:** Use `showDialog` for confirmation before delete/remove operations.
- **Success/Error Notifications:** Use `SnackBar` or Toast after form submissions.
