# Strategic PM Rigor & Genesis Interrogation Matrix

> **Core Law**: Ruthless interrogation of the "Why" and "What Breaks" before designing the "How". All feature concepts and RFC proposals must survive the viability gate before entering architectural synthesis.

---

## 1. The 8 Core Viability Questions (Proposal Gate)

Before writing any architectural blueprint (`context/00_Strategy/BLUEPRINT.md`) or technical specification (`context/03_Tech/ARCHITECTURE.md`), the proposer must confirm all 8 viability questions are answered without jargon or ambiguity:

1. **Core Objective**: What specific problem or capability is being attempted? (Written in plain English with zero marketing buzzwords).
2. **Current State & Limitations**: How is this handled today in the codebase, and where does existing practice fail or hit ceilings?
3. **Core Technical Mechanism**: What is fundamentally new in this approach, and why will it succeed within the 4 Pillars without mandatory external bloat?
4. **Target Impact**: Who or what subsystem consumes this, and what measurable difference does it make to system throughput, developer speed, or user delight?
5. **Attack Surface & Risks**: What are the high-consequence failure modes, and what is the strategic payoff if mitigated?
6. **Resource & Token Economics**: What will this cost in local compute, memory footprint, database query volume, or cloud LLM token budget?
7. **Delivery Horizon**: What is the topological phase breakdown from foundational primitives to leaf presentation?
8. **Binary Verification Exams**: What are the intermediate test assertions and final deterministic commands (`Exit Code 0`) that objectively prove completion?

---

## 2. The 5-Advisor Adversarial Panel (`@get-more-perspectives`) & 6 Technical Vectors

When evaluating architectural trade-offs, feature proposals, or major PRs, convene the **5-Advisor Adversarial Panel** first:
- **Executive Verdict Header**:
  - **Vote Split**: `[X For / Option A, Y Against / Option B, Z Conditional]`
  - **Consensus Recommendation**: One decisive sentence naming the winning path.
  - **Most Weighted Lens**: Which 1–2 advisors carry the highest weight for this domain and why.
  - **Key Guardrail Condition**: The single condition that must hold true for this recommendation to succeed.
- **Independent Advisor Commitments (Every advisor MUST commit to `For`, `Against`, or `Conditional` — no generic "it depends", and at least two advisors must directly rebut each other's core assumption)**:
  1. **🔧 The Operator (Execution & Maintainability)**: Can this be built, tested, and maintained cleanly within the 5-Tier DNA strata without operational drag?
  2. **⚠️ The Skeptic (Failure Modes, Security & State Corruption)**: What is the worst-case failure mode, race condition, silent fallback, or abuse vector?
  3. **🚀 The Visionary (Asymmetric Upside & Product Moat)**: Does this unlock compounding 2–3 year product value or merely copy a generic template?
  4. **👤 The Customer Advocate (User Friction, A11y & State Recovery)**: Does this reduce real user cognitive load and handle all 6 state families, or is it internal engineering friction disguised as a feature?
  5. **💰 The Finance Mind (Token, Cloud & Engineering ROI)**: How does this impact LLM token burn, SQLite/DB query load, latency, and engineering opportunity cost?

### Technical Deep-Dive Vectors
After the 5-Advisor Panel verdict, verify the 6 technical implementation vectors:

| Stress-Test Lens | Core Focus | Critical Interrogation |
| :--- | :--- | :--- |
| **1. Contrarian MVC / YAGNI** | Simplicity & Code Minimization | *Why does this feature need to exist? Can existing codebase utilities, stdlib primitives, or native CLI companions solve 90% of this without new abstractions?* |
| **2. Token & Resource Economics** | Scaling & Budget Ceilings | *What is the peak QPS, memory footprint, SQLite query load, or LLM token budget? Will this hit context window or token limits at scale?* |
| **3. DX & Developer Ergonomics** | Cognitive Load & Usability | *Is the API/CLI contract intuitive? Does it adhere to ecosystem conventions? Are error messages actionable, or does it add developer friction?* |
| **4. State Migration & Rollback** | Rollout Safety & Version Skew | *How do existing serialized models, SQLite tables, or configs migrate? Does this break backwards compatibility? How is safe rollback handled mid-migration?* |
| **5. Telemetry & 3 AM Observability** | Operational Visibility | *Are operations traceable via structured events? Can an oncall engineer diagnose a failure in production at 3 AM using local logs and telemetry?* |
| **6. Long-Term Tech Debt** | Architectural Longevity | *Does this introduce tightly coupled state machines or leaky abstractions that will be painful to maintain across 2+ years of evolution?* |

---

## 3. Anti-Glazing & Truth Invariants

- **Critique First**: Even when an architectural concept is strong, lead with what is missing, risky, or over-complicated before affirming merits.
- **Banned Flattery Adjectives**: Strictly eliminate validating adjectives (*brilliant, great, smart, spot-on, perfect, excellent*) when evaluating proposals.
- **Banned Apologies**: Never emit polite apologies (*I apologize, I am sorry*); state corrected technical logic or trade-offs directly.
- **Earned Agreement**: Agree only when the concept has survived rigorous, objective interrogation against the 8 Core Viability Questions.
