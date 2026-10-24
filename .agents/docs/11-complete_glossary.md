# VOLUME XI: COMPLETE GLOSSARY — Architecture Terms & Definitions

---

| Term | Category | Operational Definition |
|:---|:---|:---|
| **Active Router / Master BIOS** | Core Architecture | The root instruction file (`AGENTS.md`, with host adapters like `GEMINI.md` or `CLAUDE.md`) executed upon agent session wake, enforcing guardrails and JIT routing. |
| **Adversarial Twin Protocol** | Quality & Verification | Mandatory verification method where the agent generates attack scripts or edge-case tests against its own code before claiming implementation success. |
| **Agentic Amnesia** | LLM Failure Mode | Degradation or loss of instructional constraints when context windows grow large or when sessions restart mid-workflow. |
| **Anchor Timeline Recall** | Observational Memory | On-demand retrieval command (`orion.py brain recall <anchor_id>`) that expands the raw `recall_turns` behind an ephemeral observation anchor (`[O1]`) or generation ID (`GEN-...`). |
| **Anti-Affirmation (Triad Threat Probe)** | Architecture Audit | Review mandate requiring the agent to proactively treat proposals as flawed, probing for Boundary, Resource, and Silent Fallback gaps. |
| **AST Hollowing** | Token Optimization | Extraction of structural code skeletons (classes, methods, signatures) while stripping function bodies to reduce context size by ~90%. |
| **AutoHarness Protocol** | Verification Engine | Automated generation of verification harnesses (Action-Verifier, Action-Filter, Policy) for destructive or multi-step operations. |
| **Barrier Escalation** | Self-Learning Loop | Automated gate in `ObservationLedger.check_rule_violations()` that escalates a 2nd repeated violation of the same rule to a Tier-0 mechanical check (`[BARRIER_ESCALATION_CANDIDATE]`). |
| **Bento Task Slicer** | Execution Resilience | Sequential task engine (`commands/bento_slicer.py`) that slices multi-step plans into single atomic task sheets (`.orion/working/ACTIVE_TASK.md`) with topological sorting ($T_0 \to T_5$), bottom-up same-file ordering, live AST anchor recalibration, and a post-condition disk mutation gate. |
| **Bento-Box Law** | Resource Allocation | Behavioral rule restricting BUDGET-tier models to at most 1 logic file modification (max 3 scaffolding targets) per iteration to prevent scope drift. |
| **Circuit Breaker** | Execution Resilience | Automatic halt protocol triggered when any tool or test fails 3 times consecutively, stopping execution cascades and requesting human input. |
| **Contradiction Engine** | Knowledge Integrity | Detection and resolution mechanism in `commands/brain.py` (`orion contradict`) that flags colliding predicate triplets and adjusts edge confidence scores. |
| **Core Ceiling Ratchet (`core_max_lines`)** | Ecosystem Governance | Frontmatter line-count ceiling enforced on `SKILL.md` and root instruction files by `verify_agents.py` to prevent instruction bloat. |
| **Darwinian Heartbeat** | Self-Learning Loop | Automated check in `hooks/pre-agent-wake.py` evaluating `LEARNINGS.md` and `OBSERVATIONS.md`; flags `evolution_overdue` when unprocessed lessons $\ge 3$. |
| **Dual-Level GraphRAG** | Cognitive Retrieval | Retrieval architecture combining Global/Macro Louvain community summaries with Local/Micro 1-hop triplet graph expansion and vector similarity. |
| **Dynamic Graph Topology Clustering** | Context Packaging | Clustering methodology in `packer.py` utilizing PageRank centrality and AST import graphs to cluster codebase volume organically, preventing arbitrary bucket collapses. |
| **Episodic Memory** | Knowledge Base | Compressed journal entries capturing cross-session architectural decisions, bug fixes, and milestones in `.orion/episodic/`. |
| **Formal State Machine (FSM)** | Execution Resilience | Atomic transaction tracker logging superstep progression to `.orion/working/execution_state.json`, enabling crash recovery across IDE restarts. |
| **Four (4) Anchored Pillars** | Foundation Platform | The zero-daemon execution stack: Pure Python 3.10+ Stdlib, Cargo Rust (`rtk` + `sg`), local Ollama (`nomic-embed`), and Bun static runtime. |
| **FTS5 Porter Indexing** | Local RAG | SQLite5 Full-Text Search virtual table with Porter stemming, delivering sub-millisecond lexical search over indexed workspace files. |
| **Generational Rollover** | Observational Memory | Zero-LLM memory consolidation (`orion.py brain rollover`) that distills unarchived `recall_turns` into a single Head Reflection in `memory_generations` using Shannon Surprisal scoring and stamps old records with `superseded_by`. |
| **Genomic Ledger** | Self-Learning Loop | `EVOLUTION_LOG.jsonl` — an append-only log recording approved mutations, friction sources, and fitness deltas across iterations. |
| **Ghost Token / Ghost Reference** | Integrity Verification | An index entry, skill reference, or documentation link referencing a file that does not physically exist in the repository. |
| **Interactive 4-Turn Audit Protocol** | Context Packaging | Structured multi-turn audit workflow (`00_GEMINI_WEB_AUDIT_PROMPT.txt`) dividing review across 4 distinct phases with signature preservation mandates. |
| **Iron Evidence Law** | Core Mandate | Behavioral rule: `Exit Code 0` is necessary but insufficient; positive verification of stdout/stderr assertions and state change is required. |
| **Just-In-Time (JIT) Routing** | Context Routing | Dynamic skill and rule dispatch based on prompt keywords, loading only targeted files to prevent "Lost in the Middle" attention loss. |
| **Lessword Protocol** | Communication Standard | Terse, high-density communication standard eliminating conversational filler, articles, and hedging (~75% token savings). |
| **Lost in the Middle** | LLM Failure Mode | Empirical tendency of language models to recall instructions at the start and end of large prompts while ignoring middle instructions. |
| **Louvain Modularity Clustering** | Graph Algorithms | Pure-Python algorithm in `core/orion_graph.py` computing hierarchical community clusters on knowledge graph edges without external pip packages. |
| **NanoBrain** | Local AI Coprocessor | Local model orchestration engine (`commands/brain.py`) supporting full, embed-only, llm-only, and pure-FTS5 operational modes. |
| **Observation Ledger** | Self-Learning Loop | 5-status governance ledger (`.agents/OBSERVATIONS.md` and `OBSERVATIONS.archive.md`) tracking friction events, rule violations, and operator habits across `open`, `validated`, `promoted`, `parked`, and `superseded` states. |
| **Omni-Buffer** | IDE Synchronization | Cache-aware state file (`.orion/working/context.json`) populated by `pre-agent-wake.py` with active editor file, terminal error, active Bento task, and a 5-minute SHA-256 structural hash gate. |
| **Operator Habit Miner** | Self-Learning Loop | Pattern detector (`mine_operator_habits`) in `commands/reflexion.py` that identifies recurring manual developer CLI sequences ($\ge 3$ occurrences) for workflow automation. |
| **Post-Condition Disk Mutation Gate** | Execution Resilience | Verification check in `bento_slicer.py` (`cmd_next`) that inspects the target file on disk before running tests and rejects unapplied patches with `Exit Code 2 ([BENTO NO-OP REJECTED])`. |
| **Pre-Audit Static Radar** | Context Packaging | Deterministic pre-computed risk index embedded in Bundle 01 identifying broad/silent exception handlers (`catch {}`), native execution sinks (`spawn`, `execAsync`), and large polyglot modules. |
| **Prompt-in-Data Shield** | Security Gate | Security mechanism unconditionally escaping prompt injection tags (`<system>`, `<prompt_instructions>`, `</artifact>`) across all lines including code blocks. |
| **Prose Authenticity** | Documentation Standard | Writing standard (`rules/prose-authenticity.md`) eliminating 54 structural AI tells, binary contrast reversals, and corporate buzzwords. |
| **RTK (Rust Token Killer)** | Token Optimization | Compiled Cargo Rust binary proxying terminal execution to strip progress bars, download stats, and info logs (60–90% noise reduction). |
| **Save Point Protocol** | Version Control | Mandatory atomic git commits following every verified sub-step or passing test in an implementation plan. |
| **Semantic Triplet** | Knowledge Graph | Structured `(Subject, Predicate, Object)` dependency extracted from source code and stored in the `edges` and `nodes` SQL tables. |
| **Small Model Superiority (SMS)** | Cost Optimization | Telemetry metric and routing principle demonstrating that constrained models operating with tight harnesses outperform unbounded large models. |
| **Stale Data & Cache-Aware TTL Gate** | IDE Synchronization | 5-minute SHA-256 structural hash check in `pre-agent-wake.py` that preserves LLM KV prompt caches on unchanged turns and emits a `temporal_gap_marker` after idle gaps. |
| **Strict TDD** | Development Standard | Mandatory RED-GREEN-REFACTOR cycle with mechanical rollback (`git stash`) if implementation code precedes a verified failing test. |
| **Systematic Debugging** | Diagnostic Protocol | 4-phase scientific root-cause protocol: Investigation → Pattern Analysis → Hypothesis Testing → Surgical Fix. |
| **Tier Mismatch** | Resource Allocation | Condition where the active model class is weaker than required for the task tier, triggering an immediate `[ABORT: TIER MISMATCH]`. |
| **Unified Context Packer** | Context Packaging | Zero-pip context packaging engine (`packer.py` / `digestpack`) that clusters codebases into at most 10 Markdown bundles (`.md`) across `arch`, `hybrid`, and `full` tiers. |
| **Unified Response Footer** | Communication Standard | Standardized navigation block terminating agent responses (`CHECKPOINT`, `EVIDENCE`, `EVALUATION`, `RECOMMENDED TIER`, `NEXT TASK`). |
| **Zero-Pip Sovereign Mandate** | Architecture Standard | Architectural mandate requiring core orchestration to run purely on standard library modules (`ast`, `re`, `sqlite3`, `urllib`), zero pip required. |
