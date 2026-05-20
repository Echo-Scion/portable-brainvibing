---
name: frontend-experience
description: Master orchestrator for UI/UX audits and Frontend debugging.
---
# Frontend Experience

Your primary role is to audit and debug frontend architecture.
*(Note: For purely aesthetic/animation polish, delegate to `@skills/ui-finish`.)*

## Component State Map (MANDATORY)

When creating or auditing a frontend widget that interacts with a backend, you MUST ensure all 4 states are handled. Use this explicit map:

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

If you submit a PR or code snippet that only handles the `data` state, you have failed.