# Micro-Canon: Flutter `pubspec.yaml` Dependency Policy

When initializing a project or adding dependencies, **DO NOT rely on hardcoded legacy versions**. Frameworks evolve rapidly.

## Policy Rules
1. **Always use the latest stable versions** of core libraries.
2. During initialization, you may use `any` as a temporary placeholder and run `flutter pub get` or `flutter pub outdated` to resolve the latest versions.
3. Once versions are resolved, lock them in `pubspec.yaml` using the `^` syntax (e.g., `^3.1.0`) to allow minor security patches but prevent breaking major updates.

## Core Blessed Dependencies
- **State & Routing**: `flutter_riverpod`, `riverpod_annotation`, `go_router`, `freezed_annotation`, `json_annotation`
- **Dev Tools**: `build_runner`, `riverpod_generator`, `custom_lint`, `freezed`, `json_serializable`
- **Backend & Networking**: `supabase_flutter`, `http`, `shared_preferences`, `flutter_secure_storage`
- **UI & Styling**: `cached_network_image`, `flutter_svg`, `google_fonts`, `lucide_icons_flutter`

> **IMPORTANT**: Never hardcode versions from an agent memory prompt, as they will decay over time. Always resolve against the live environment.
