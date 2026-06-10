---
activation: glob
description: Comprehensive Flutter architecture, development standards, and styling guidelines.
globs: *.dart

version: 0.0.1
last_updated: 2026-05-20
---

# Flutter Hybrid Architecture & Standards

> **⚠️ CRITICAL COUPLING**: Any architectural changes here must be reflected in `.agents/canons/ecosystems/flutter/flutter-init.md`.

> [!IMPORTANT]
> **MICRO-CANON MANDATE**: For syntax specifics regarding Riverpod, Freezed, GoRouter, and common pitfalls, you MUST adhere strictly to the cheat sheet at `view_file .agents/canons/micro/flutter.md`. Do not hallucinate syntax.

## 1. Modular Structure & Navigation
- **Architecture**: Separate into Data, Domain, and Presentation layers.
- **Navigation**: Use `go_router`. Define routes centrally. Use `redirect` for auth guards. Deep linking is mandatory.

## 2. Hybrid Patterns (Multi-Platform)
- **Realtime Sync**: MANDATORY use of **Supabase Realtime Channels** to sync state instantly between Web (Next.js) and Mobile (Flutter) without polling.
- **Thread Isolation (60FPS Rule)**: For heavy data transformations (JSON parsing/Image processing), ALWAYS use `compute()` or `Isolate` on Mobile.
- **Type-Safe Native Bridge**: Use **Pigeon** for native mobile APIs to prevent runtime type errors.

## 3. Visual State Mapping (The 5-State Rule)
Every UI component MUST account for and implement all states. Do NOT write only the success path.
1. **Loading**
2. **Empty**
3. **Success**
4. **Error**
5. **Shimmer** (while fetching subsequent data)

## 4. Unidirectional Data Flow / UDF (The "One-Way Street")
- **Mandate**: State MUST flow **Model -> UI**. Events flow **UI -> Model**.
- **Riverpod 2.x**: Formalize logic in `AsyncNotifier` or `Notifier`. See Micro-Canon for exact syntax.
- **Reactive Mapping**: Every state change MUST be traceable through a central provider.

## 5. Performance Targets
- **Speed**: Target load times under 1.5 seconds.
- **FPS**: Maintain 60fps during transitions.
- **Lists**: MANDATORY use of `ListView.builder` for dynamic lists. Never use standard `ListView`.
