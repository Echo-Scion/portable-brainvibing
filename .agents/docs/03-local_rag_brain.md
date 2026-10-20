# VOLUME III: LOCAL RAG BRAIN — Architecture of `.orion/`

---

## Chapter 5: Directory Structure & SQLite Schema

The local cognitive subsystem resides in `.orion/`. It operates locally without third-party cloud vector dependencies:

```
.orion/
├── _manifest.json        # Asset hashes and indexing timestamps
├── index.md              # Human-readable index of all ecosystem assets
├── log.md                # Episodic cross-session journal
├── orion.db              # Primary SQLite3 database (WAL mode, busy_timeout=5000ms)
├── episodic/             # Compressed historical session summaries
├── matrix/               # Machine-readable compiled JSON rule matrices
├── sources/              # Processed markdown and YAML source mirrors
└── working/
    ├── context.json      # Omni-Buffer real-time IDE state
    ├── execution_state.json # Crash-proof FSM transaction tracker
    └── handoff.md        # Session handoff notes
```

---

### 5.1. SQLite Database Architecture (`orion.db`)

All connections enforce SQLite WAL mode (`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;`) via `core/db.py`. The database manages 18 relational and virtual FTS5 tables across core modules, plus 2 backward-compatible SQL views (`nodes` and `edges`), with all 18 active tables verified by schema cohesion:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        orion.db SQLite Schema                          │
├────────────────────────────┬───────────────────────────────────────────┤
│ Table                      │ Purpose                                   │
├────────────────────────────┼───────────────────────────────────────────┤
│ `pages`                    │ SHA-256 hashed markdown document assets   │
│ `pages_fts`                │ FTS5 virtual table for Porter BM25 search │
│ `entities`                 │ Canonical entities with types & desc      │
│ `relations`                │ Triplets with FTS5 BM25 search            │
│ `entities_fts`             │ FTS5 canonical entity index               │
│ `relations_fts`            │ FTS5 canonical relation index             │
│ `communities`              │ Louvain modularity hierarchical clusters  │
│ `community_members`        │ Entity membership mappings for clusters   │
│ `communities_fts`          │ FTS5 community index                      │
│ `contradictions`           │ Colliding predicates flagged for review   │
│ `multi_layer_memory`       │ Virtual memory hierarchy                  │
│ `memory_mutation_history`  │ Memory mutation audit trail               │
│ `archival_vectors`         │ Archived vector records (Float32 BLOB)    │
│ `recall_turns`             │ Recall/session interaction turns          │
│ `fsm_checkpoints`          │ Transactional FSM recovery checkpoints    │
│ `spans`                    │ Trace/span telemetry                      │
│ `rag_evaluations`          │ Retrieval relevance diagnostics           │
│ `telemetry`                │ Execution event telemetry log             │
│ `nodes` (VIEW)             │ Backward compatibility graph entity view  │
│ `edges` (VIEW)             │ Backward compatibility graph relation view│
└────────────────────────────┴───────────────────────────────────────────┘
```

#### FTS5 Porter Lexical Indexing
```sql
CREATE VIRTUAL TABLE pages_fts USING fts5(
    path,
    content,
    tokenize='porter'
);
```

Lexical queries execute in sub-millisecond timeframes:
```sql
SELECT path, bm25(pages_fts) AS rank 
FROM pages_fts 
WHERE pages_fts MATCH 'auth OR jwt OR token' 
ORDER BY rank LIMIT 10;
```

---

## Chapter 6: Relational Triplet Graph (Code Dependency Safety)

Source files express structural dependencies. During ingestion, the engine extracts semantic triplets `(Subject, Predicate, Object)`:

```json
{
  "subject": "UserController",
  "predicate": "depends_on",
  "object": "AuthService",
  "context": "UserController validates JWT claims using AuthService instance."
}
```

### Table Definitions:
```sql
-- Canonical GraphRAG Tables
CREATE TABLE entities (
    name TEXT PRIMARY KEY,
    type TEXT,
    description TEXT,
    source_path TEXT
);

CREATE TABLE relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_id TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    provenance TEXT DEFAULT 'EXTRACTED',
    source_path TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(subject_id, predicate, object_id)
);

CREATE TABLE archival_vectors (
    id TEXT PRIMARY KEY,
    content TEXT,
    embedding BLOB,
    created_at REAL
);

-- Backward-Compatible Views (Zero-Duplication over entities & relations)
CREATE VIEW IF NOT EXISTS nodes AS
SELECT name AS id, type, name, source_path FROM entities;

CREATE VIEW IF NOT EXISTS edges AS
SELECT subject_id AS source_id, object_id AS target_id, predicate AS relation, weight AS confidence, source_path FROM relations;

-- Triggers for transparent backward compatibility on views
CREATE TRIGGER IF NOT EXISTS edges_view_insert INSTEAD OF INSERT ON edges BEGIN
    INSERT OR IGNORE INTO entities (name, type, description, source_path) VALUES (NEW.source_id, 'Entity', NEW.source_id, NEW.source_path);
    INSERT OR IGNORE INTO entities (name, type, description, source_path) VALUES (NEW.target_id, 'Entity', NEW.target_id, NEW.source_path);
    INSERT INTO relations (subject_id, predicate, object_id, weight, source_path)
    VALUES (NEW.source_id, NEW.relation, NEW.target_id, NEW.confidence, NEW.source_path)
    ON CONFLICT(subject_id, predicate, object_id) DO UPDATE SET
        weight = excluded.weight,
        source_path = excluded.source_path;
