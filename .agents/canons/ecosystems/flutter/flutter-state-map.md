---
description: Flutter 4-state widget pattern using Riverpod AsyncValue. Referenced by universal skills via delegation.
ecosystem: flutter
---

# Flutter State Map (Riverpod AsyncValue)

> This is the **Flutter-specific** implementation of the universal 4-state mandate (Loading, Empty, Error, Success).

## Component State Map

When creating or auditing a Flutter widget that interacts with a backend, you MUST ensure all 4 states are handled:

```dart
// FLUTTER RIVERPOD 6-FAMILY STATE MACHINE PATTERN
Widget build(BuildContext context, WidgetRef ref) {
  final dataState = ref.watch(userListProvider);
  final activeQuery = ref.watch(searchQueryProvider);

  return dataState.when(
    data: (users) {
      // 1. FIRST-TIME EMPTY: Orientation + Primary Create CTA
      if (users.isEmpty) {
        return EmptyStateWidget(
          title: 'No users yet',
          description: 'Invite team members to collaborate on this workspace.',
          actionLabel: 'Invite user',
          onAction: () => _openInviteDialog(context),
        );
      }
      final filtered = users.where((u) => u.matches(activeQuery)).toList();
      // 2. FILTERED-TO-EMPTY: Name query + Reset filter action
      if (filtered.isEmpty) {
        return EmptyStateWidget(
          title: 'No results for "$activeQuery"',
          description: 'Try a different search term or clear active filters.',
          actionLabel: 'Clear filters',
          onAction: () => ref.read(searchQueryProvider.notifier).clear(),
        );
      }
      // 3. POPULATED (Truncation-safe rows)
      return UserListView(users: filtered);
    },
    // 4. INSTRUCTIONAL ERROR + RETRY RECOVERY
    error: (err, stack) => ErrorDisplayWidget(
      title: 'Unable to load users',
      instruction: 'Check your connection and try again.',
      onRetry: () => ref.invalidate(userListProvider),
    ),
    // 5. SKELETON LOADING (Preserves layout geometry)
    loading: () => const SkeletonUserList(),
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
