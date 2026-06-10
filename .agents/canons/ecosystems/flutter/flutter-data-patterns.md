---
description: Flutter data modeling patterns using Freezed and Riverpod. Referenced by universal data-logic skill via delegation.
ecosystem: flutter
---

# Flutter Data & Logic Patterns (Riverpod + Freezed)

> This is the **Flutter-specific** implementation of the universal data-logic skill (immutability, DTOs, reactive state).

## JIT Tool Directives
1. Load `flutter_logic_patterns.md` for Freezed model templates and Riverpod Notifier snippets.
2. Use `grep_search` (pattern `*.dart`) to locate `domain/` and `presentation/` directories.
3. Check `pubspec.yaml` for codegen dependencies.

## Critical Validations
- **Immutability**: ALWAYS use `@freezed` for data models.
- **Optimization**: ALWAYS follow the `.select()` Rule when watching complex states.
- **Isolation**: NEVER put business logic in Widgets. Logic lives in Notifiers.
- **Safety**: NEVER use `dynamic` in models. ALWAYS call `state =` with `copyWith`.

## Workflow Patterns
1. **The .select() Rule**: Watch specific fields to prevent unnecessary rebuilds.
2. **Provider Choice**: Use `AsyncNotifier` for async state mutations and `FutureProvider` for one-off fetches.
3. **Loop Prevention**: Handle futures/streams with `.when` or `AsyncValue`.

## Troubleshooting
- **copyWith not found**: Missing `part` directive.
- **UI not rebuilding**: Using `ref.read` instead of `ref.watch`.
- **Duplicate Provider**: Multiple `@riverpod` with same name.

---
*Flutter Logic Patterns - Ecosystem Canon*
