---
activation: on-demand
description: Architectural canon for local-first, semi-agentic Flutter apps utilizing on-device tool calling, embedded SQLite/Drift, and Bring Your Own Key (BYOK) privacy.
ecosystem: flutter
---

# Local-First Semi-Agentic Architecture (BYOK & On-Device Tool Execution)

This canon defines the architecture for building semi-agentic mobile applications running entirely on-device without remote servers or cloud database bills.

The application acts as a sovereign terminal: the user supplies their own LLM API key (BYOK), and the model's tool calls directly manipulate an embedded local database (SQLite/Drift).

---

## 1. Zero-Cloud Sovereignty Model

```
┌────────────────────────────────────────────────────────────────────────┐
│               LOCAL-FIRST SEMI-AGENTIC CONTROL FLOW                    │
├────────────────────────────────────────────────────────────────────────┤
│ 1. User Intent ────► Prompt Assembler + Tool Declarations              │
│ 2. BYOK Client ────► Direct LLM Provider (OpenAI/Gemini/Ollama)        │
│ 3. Tool Calls  ────► Local Agent Router (JSON Dispatcher)              │
│ 4. Execution   ────► Embedded Database (Drift / SQLite in WAL Mode)    │
│ 5. Reactive UI ────► Drift Stream / Riverpod UI Auto-Rebuild (120Hz)   │
└────────────────────────────────────────────────────────────────────────┘
```

- **Cloud Hosting Costs**: $0.00/month.
- **Privacy Guarantee**: User notes, tasks, and data never leave the local device SQLite file.
- **Offline Integrity**: All read, write, filter, and state transitions execute locally regardless of network availability.

---

## 2. BYOK Key Management (Hardware Keystore)

User API keys MUST be stored exclusively in platform hardware security enclaves using `flutter_secure_storage`:

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class KeyVault {
  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static const _providerKey = 'byok_api_token';

  Future<void> saveKey(String key) async {
    await _storage.write(key: _providerKey, value: key.trim());
  }

  Future<String?> readKey() async {
    return await _storage.read(key: _providerKey);
  }

  Future<void> deleteKey() async {
    await _storage.delete(key: _providerKey);
  }
}
```

---

## 3. Local Tool Declaration & Dispatch Contract

Declare tool schemas to the model using standard JSON Schema definitions. When the model invokes a tool, dispatch it directly against local Drift/SQLite repositories:

```dart
// 1. Tool Declaration
final taskTools = [
  {
    'type': 'function',
    'function': {
      'name': 'addTask',
      'description': 'Creates a new task in the local on-device SQLite database.',
      'parameters': {
        'type': 'object',
        'properties': {
          'title': {'type': 'string', 'description': 'Task title or action item'},
          'priority': {'type': 'string', 'enum': ['low', 'medium', 'high'], 'description': 'Priority level'},
          'dueMinutes': {'type': 'integer', 'description': 'Minutes from now when due, optional'}
        },
        'required': ['title', 'priority'],
      },
    },
  },
  {
    'type': 'function',
    'function': {
      'name': 'rescheduleOverdue',
      'description': 'Reschedules overdue tasks to today or a specified target date.',
      'parameters': {
        'type': 'object',
        'properties': {
          'strategy': {'type': 'string', 'enum': ['eisenhower', 'fifo', 'batch']}
        },
        'required': ['strategy'],
      },
    },
  }
];

// 2. Local Dispatcher
class LocalToolDispatcher {
  final TaskRepository repository;

  LocalToolDispatcher(this.repository);

  Future<Map<String, dynamic>> executeToolCall(String name, Map<String, dynamic> args) async {
    switch (name) {
      case 'addTask':
        final task = await repository.createTask(
          title: args['title'] as String,
          priority: args['priority'] as String,
          dueMinutes: args['dueMinutes'] as int?,
        );
        return {'status': 'success', 'taskId': task.id};

      case 'rescheduleOverdue':
        final count = await repository.rescheduleOverdue(strategy: args['strategy'] as String);
        return {'status': 'success', 'updatedCount': count};

      default:
        return {'status': 'error', 'message': 'Unknown local tool: $name'};
    }
  }
}
```

---

## 4. Transactional Safety & Hallucination Rollbacks

Local backends must wrap AI tool executions inside transactional rollback gates:

```dart
Future<void> executeBatchToolCalls(List<ToolCall> calls) async {
  await database.transaction(() async {
    for (final call in calls) {
      final res = await dispatcher.executeToolCall(call.name, call.arguments);
      if (res['status'] != 'success') {
        throw Exception('Tool execution aborted: ${res['message']}');
      }
    }
  });
}
```

---

## 5. Local Database Invariants (Drift / SQLite)

1. **Write-Ahead Logging (WAL)**: Always enable `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` to ensure UI reads remain non-blocking while background tool executors write to disk.
2. **Reactive Streams**: Presentation widgets must subscribe to Drift query streams (`watch()`) so that when the local agent writes to the database, the UI updates instantly without manual state synchronization.
3. **Local Vector Search**: For semantic task retrieval, utilize `sqlite-vec` or pre-computed embeddings cached in local tables. Avoid external vector databases.
