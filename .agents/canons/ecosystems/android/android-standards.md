---
activation: glob
description: Core Android architecture, Kotlin conventions, and defensive development standards.
globs: *.kt, *.kts, *.java
last_updated: 2026-10-29
---

# Android Architecture & Core Development Standards

## 1. Clean Architecture & Layering
Android codebases MUST enforce unidirectional separation across three layers:
- **Presentation Layer**: Activities, Fragments, and UI components observe UI state exposed by ViewModels. Presentation logic MUST NOT perform raw database queries or network requests.
- **Domain Layer**: Pure business logic encapsulated in Use Cases / Interactors. Dependencies in this layer MUST be pure Kotlin/Java without Android framework imports.
- **Data Layer**: Repositories, Data Sources (Room, Retrofit/Ktor), and Data Mappers. Repositories expose immutable `Flow` or coroutine-backed results to the domain layer.

## 2. Asynchronous Programming & Concurrency
- **Coroutines & Flow**: All background operations MUST execute on appropriate dispatchers:
  - `Dispatchers.IO`: Disk, database, and network I/O.
  - `Dispatchers.Default`: CPU-intensive computations (JSON parsing, cryptography).
  - `Dispatchers.Main`: UI updates only.
- **Lifecycle Safety**: Flows collected in the UI layer MUST utilize lifecycle-aware collectors (`repeatOnLifecycle(Lifecycle.State.STARTED)` or `collectAsStateWithLifecycle()` in Compose) to prevent background resource leaks.

## 3. State Management & Unidirectional Data Flow (UDF)
- UI state MUST be represented as a single, immutable data class (e.g., `UiState`).
- The ViewModel exposes state via `StateFlow` and handles user intentions via explicit event methods.
- UI components MUST handle all visual states:
  1. **Loading**
  2. **Empty**
  3. **Success**
  4. **Error** (with actionable retry mechanisms)

## 4. Permissions & Hardware Gateways
- Runtime permissions (`POST_NOTIFICATIONS`, `ACCESS_FINE_LOCATION`, etc.) MUST be verified and requested using prior educational rationale dialogs.
- Service status checks MUST be performed every time the app returns to `Lifecycle.State.RESUMED`.
