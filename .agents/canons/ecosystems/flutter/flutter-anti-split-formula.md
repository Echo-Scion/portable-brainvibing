---
activation: on-demand
description: Master architectural formula for Unfair Flutter (Anti-Split Stack) - Impeller 120Hz GPU shaders, Rust FFI compute bridge, split-domain WasmGC web, local-first Drift/SQLite WAL sovereignty, and AOT hardening.
ecosystem: flutter
---

# The Anti-Split Stack Formula: Unfair Flutter Architecture

This master canon defines the **Unfair Flutter** doctrine. It supersedes conventional "pure Flutter" CRUD development and directly eliminates the need to fragment an engineering team into a split stack (e.g., Next.js for Web + Tauri for Desktop + React Native for Mobile).

---

## 1. The Architectural Divergence

When Flutter is treated as a generic cross-platform CRUD framework with simple Material/Cupertino widgets and cloud API calls, it inherits engine bundle overhead while failing to beat specialized tools on their home turf.

The **Anti-Split Stack Formula** converts Flutter's characteristics into defensible moats:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE ARCHITECTURAL DIVERGENCE                         │
├────────────────────────────────────────────────────────────────────────┤
│ PURE FLUTTER (Conventional CRUD)                                       │
│ • Generic UI widgets (Material/Cupertino clones)                       │
│ • Dart-only compute (slow JSON/tokenization, FFI underutilized)        │
│ • Cloud-dependent backend (Supabase/Firebase CRUD bills)               │
│ • Fights DOM on SEO turf (loses to Next.js)                            │
│ ➔ RESULT: Pays all engine bundle taxes with zero unique advantage.     │
├────────────────────────────────────────────────────────────────────────┤
│ UNFAIR FLUTTER (The Anti-Split Formula)                                │
│ • Impeller GPU Shaders & 120Hz tactile physics (DOM/Tauri cannot match)│
│ • Rust FFI Engine Bridge (Pillar 2 compute, memory safety, zero-copy)  │
│ • Local-First Agentic Sovereignty (Drift/SQLite WAL + BYOK tool loop)  │
│ • Split-Domain Web (Static Astro SEO landing + Flutter WasmGC app)     │
│ • AOT Binary Hardening (compiler obfuscation, tamper resistance)       │
│ ➔ RESULT: Single unified codebase outperforming fragmented stacks.     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The 5 Pillars of Unfair Flutter

### Pillar 1: GPU Pipeline Ownership (Impeller & GLSL Shaders)
- **Direct Rasterization**: Flutter does not wrap host OS views or DOM elements. Through the **Impeller** engine (Metal on iOS/macOS, Vulkan on Android), Flutter directly controls pixel rasterization.
- **GLSL 460 Fragment Programs**: Write custom fragment shaders (`shaders/*.frag`) compiled into SPIR-V. Compute procedural liquid glass, chromatic aberration, and refraction with sub-millisecond draw calls.
- **120Hz Tactile Physics**: Decouple interactive animation curves from host OS constraints. Use `CustomPainter` wrapped in `RepaintBoundary` to maintain lockstep 120Hz refresh rates without frame drops.
- **Reference**: Follow [`flutter-hardware-shaders.md`](flutter-hardware-shaders.md) and [`liquid-glass-widgets.md`](liquid-glass-widgets.md).

### Pillar 2: Rust FFI Engine Companion (Native Systems Compute)
- **Zero-Copy Memory**: Dart's dynamic typing and garbage collector can become bottlenecks for heavy token processing, local LLM orchestration (`llama.cpp`), high-throughput cryptographic operations, and binary deserialization.
- **Pillar 2 Mesh Integration**: Pair Flutter with a Rust native companion using `flutter_rust_bridge` or direct `dart:ffi`.
  - Dart handles the **120Hz GPU Presentation Layer**.
  - Rust handles the **zero-GC systems compute engine**, background thread pools, and streaming memory buffers.
- **No IPC Serialization Overhead**: Unlike WebViews or Electron, which serialize data over JSON IPC pipes, Dart FFI passes raw memory pointers directly to compiled Rust binaries with zero copy.

