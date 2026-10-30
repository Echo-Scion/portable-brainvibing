---
activation: model_decision
description: Jetpack Compose declarative UI standards, @Composable state hoisting, and @Preview sidecar integration.
last_updated: 2026-10-29
---

# Jetpack Compose UI Standards & Preview Conventions

> **Opt-In Module**: Applicable to projects utilizing `androidx.compose` and declarative Kotlin UI.

## 1. Composable Function Architecture
- **State Hoisting**: Screen composables MUST be split into:
  1. **Stateful Container**: Injects ViewModel, collects `uiState`, and passes lambda event callbacks downward.
  2. **Stateless Content Component**: Accepts pure values and lambda callbacks (`onClick: () -> Unit`). All UI logic and layout rendering happen here.
- **Placement**: UI composables MUST reside in `app/src/main/java/<package>/ui/` or modular `feature/` presentation packages.

## 2. Mandatory `@Preview` Standard
To enable zero-runtime visual iteration in Antigravity's **Android Compose Preview** sidecar without booting a full emulator, every user-facing Composable MUST define a paired `@Preview`:

```kotlin
@Preview(name = "Light Mode", showBackground = true)
@Preview(name = "Dark Mode", uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun UserProfileScreenPreview() {
    AppTheme {
        UserProfileContent(
            state = UserProfileUiState.Success(name = "Alice"),
            onAction = {}
        )
    }
}
```

## 3. Preview Constraints
- `@Preview` functions MUST NOT instantiate ViewModels, Room databases, or network clients.
- Complex or parameterized data MUST utilize `PreviewParameterProvider<T>` or static mock fixtures.
- Antigravity AI agents can trigger rendering directly via the `Android Compose Preview` sidecar panel without invoking a full build/deploy cycle.
