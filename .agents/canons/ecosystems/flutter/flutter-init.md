---
description: Concrete steps and commands to initialize a new Flutter project under the Anti-Split Stack architecture.
---

# Workflow: Flutter Initialization (`/flutter-init`)

> **⚠️ CRITICAL COUPLING**: This initialization workflow must remain synchronized with architectural mandates in `.agents/canons/ecosystems/flutter/flutter-standards.md` and the 5 pillars in `.agents/canons/ecosystems/flutter/flutter-anti-split-formula.md`.

Follow these concrete steps when the user asks to create a new Flutter application from scratch.

## 1. Execute `flutter create`
Run this exact command in the terminal (replace `app_name` and `com.example` with actual values):

```bash
flutter create --org com.example --platforms android,ios,macos,windows,linux,web app_name
cd app_name
```

## 2. Install Blessed Dependencies (Anti-Split Stack)
Read `.agents/canons/micro/pubspec.md` for the exact versions, then run:

```bash
# State, Routing & UI
flutter pub add flutter_riverpod riverpod_annotation go_router shared_preferences
flutter pub add cached_network_image flutter_svg google_fonts lucide_icons_flutter

# Local-First Sovereignty & Hardware Keystore (Pillar 4)
flutter pub add drift drift_flutter sqlite3_flutter_libs flutter_secure_storage

# Dev Code Generators & Analyzers
flutter pub add dev:build_runner dev:riverpod_generator dev:custom_lint dev:riverpod_lint dev:freezed
flutter pub add dev:drift_dev dev:json_serializable freezed_annotation json_annotation
```

*(Optional: If high-throughput token crunching, local AI inference, or systems compute is required, install `flutter_rust_bridge` per Pillar 2).*

## 3. Scaffold Core Directories (Including Shaders & Native Compute)
Execute this command to create the standard feature-based architecture and hardware assets:

```bash
# Core Architecture & Database
mkdir -p lib/core/database lib/core/routing lib/core/theme lib/core/constants lib/core/utils
mkdir -p lib/features/auth/data/models lib/features/auth/data/repositories lib/features/auth/presentation/screens lib/features/auth/presentation/providers

# Hardware Shaders & Systems Bridges (Pillars 1 & 2)
mkdir -p shaders native
```

## 4. Declare Shaders in `pubspec.yaml`
Add the hardware shader declaration under the `flutter:` block in `pubspec.yaml`:

```yaml
flutter:
  uses-material-design: true
  shaders:
    - shaders/liquid_glass.frag
```

*(Create a placeholder shader file at `shaders/liquid_glass.frag` following `.agents/canons/ecosystems/flutter/flutter-hardware-shaders.md`).*

## 5. Scaffold `main.dart`
Rewrite `lib/main.dart` to include `ProviderScope`, Drift database initialization, and theme configuration:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      title: 'Unfair Flutter App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6366F1),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const Scaffold(
        body: Center(
          child: Text(
            'Unfair Flutter Initialized',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          ),
        ),
      ),
    );
  }
}
```

## 6. Web Distribution Strategy (Pillar 3: Split-Domain)
- **Production Web Workstation**: Compile web builds targeting WebAssembly Garbage Collection (WasmGC) and Skwasm for maximum 120Hz canvas parity:
  ```bash
  flutter build web --wasm --release
  ```
- **SEO Separation**: Remind the user that public SEO marketing pages live on `domain.com` (static Astro/Next.js/HTML), while the Flutter WasmGC app lives on `app.domain.com`.

## 7. Optimize Resource Limits (Hardware Constraints)
> **⚠️ CRITICAL**: Default Gradle settings can consume too much memory and crash laptops with 8GB RAM or less. You MUST apply these fixes immediately after scaffolding.
- **Action**: Edit `android/gradle.properties` (if it exists) and set:
  ```properties
  org.gradle.jvmargs=-Xmx1024m -XX:MaxMetaspaceSize=512m
  ```
- **Rule**: Remind the user to run the app on a **Real Phone** (kills the emulator, saves ~2GB RAM).
- **Rule**: Remind the user to use **VS Code** instead of Android Studio (saves ~1GB RAM).

## 8. Verify Setup
Run `flutter analyze` to ensure there are no initial errors.
Then transition the user to creating their first feature using the recipes in `.agents/canons/ecosystems/flutter/flutter-feature-recipe.md`.