### Pillar 3: Split-Domain Web Distribution (Solving the SEO Vector)
- **The Core Flaw of Pure Flutter Web**: Forcing Flutter Web to act as an SEO-driven marketing blog causes high bounce rates due to Wasm/CanvasKit bundle download times and lack of indexable DOM text.
- **The Split-Domain Architecture**:
  1. `domain.com` (Public Acquisition): Zero-bundle static HTML or lightweight SSR (`Astro`, `Next.js`, or raw HTML) optimized strictly for search crawlers, OpenGraph previews, and sub-100ms first contentful paint (FCP).
  2. `app.domain.com` (Sovereign Workstation): The unified Flutter Web application compiled with **WasmGC + Skwasm** (`flutter build web --wasm`). Users experience the identical 120Hz workstation interface in the browser with 100% shared code from mobile and desktop.

### Pillar 4: Local-First Agentic Sovereignty (Zero-Cloud BYOK Model)
- **Embedded Database**: Use **Drift** backed by SQLite in **WAL (Write-Ahead Logging)** mode. Reactive UI streams auto-rebuild on database mutations with zero network latency.
- **BYOK (Bring Your Own Key)**: The user provides their own LLM API credentials (stored in hardware-backed `flutter_secure_storage`).
- **Autonomous Tool Calling**: Structured tool calls from on-device or remote LLMs execute directly against local SQLite tables.
- **Cost & Privacy Guarantee**: $0.00/month cloud hosting bills. User data never leaves the local device storage.
- **Reference**: Follow [`flutter-local-agentic.md`](flutter-local-agentic.md).

### Pillar 5: AOT Binary Hardening & Anti-Reverse Engineering
- **Tamper Resistance**: Web JavaScript bundles and React Native Hermes bytecode are trivial to decompile, beautify, and clone via AI prompts.
- **AOT Machine Snapshots**: Flutter compiles directly to architecture-specific native machine instructions (`arm64`, `x86_64`) using a proprietary Dart heap layout.
- **Hardening Standards**:
  - Enforce release build obfuscation: `flutter build <target> --obfuscate --split-debug-info=symbols/`.
  - Enforce TLS certificate pinning with Dart `SecurityContext`.
  - Enforce device integrity checks (Play Integrity API / App Attest).
- **Reference**: Follow [`flutter-app-hardening.md`](flutter-app-hardening.md).

---

## 3. Architectural Comparison: Unfair Flutter vs. The Split Stack

| Capability Vector | Unfair Flutter (Single Codebase) | Fragmented Alternative (Split Stack) | Why Unfair Flutter Wins |
| :--- | :--- | :--- | :--- |
| **Tactile Visual Taste** | Impeller GLSL shaders + custom 120Hz canvas rendering. | DOM CSS / WebView filters (laggy, limited by CSS specs). | Pixel-level GPU ownership; unique taste moat impossible to clone via web wrappers. |
| **Compute & AI Throughput** | Direct Dart FFI pointer sharing to Rust (`llama.cpp`, tokenizers). | JSON IPC over Electron/Tauri bridge or pure JS in Web. | True zero-copy memory transfer; native machine speed with zero GC pauses. |
| **Web Presence & SEO** | Split-domain: Astro landing on root + WasmGC app on subdomain. | Next.js full-stack app. | 100% SEO score on public landing; identical interactive workstation on app. |
| **Development Velocity** | 1 unified codebase, 1 Drift database schema, 1 state model. | 3 codebases (Next.js, Tauri, React Native/Kotlin), 3 state paradigms. | Eliminates cross-team drift, contract desynchronization, and triple maintenance. |
| **IP Protection** | Stripped Dart AOT snapshot binary. | Plaintext / minified JavaScript bundles. | High reverse-engineering friction against automated LLM clones. |

---

## 4. Operational Invariant

When designing, scaffolding, or auditing any Flutter feature within `.agents`:
1. **Never default to basic CRUD**: Reject building generic Material cards when tactile canvas physics or custom shaders are warranted.
2. **Never split the application engine**: Never propose migrating desktop or mobile features to a secondary web framework unless strictly building a public SEO marketing landing page.
3. **Always anchor in Local-First Sovereignty**: The core app must operate flawlessly offline against local Drift/SQLite before layer-2 cloud sync (e.g., Supabase Realtime Channels) is introduced.
