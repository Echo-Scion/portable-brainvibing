---
description: Flutter data modeling patterns using Freezed and Riverpod. Referenced by universal data-logic skill via delegation.
ecosystem: flutter
---

# Flutter Data & Logic Patterns (Riverpod + Freezed)

> This is the **Flutter-specific** implementation of the universal data-logic skill (immutability, DTOs, reactive state).

## JIT Tool Directives
1. Load `flutter-logic-patterns.md` for Freezed model templates and Riverpod Notifier snippets.
2. Use an available file-search tool with pattern `*.dart` to locate `domain/` and `presentation/` directories.
3. Check `pubspec.yaml` for codegen dependencies.

## Critical Validations
- **Immutability**: ALWAYS use `@freezed` for data models.
- **Optimization**: ALWAYS follow the `.select()` Rule when watching complex states.
- **Isolation**: NEVER put business logic in Widgets. Logic lives in Notifiers.
- **Safety**: NEVER use `dynamic` in models. ALWAYS call `state =` with `copyWith`.

## Workflow Patterns
1. **The .select() Rule**: Watch specific fields to prevent unnecessary rebuilds.
2. **Provider Choice**: Use `AsyncNotifier` for async state mutations and `FutureProvider` for one-off fetches.
3. **Loop Prevention**: Handle futures/streams with `.when` or `AsyncValue`.

## 🌐 Cross-Boundary Hybrid Persistence Contracts (Flutter <-> Native Daemons)
When synchronizing preferences and state between Flutter and native Android/iOS daemons (`AccessibilityService`, `BroadcastReceiver`, `WindowManager` overlays):

1. **Cold-Start Listener Binding Invariant**:
   - Native daemons MUST register `OnSharedPreferenceChangeListener` directly and unconditionally against `"FlutterSharedPreferences"` (`Context.MODE_PRIVATE`).
   - FORBIDDEN: Conditional listener traps such as `if (flutterPrefs.all.isNotEmpty()) flutterPrefs else defaultPrefs`. On fresh installs before Flutter writes, `all.isEmpty()` evaluates to true, binding the listener permanently to the wrong file.

2. **Collection Serialization Invariant (`setStringList` vs JSON)**:
   - When storing lists or sets destined for native daemons, Flutter code MUST serialize via `_prefs.setString(key, jsonEncode(list))` instead of `setStringList`.
   - **Rationale**: Modern `shared_preferences_android` prepends an internal Base64 identifier prefix (`VGhpcyBpcyB0aGUgcHJlZml4...`) to strings saved via `setStringList`, causing native `JSONArray` and `getStringSet` to fail with `JSONException` or `ClassCastException` and silently return empty sets.
   - Native Kotlin reader pattern:
     ```kotlin
     fun getSharedList(context: Context, key: String): List<String> {
         val prefs = context.getSharedPreferences("FlutterSharedPreferences", Context.MODE_PRIVATE)
         val raw = prefs.getString("flutter.$key", null) ?: return emptyList()
         return try {
             val json = org.json.JSONArray(raw)
             List(json.length()) { json.getString(it) }
         } catch (e: Exception) {
             emptyList()
         }
     }
     ```

## Troubleshooting
- **copyWith not found**: Missing `part` directive.
- **UI not rebuilding**: Using `ref.read` instead of `ref.watch`.
- **Duplicate Provider**: Multiple `@riverpod` with same name.
- **Native Daemon Missing Pref Updates**: Listener registered to wrong preferences file on cold start or collection format mismatch.

---
*Flutter Logic Patterns - Ecosystem Canon*
