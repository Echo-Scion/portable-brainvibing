---
activation: glob
description: Comprehensive Flutter architecture, development standards, and styling guidelines.
globs: *.dart
last_updated: 2026-11-01
---

# Flutter Unfair Architecture & Standards (Anti-Split Stack)

> **⚠️ CRITICAL COUPLING**: Any architectural changes here must be reflected in `.agents/canons/ecosystems/flutter/flutter-init.md`.

> [!IMPORTANT]
> **ANTI-SPLIT DOCTRINE MANDATE**: For architectural invariants explaining how and why Flutter supersedes fragmented multi-stack strategies (Tauri, Next.js, React Native), you MUST adhere to [`flutter-anti-split-formula.md`](flutter-anti-split-formula.md).
> For syntax specifics regarding Riverpod, Freezed, GoRouter, and common pitfalls, adhere strictly to `view_file .agents/canons/micro/flutter.md`.

## 1. Core Architectural Superpowers (The 5 Pillars)
1. **GPU Pipeline Ownership (Impeller 120Hz)**: Primary visual models and micro-interactions MUST leverage Flutter Impeller with custom GLSL 460 fragment shaders (`FragmentProgram`) and `CustomPainter`. Isolate continuous rendering loops with `RepaintBoundary` to maintain lockstep 120Hz refresh rates. Follow [`flutter-hardware-shaders.md`](flutter-hardware-shaders.md) and [`liquid-glass-widgets.md`](liquid-glass-widgets.md).
2. **Rust FFI Engine Companion**: Heavy data transformations, token processing, local model inference (`llama.cpp`), and cryptographic/system operations MUST be offloaded to a native Rust companion via `flutter_rust_bridge` or direct `dart:ffi`. Flutter acts strictly as the 120Hz presentation layer; Rust operates as the zero-GC compute engine.
3. **Split-Domain Web Distribution**: For public-facing products requiring search discoverability, decouple marketing from app logic: public SEO landing pages live on static HTML/Astro at `domain.com`; the full reactive workstation runs on Flutter Web (**WasmGC + Skwasm**) at `app.domain.com`.
4. **Local-First Agentic Sovereignty**: Anchor application state in an embedded **Drift** database backed by SQLite in **WAL (Write-Ahead Logging)** mode. Store user LLM credentials in hardware Keystore/Keychain via `flutter_secure_storage`. Execute agentic tool calling locally with zero cloud hosting bills. Follow [`flutter-local-agentic.md`](flutter-local-agentic.md).
5. **AOT Hardening & Anti-Reverse Engineering**: Enforce release binary obfuscation (`--obfuscate --split-debug-info`), TLS certificate pinning, and tamper attestation. Follow [`flutter-app-hardening.md`](flutter-app-hardening.md).

## 2. Modular Structure & Navigation
- **Architecture**: Separate cleanly into Data, Domain, and Presentation layers.
- **Navigation**: Use `go_router`. Define routes centrally. Use `redirect` for authentication guards. Deep linking is mandatory across Mobile, Desktop, and Web.

## 3. Multi-Platform Sovereignty & State Synchronization
- **Single-Engine Parity**: Application logic and UI code must remain 100% unified across Android, iOS, macOS, Windows, Linux, and Web (WasmGC). Never bifurcate core product code across multiple frontend frameworks.
- **Local-First Precedence**: State changes MUST commit to local Drift/SQLite storage first before streaming deltas to remote backends.
- **Multi-Device Realtime Sync**: When multi-device cloud synchronization is required, use **Supabase Realtime Channels** or WebSocket deltas without altering the local reactive Drift stream.
- **Type-Safe Native Bridge**: Use **Pigeon** or `MethodChannel` with structured DTOs for OS-level platform services (sensors, background daemons, overlays).

## 4. Visual State Mapping (The 5-State Rule)
Every UI component MUST account for and implement all states. Do NOT write only the success path.
1. **Loading**
2. **Empty**
3. **Success**
4. **Error**
5. **Shimmer** (while fetching subsequent data)

## 5. Unidirectional Data Flow / UDF (The "One-Way Street")
- **Mandate**: State MUST flow **Model -> UI**. Events flow **UI -> Model**.
- **Riverpod 2.x**: Formalize logic in `AsyncNotifier` or `Notifier`. See Micro-Canon for exact syntax.
- **Reactive Mapping**: Every state change MUST be traceable through a central provider connected to reactive Drift streams or repositories.

## 6. Performance Targets
- **Speed**: Target cold startup times under 1.0 second.
- **FPS**: Maintain 120fps lockstep refresh rate during transitions and canvas animations on supported displays (fallback to 60fps).
- **Zero-Copy Memory**: For heavy data parsing (large JSON payloads, image filters), use Rust FFI memory pointer sharing or `compute()` / `Isolate`.
- **Dynamic Lists**: MANDATORY use of `ListView.builder` for dynamic lists. Never use standard un-indexed `ListView`.

## 7. Platform Daemons, Permission Gates & Asset Standards
- **Permission Onboarding Mandate**: Whenever a UI switch or action controls a native OS capability (`AccessibilityService`, `SYSTEM_ALERT_WINDOW`, `BIND_NOTIFICATION_LISTENER_SERVICE`, `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`), the UI MUST NOT optimistically toggle state. It MUST verify service status via `MethodChannel` first, prompt the user with an educational rationale dialog (`PermissionGateDialog`), and re-check permission on app lifecycle `resumed`.
- **Localization Directory Standard**: Localization files MUST reside in `lib/l10n/app_<locale>.arb` backed by `l10n.yaml` in the project root (`arb-dir: lib/l10n`, `template-arb-file: app_en.arb`), never in arbitrary subdirectories like `lib/core/l10n/`.
- **Real-time App Icon Extraction**: When querying installed packages (`QUERY_ALL_PACKAGES`), the native layer MUST extract `Drawable` icons into compressed PNG byte arrays ($48\times 48\text{dp}$) on a background thread (`Dispatchers.IO`) and pass them to Flutter as `Uint8List` with an in-memory LRU cache to prevent generic placeholder icons.
