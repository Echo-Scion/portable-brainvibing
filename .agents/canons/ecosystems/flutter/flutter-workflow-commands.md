---
description: Flutter CLI commands for project lifecycle (create, build, test, analyze, release). Referenced by universal workflows via delegation.
ecosystem: flutter
---

# Flutter Workflow Commands

> This is the **Flutter-specific** command reference for universal workflows (app-builder, strict-tdd, full-lifecycle).

## Project Initialization
```bash
flutter create --org com.example --platforms android,ios,web app_name
```

## Dependency Installation
```bash
flutter pub add flutter_riverpod riverpod_annotation go_router shared_preferences supabase_flutter
flutter pub add dev:build_runner dev:riverpod_generator dev:custom_lint dev:riverpod_lint dev:freezed
flutter pub add freezed_annotation json_annotation
```

## Testing
```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Run specific test file
flutter test test/features/auth/auth_test.dart
```

## Static Analysis
```bash
flutter analyze
```

## Build & Release
```bash
# Android APK
flutter build apk --release

# Android App Bundle
flutter build appbundle --release

# iOS
flutter build ios --release

# Web
flutter build web --release
```

## Code Generation (Freezed/Riverpod)
```bash
dart run build_runner build --delete-conflicting-outputs
```

## Resource Limits (8GB RAM Laptops)
Edit `android/gradle.properties`:
```properties
org.gradle.jvmargs=-Xmx1024m -XX:MaxMetaspaceSize=512m
```

---
*Flutter Workflow Commands - Ecosystem Canon*
