---
description: Concrete steps and commands to initialize a new Flutter project with the correct architecture.
---

# Workflow: Flutter Initialization (`/flutter-init`)

> **⚠️ CRITICAL COUPLING**: This initialization workflow must remain synchronized with architectural mandates in `.agents/rules/flutter-standards.md`.

Follow these concrete steps when the user asks to create a new Flutter application from scratch.

## 1. Execute `flutter create`
Run this exact command in the terminal (replace `app_name` and `com.example` with actual values):

```bash
flutter create --org com.example --platforms android,ios,web app_name
cd app_name
```

## 2. Install Blessed Dependencies
Read `.agents/canons/micro/pubspec.md` for the exact versions, then run:

```bash
flutter pub add flutter_riverpod riverpod_annotation go_router shared_preferences supabase_flutter
flutter pub add dev:build_runner dev:riverpod_generator dev:custom_lint dev:riverpod_lint dev:freezed
flutter pub add freezed_annotation json_annotation
```

## 3. Scaffold Core Directories
Execute this command to create the standard feature-based architecture:

```bash
mkdir -p lib/core/routing lib/core/theme lib/core/constants lib/core/utils
mkdir -p lib/features/auth/data/models lib/features/auth/data/repositories lib/features/auth/presentation/screens lib/features/auth/presentation/providers
```

## 4. Scaffold `main.dart`
Rewrite `lib/main.dart` to include `ProviderScope` and setup routing:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // TODO: Replace with routerProvider when routing is setup
    return MaterialApp(
      title: 'Flutter App',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const Scaffold(body: Center(child: Text('App Initialized'))),
    );
  }
}
```

## 5. Optimize Resource Limits (Hardware Constraints)
> **⚠️ CRITICAL**: Default Gradle settings can consume too much memory and crash laptops with 8GB RAM or less. You MUST apply these fixes immediately after scaffolding.
- **Action**: Edit `android/gradle.properties` (if it exists) and set:
  ```properties
  org.gradle.jvmargs=-Xmx1024m -XX:MaxMetaspaceSize=512m
  ```
- **Rule**: Remind the user to run the app on a **Real Phone** (kills the emulator, saves ~2GB RAM).
- **Rule**: Remind the user to use **VS Code** instead of Android Studio (saves ~1GB RAM).

## 6. Verify Setup
Run `flutter analyze` to ensure there are no initial errors.
Then transition the user to creating their first feature using the recipes in `.agents/canons/global/flutter-feature-recipe.md`.
