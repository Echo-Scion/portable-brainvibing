# ARCHITECTURE: Scionlog & Orion Foundation

> **Master Technical Atlas (Pillar: 03_Tech)**
> Details System Architecture, Data Pipelines, Database Schemas, and Security Guardrails.

---

## 1. High-Level System Architecture

The ecosystem operates as a bi-cameral architecture: a **Cognitive Brain Layer (Orion)** paired with an **Algorithmic Execution Muscle (Scionlog)**.

```mermaid
graph TD
    User[Developer / Operator] --> IDE[Antigravity / Gemini IDE]
    IDE --> PreWake[Hook: pre-agent-wake.py]
    PreWake --> WorkingBuffer[.orion/working/context.json]
    
    subgraph Cognitive Layer (Orion)
        OrionCLI[scripts/orion.py] --> OrionBrain[commands/brain.py]
        OrionBrain --> OrionDB[(.orion/orion.db - FTS5 + Triplet Graph)]
        OrionBrain --> MatrixRules[.orion/matrix/ - Compiled JSON Rules]
        OrionBrain --> LocalOllama[Dual-Stack Local LLM - Qwen2.5-Coder]
    end
    
    subgraph Execution Muscle (Scionlog)
        Scanner[src/engine/pipeline.py] --> CCXT[CCXT / Binance API]
        Scanner --> Indicators[src/indicators/indicators.py]
        Indicators --> RiskEngine[src/engine/risk.py]
        RiskEngine --> TradeDB[(scionlog.sqlite - WAL Mode)]
        TradeDB --> Telemetry[src/core/notifications.py -> Telegram]
        TradeDB --> Lessons[src/engine/lessons.py -> hyperopt.py]
    end
    
    Lessons -. Darwinian Feedback .-> OrionBrain
```

---

## 2. Core System Components

### A. The Cognitive Brain (`.agents/` & `.orion/`)
- **Master Router**: `GEMINI.md` routes intent JIT to specialized personas and canon recipes.
- **Unified Engine**: `scripts/orion.py` exposes 20+ commands with auto-retry resilience and dual-stack IPv4/IPv6 Ollama network fallback.
- **GraphRAG Store**: `.orion/orion.db` stores semantic entities, relational edges, and page hashes using SQLite FTS5.
- **Rule Matrices**: `.agents/scripts/commands/compile_rules.py` flattens markdown rules into dense JSON matrices in `.orion/matrix/` for low-token matching.

### B. The Execution Muscle (`scionlog/`)
- **Data Ingestion**: Multi-timeframe OHLCV fetching via CCXT with exponential backoff.
- **Signal Pipeline**: 12-point sniper checklist combining Trend, Volume, Microstructure, and Volatility.
- **Risk Gate**: Dynamic ATR position sizing, max leverage constraints, and capital preservation circuit breakers.
- **Persistence**: SQLite in WAL mode (`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;`) preventing database lock contention.

---

## 3. Database Schemas

### Scionlog Operational Database (`scionlog.sqlite`)
```sql
CREATE TABLE IF NOT EXISTS positions (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_price REAL NOT NULL,
    size REAL NOT NULL,
    stop_loss REAL NOT NULL,
    take_profit REAL NOT NULL,
    status TEXT NOT NULL,
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_price REAL NOT NULL,
    exit_price REAL NOT NULL,
    pnl REAL NOT NULL,
    roi REAL NOT NULL,
    duration_seconds INTEGER,
    exit_reason TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS darwinian_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    mistake_type TEXT NOT NULL,
    parameter_adjusted TEXT NOT NULL,
    old_value REAL NOT NULL,
    new_value REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Orion Knowledge Graph (`.orion/orion.db`)
```sql
CREATE TABLE IF NOT EXISTS pages (
    path TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL,
    title TEXT,
    mtime REAL,
    access_count INTEGER DEFAULT 0,
    last_accessed TEXT
);

CREATE TABLE IF NOT EXISTS edges (
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    PRIMARY KEY (source_id, target_id, relation)
);

CREATE TABLE IF NOT EXISTS contradictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_a_source TEXT, edge_a_target TEXT, edge_a_relation TEXT,
    edge_b_source TEXT, edge_b_target TEXT, edge_b_relation TEXT,
    resolution TEXT DEFAULT 'unresolved',
    evidence TEXT,
    detected_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT
);
```

---

## 4. Security & Circuit Breakers

1. **Local Secrets Vault**: All API keys, tokens, and endpoints reside strictly in `.env` (enforced by `.gitignore` and `secrets_scan_verifier.py`).
2. **Paper Trading Firewall**: `PAPER_TRADING=True` is hardcoded as default in runtime configuration.
3. **Network Resiliency**: Dual-stack IP resolution in `resolve_ollama_base_url()` tries `127.0.0.1` -> `::1` -> `localhost` with 1-second connect timeouts.
4. **Subprocess Isolation**: Background sub-processes enforce `check=True` in try-except blocks, logging failures to `sys.stderr` to eliminate silent dropouts.

---

## 5. Granular Detail References (JIT Child Mapping)
When deep technical implementation is needed, generate detail files using these official prefixes:
- `Dev_` — Component implementations and schemas (e.g., `Dev_Database.md`, `Dev_Pipeline.md`).
- `Infra_` — Process supervision and deployment scripts (e.g., `Infra_CI_CD.md`, `Infra_PM2.md`).
- `Test_` — Integration test harnesses and backtesting suites (e.g., `Test_Backtest_Harness.md`).