END;
```

During architectural refactoring, 1-hop graph neighbor traversal inspects incoming and outgoing edges (`relations` and `edges`) to notify agents of connected callers, eliminating broken dependencies before code modification. Vector embeddings are stored as packed binary float32 blobs in `archival_vectors`, eliminating JSON serialization overhead.

---

## Chapter 7: Universal AST Parser (`scripts/core/scanner.py`)

Feeding 2,000-line source files into an LLM context wastes tokens on method bodies and implementation details. `scanner.py` implements a structural parser:

```
┌────────────────────────────────────────────────────────┐
│              Input Source Code (2,000 LOC)             │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 1. Native Python `ast` Standard Library                │
│    Inspects classes, function signatures, docstrings   │
│    Emits exact [Lstart-Lend] line spans for Python     │
└───────────────────────────┬────────────────────────────┘
                            │ (fallback for JS/TS/Dart/polyglot)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 2. Deterministic Polyglot Regex Heuristics             │
│    Extracts class, struct, interface, and functions    │
│    Emits estimated [Lstart-Lend] spans across languages│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│       Output Structural Skeleton (~200 LOC, -90%)      │
└────────────────────────────────────────────────────────┘
```

The resulting skeleton preserves class signatures, parameters, return types, and docstrings, allowing the agent to grasp architectural relationships at 10% of the token cost.

---

## Chapter 8: Dual-Level GraphRAG & Pure-Python Louvain Modularity

### 8.1. The Dual-Level Query Mechanism
Standard vector search fails on broad architectural questions (*"How does authentication and state management interact?"*), while standard keyword search misses semantic synonyms. `.agents` implements a **Dual-Level GraphRAG** architecture:

```
                               ┌──────────────────────┐
                               │  User Query String   │
                               └──────────┬───────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
        ┌─────────────────────┐                       ┌─────────────────────┐
        │   Global (Macro)    │                       │    Local (Micro)    │
        │ Louvain Community   │                       │ 1-Hop Graph + Vector│
        │     Summaries       │                       │   + FTS5 BM25 Match │
        └──────────┬──────────┘                       └──────────┬──────────┘
                   │                                             │
                   └──────────────────────┬──────────────────────┘
                                          ▼
                               ┌──────────────────────┐
                               │ Combined Context Box │
                               │ Synthesized for LLM  │
                               └──────────────────────┘
```

1. **Global / Macro Retrieval**: `core/orion_graph.py` computes Louvain community clusters purely using Python stdlib (`math`, `random`, `collections`). Nodes are grouped into dense semantic communities, and community summary centroids answer macro-architectural inquiries.
2. **Local / Micro Retrieval**: Matches exact keywords via FTS5 BM25, computes cosine similarity against local `nomic-embed-text` embeddings, and traverses 1-hop graph edges.

### 8.2. Pure-Python Louvain Modularity Algorithm
`core/orion_graph.py` calculates modularity gain $\Delta Q$ without requiring compiled C extensions like `networkx` or `scipy`:

$$\Delta Q = \frac{k_{i,\text{in}}}{m} - \frac{\Sigma_{\text{tot}} k_i}{2m^2}$$

Communities optimize partitioning dynamically, storing community assignments directly in the `communities` and `community_members` tables.

### 8.3. Granular NanoBrain States
`python .agents/scripts/orion.py brain nanobrain <mode>`:
- `on`: Full local neural execution (Ollama generative model + embedding vector search).
- `embed_only` *(Default)*: Local vector generation (`nomic-embed-text`) via Ollama with zero generative VRAM load. Fast semantic search with minimal RAM.
- `llm_only`: Generative summarization active, vector logic disabled.
- `off`: Pure SQLite3 FTS5 Porter BM25 lexical search. Fully functional without Ollama running.

---

## Chapter 9: Memory Hygiene, Contradiction Engine & Temporal Pulse

### 9.1. Smart Memory Hygiene
Context compaction uses mechanical eligibility criteria:
- Every page in `orion.db` records access frequency in `pages.access_count`.
- Frequently recalled nodes have their access count incremented.
- Compaction scripts (`commands/compact.py` via `commands/brain.py: compact & compress`) drive multi-tier context shrinking across 5 levels (`lite`, `stream`, `full`, `aggressive`, `ultra`, `pipeline`), utilizing `SyntaxAnchorGuard`, `PayloadStreamShaper` (AST/JSON/Trace shaping), and `ChronologicalSectionDecay`, while pruning only low-access nodes older than 14 days and protecting critical architectural decisions from eviction.

### 9.2. Contradiction Engine (`commands/brain.py contradict`)
Conflicting directives across absorbed files (e.g., File A recommends Riverpod, File B recommends Provider) are identified by predicate collisions:
- Detected collisions write to the `contradictions` SQL table.
- Agents resolve conflicts algorithmically by adjusting edge confidence weights (0.0 to 1.0) rather than deleting historical notes.

### 9.3. Activity-Based Temporal Pulse (`commands/reflexion.py`)
Rather than relying on calendar cron jobs, the ecosystem advances memory across activity-based intervals:
1. **Session Pulse**: Triggered on `/session-offload`. Summarizes the immediate working turn.
2. **Milestone Synthesis**: Evaluated every 5 completed sessions, distilling micro-steps into milestone records.
3. **Epoch Consolidation**: Evaluated every 4 milestones, archiving deep history into permanent repository logs.
