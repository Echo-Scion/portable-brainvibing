# Canon: Core Foundation & Architectural Standards (Portable Brainvibing)

## 1. Overview
This is the foundational canon for all projects. It defines the "Hukum Tata Negara" (Core Laws) that every AI agent must follow to ensure consistency, security, and scalability.

## 2. Core Principles
- **Agent-First Design:** Code must be structured so that it is easily parsable and maintainable by AI agents.
- **Predictable Modularity:** Prefer clean, isolated modules over large, monolithic structures.
- **Distributed Context (Double Lean):** In monorepos, maintain high-fidelity context at both root (platform) and app (features) levels to preserve token efficiency.
- **Code-As-Harness (Rejection Sampling):** Offload transition validity and constraint checking to external, verifiable code harnesses. Agents must synthesize their own verifier scripts to prevent "illegal moves" rather than relying purely on internal simulation.
- **Unidirectional Data Flow (UDF):** All state management MUST follow unidirectional flow patterns (e.g., Redux, Bloc, Riverpod) where state is immutable and mutations happen via distinct actions/events.
- **Strict Verification:** No feature is complete until it has been mechanically verified via automated tests and synthesized harnesses.

## 3. Mandatory Protocol
- All major tasks must be broken into atomic tasks using `ATOMIC_TASK.template.md`.
- Use "Surgical Munching" (targeted line reading) to minimize context rot.
- Utilize the AutoHarness Protocol (`rules/autoharness-protocol.md`) for tasks with complex constraints.

---
*Global Foundation Protocol v1.1.0*