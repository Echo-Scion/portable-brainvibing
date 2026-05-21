# Micro-Canon: Flutter `pubspec.yaml` Blessed Versions

When initializing a project or adding dependencies, use these exact versions to avoid dependency hell and breaking changes.
These have been tested and verified to work together seamlessly.

## Core State Management & Routing
```yaml
dependencies:
  flutter_riverpod: ^2.6.1
  riverpod_annotation: ^2.3.5
  go_router: ^14.6.2
  freezed_annotation: ^2.4.4
  json_annotation: ^4.9.0

dev_dependencies:
  build_runner: ^2.4.13
  riverpod_generator: ^2.4.3
  riverpod_lint: ^2.3.13
  custom_lint: ^0.7.0
  freezed: ^2.5.7
  json_serializable: ^8.1.0
```

## Backend & Networking
```yaml
dependencies:
  supabase_flutter: ^2.6.0
  http: ^1.2.2
  shared_preferences: ^2.3.3
  flutter_secure_storage: ^9.2.2
```

## UI & Styling
```yaml
dependencies:
  cached_network_image: ^3.4.1
  flutter_svg: ^2.0.17
  google_fonts: ^6.2.1
  lucide_icons_flutter: ^1.0.0+1
```

> **IMPORTANT**: Never use `^` for major version bumps (e.g., `^3.0.0` if `^2.6.1` is listed). Stick to the established major versions to prevent architecture breakage.
