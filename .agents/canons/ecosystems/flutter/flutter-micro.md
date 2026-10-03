# Micro-Canon: Flutter 3.x (≤50 lines — Budget Model Cheat Sheet)
> Source: .agents/rules/flutter-standards.md

## STATE MANAGEMENT (Riverpod 2.x)
- DO: `@riverpod` annotation + `ref.watch()` for reactive state
- DO: `AsyncNotifierProvider` for async operations (not `FutureProvider` for complex state)
- DONT: `setState()` in anything larger than a leaf widget
- SYNTAX: `final counterProvider = NotifierProvider<Counter, int>(Counter.new);`

## NAVIGATION (GoRouter)
- DO: `context.go('/path')` — replaces stack
- DO: `context.push('/path')` — adds to stack
- DONT: `Navigator.push()` in apps using GoRouter (conflicts with deep-link state)
- SYNTAX: `GoRoute(path: '/home', builder: (ctx, state) => const HomeScreen())`

## DATA / IMMUTABILITY (Freezed)
- DO: `@freezed` for all data models
- DO: `.copyWith()` for mutations — never mutate directly
- DONT: mutable `class` with `setState` for business data
- SYNTAX: `@freezed class User with _$User { const factory User({required String id}) = _User; }`

## ASYNC PATTERNS
- DO: `AsyncValue<T>` for loading/error/data tri-state
- DO: `.when(data: ..., loading: ..., error: ...)` for UI branching
- DONT: raw `FutureBuilder` in Riverpod apps — use `AsyncNotifier`

## COMMON PITFALLS (DO NOT HALLUCINATE THESE)
- `ref.read()` → one-time read, use inside callbacks/methods only
- `ref.watch()` → reactive, use inside `build()` only
- `ref.listen()` → side effects (navigation, snackbar), NOT in build
- `invalidate(provider)` → force refresh; `refresh(provider)` → returns new value

## WIDGET PATTERNS
- DO: `const` constructors wherever possible (performance)
- DO: Extract widgets to separate classes, not inline functions
- DONT: `Column` inside `SingleChildScrollView` without `mainAxisSize: MainAxisSize.min`
- DONT: `Expanded` outside `Flex` context (crashes at runtime)

## PERFORMANCE GUARDS
- DO: `RepaintBoundary` around heavy custom painters
- DO: `AutomaticKeepAliveClientMixin` for tabs that must not re-render
- DONT: `setState()` at the root/page level for localized changes
