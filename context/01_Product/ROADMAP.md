# ROADMAP: Scionlog & Orion Foundation

> **Master Product Atlas (Pillar: 01_Product)**
> Integrates Roadmap Milestones, Viability Scorecard, Anti-Goals, and Feature Metrics.

---

## 1. Product Milestones

### Phase 1: Foundation Hardening & Mechanical Synapses (COMPLETED)
- [x] Dual-stack network resolver (`resolve_ollama_base_url`) preventing Windows IPv6 SYN timeout.
- [x] Cross-platform hardware sensing for macOS Apple Silicon unified memory.
- [x] SQLite WAL database concurrency and defensive schema initialization.
- [x] Recursive matrix compilation for standards (`standards__fsm-protocol.json`).
- [x] Platform-agnostic hook execution via `--hook` eliminating Windows `> NUL` shell dependencies.

### Phase 2: Sniper Execution Muscle (CURRENT)
- [x] Modular CCXT exchange connector with rate-limit circuit breakers.
- [x] 12-point sniper market scanning pipeline for cryptocurrency spot/futures.
- [x] SQLite atomic position tracking (`scionlog.sqlite`).
- [ ] Telegram interactive telemetry bot (`/status`, `/pnl`, `/positions`).
- [ ] Fallback equity market scanner via yfinance.

### Phase 3: Darwinian Learning & Self-Tuning (UPCOMING)
- [ ] Automated post-mortem extraction from closed trades into `lessons.py`.
- [ ] Parameter mutation testing via `hyperopt.py` against historical walk-forward windows.
- [ ] Automated syncing of trade learnings into `.orion/episodic/` and `orion.db`.
- [ ] Fitness scoring gate for trading parameter updates.

### Phase 4: Ecosystem Deployment & Scale (PLANNED)
- [ ] One-command headless daemon supervision (`pm2` / systemd / Windows Task Scheduler).
- [ ] Remote multi-node status heartbeat via Telegram webhook.
- [ ] Upstream synchronization pipeline for multi-project foundation instances.

---

## 2. Viability Scorecard

| Dimension | Score (1-10) | Evaluation & Risk Analysis |
| :--- | :---: | :--- |
| **Technical Complexity** | 8 | Asynchronous market data streaming, multi-process concurrency, and dynamic GraphRAG. |
| **Market Saturation** | 6 | High competition in basic bots; high blue-ocean gap for self-evolving agentic trading systems. |
| **Monetization Ease** | 9 | Quantifiable alpha generation and disciplined risk enforcement command high premium value. |
| **Solo-Dev Feasibility** | 8 | Highly modular, clean architecture with automated verification suites and zero external cloud debt. |

**Total Score: 31 / 40** (Viable to proceed with high-velocity execution).

---

## 3. Anti-Goals (The "Cut" List)

1. **NO Unvalidated Live Capital Orders**: Live execution is strictly locked behind `PAPER_TRADING=True` until a statistical win-rate >65% is demonstrated across 500 consecutive paper trades.
2. **NO Heavy Cloud Vectors on Lean Machines**: High-latency, expensive vector APIs are banned for core routing; SQLite FTS5 lexical matching + BM25 is the primary retrieval engine.
3. **NO Bloated Web Dashboards in v1**: Telegram CLI and interactive terminal outputs provide 100% of telemetry, keeping CPU and RAM footprints under 150MB.

---

## 4. Granular Detail References (JIT Child Mapping)
When deep product execution planning is needed, generate detail files using these official prefixes:
- `Plan_` — Feature scoping and sprint prioritization (e.g., `Plan_MVP_Scope.md`).
- `Launch_` — Release checklists and deployment gating (e.g., `Launch_Public_Release.md`).
- `Data_` — PnL analytics, KPI tracking, and execution logs (e.g., `Data_KPI_Dashboard.md`).
- `Rev_` — Capital allocation models and risk-adjusted returns (e.g., `Rev_Pricing_Strategy.md`).
