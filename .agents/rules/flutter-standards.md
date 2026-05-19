---
activation: glob
description: Comprehensive Flutter architecture, development standards, and styling guidelines.
globs: *.dart

version: 2.4.0
last_updated: 2026-05-20
---

# Flutter Hybrid Architecture

## 1. Modular Structure
- Separate the application into clear layers: Data, Domain, and Presentation.
- Use a features-driven directory structure: `lib/src/features/[feature]/`.
- Isolate platform-specific logic using interfaces or conditional imports.
- Barrel exports: each feature exposes a single `[feature].dart` export file.

## 2. Navigation (go_router)
- Use `go_router` with `ShellRoute` for persistent bottom nav bars.
- Define all routes in a central `router.dart` using `GoRoute`.
- Implement auth guards via `redirect` callback: check auth state in `RouterNotifier`.
- Support deep linking by registering URL schemes in Android/iOS manifests.

## 3. Hybrid Patterns (Multi-Platform)
- **Cross-Platform Realtime Sync**: MANDATORY use of **Supabase Realtime Channels** to sync state instantly between Web (Next.js) and Mobile (Flutter) without polling.
- **Thread Isolation (60FPS Rule)**: For heavy data transformations (JSON parsing/Image processing), ALWAYS use `compute()` or `Isolate` on Mobile to keep the main UI thread free from jitters.
- **Web Shell Interop**: Use `dart:js_interop` for web shell communication and `Web Workers` for background heavy-lifting in Web environments.
- **Type-Safe Native Bridge**: Use **Pigeon** for native mobile APIs (Android/iOS) to prevent runtime type errors and IPC overhead.
- **Unified Logic Layer**: Maintain a shared Riverpod state layer, but isolate platform-specific implementation (e.g., File Storage vs LocalStorage) behind an interface.

## 4. Testing Strategy
- Unit tests for all Notifiers and Services (target ≥80% coverage).
- Widget tests for all critical user flows.
- Golden tests for UI regression: `flutter test --update-goldens` on design changes.
- Integration tests using `patrol` for E2E flows on device.



# Flutter Development Standards (Antigravity)

## 1. Aesthetic-First Prototyping (The "Liquid Glass" Principle)
- **Premium Craftsmanship**: Every pixel and architecture choice must be intentional. Avoid basic implementations; optimize for both 60fps animations and low memory footprint.
- **Glassmorphism & Polish**: Leverage `ui-finish` to build beautiful visual frameworks (Liquid Glass) with micro-interactions early in the lifecycle.
- **Theme Consistency**: Strictly use project design tokens (`Theme.of(context)`) to maintain the Antigravity aesthetic.

## 2. Structural & UI Excellence
- **Visual State Mapping**: Every UI component MUST account for and implement all states: Loading, Empty, Success, Error, and Shimmer (using `Skeleton` or similar).
- **Accessibility (A11y)**: All code MUST be compliant with WCAG 2.1 AA standards. Use proper `Semantics` labels, ensure color contrast, and support keyboard/screen reader navigation.

## 3. Unidirectional Data Flow / UDF (The "One-Way Street" Principle)
- **Mandate**: All state MUST flow in one direction: **Model -> UI**. Events flow **UI -> Model**.
- **Riverpod 2.x**: Formalize logic in `AsyncNotifier` or `Notifier` to manage state predictably.
- **Reactive Mapping**: Every state change MUST be traceable through a central provider. This simplifies agent understanding of the codebase.

## 4. Widget Design
- Favor Composition over Inheritance.
- Use `const` whenever possible to optimize performance.
- Modularize UI components into small, reusable widgets (<150 lines per widget file).
- Never put business logic inside `build()` — extract to Notifiers or Services.

## 5. File & Naming Conventions
- Feature-driven structure: `lib/src/features/[feature_name]/`
  - `data/` — repositories, data sources, DTOs
  - `domain/` — models (Freezed), use cases
  - `presentation/` — widgets, providers, screens
- File names: `snake_case.dart`. Class names: `PascalCase`.
- Providers: `[featureName]Provider`, Notifiers: `[FeatureName]Notifier`.

## 6. Error Handling
- Use structured error handling (`AsyncValue.error`) in providers.
- Provide user-friendly error messages for common failure scenarios.
- Log critical errors with sufficient context for debugging.
- Never use empty `catch {}` blocks — at minimum, rethrow or log.

## 7. Performance Optimization
- **Speed Targets**: Target load times under 1.5 seconds and maintain consistent 60fps during transitions.
- Optimize build methods to avoid unnecessary rebuilds (`select()` over `watch()`).
- Use image caching (`cached_network_image`) for network assets.
- Use `ListView.builder` (never `ListView` with children) for dynamic lists.



# Dart & Flutter Style Guide

## 1. Formatting & Linting
- Use `flutter format .` regularly.
- Follow `package:flutter_lints` or `package:very_good_analysis`.
- Avoid `relative` imports; use `package:` imports.

## 2. Naming Conventions
- `UpperCamelCase` for classes, enums, typedefs.
- `lowerCamelCase` for variables, properties, functions.
- `snake_case` for filenames and directory names.

## 3. Widget Architecture
- Keep build methods small and clean.
- Prefer `StatelessWidget` when possible.
- Use `const` constructors for performance.

## 4. State Management (Riverpod)
- Use `Provider` for constants.
- Use `AsyncNotifier` or `Notifier` for mutable state.
- Keep logic in Notifier classes, not UI.

## 5. Async Handling
- Use `await` instead of `.then()` for readability.
- Handle errors using `try-catch` or `AsyncValue.when`.
- Use `Future.wait` for parallel independent requests.