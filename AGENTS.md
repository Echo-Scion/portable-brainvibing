# AGENTS: The `.agents` Ecosystem Guide (Beginner-Friendly Edition)

Welcome to the **Portable Brainvibing AI-Surgical Infrastructure**. Think of the `.agents` folder and its contents as the "brain," "playbook," and "toolbox" for your AI assistant.

While software development can often seem like magic, this ecosystem brings order, safety, and predictability to how the AI operates. This document is designed to help you, even as a non-technical reader, understand exactly how this system is structured, how it keeps your code safe, and how it organizes complex tasks.

---

## 🏛️ CANONS (`canons/`)
**The Constitution of the Project**

These are the absolute, unchangeable laws regarding the software's architecture. They define the structural foundation of your application. The AI is strictly forbidden from violating these foundational rules.
- **Global Architecture** (`global/core-architecture.md`): The overarching rules for how different parts of your application talk to each other. It dictates state management principles and structural boundaries.
- **Automated Harnesses** (`global/harnesses/README.md`): The definitions for automated Action-Verifier execution loops, allowing the AI to safely test its own work.
- **Microservices** (`micro/README.md`): The rules for building small, independent pieces of logic (like edge functions) safely without tightly coupling them.

## 🛡️ RULES (`rules/`)
**Traffic Lights & Security Guards**

This folder acts as a "Pre-Execution Firewall." It contains strict restrictions and obligations to ensure the AI works safely, cleanly, and professionally.
- **Cognitive & Constraint Rules**: Forces the AI to think critically rather than just being a yes-man. For example, the *Anti-Affirmation Mandate* prevents the AI from blindly agreeing with bad ideas; it must always look for flaws and edge cases first.
- **Engineering Standards**: Strict coding paradigms (`flutter-standards.md`, `web.md`) that ensure clean, maintainable, and highly performant code tailored to specific platforms like mobile or web.
- **Security & Workflow**: Ensures the AI never leaks passwords or API keys (`security-guardrails.md`), enforces "zero-trust" security, and defines how it should safely manage Git version control (`git-workflow.md`).

## 🎯 SKILLS (`skills/`)
**The AI's Professional Hats**

Depending on the task you assign, the AI can switch "personas" or roles. Each skill folder equips the AI with deep, domain-specific expertise, ensuring it approaches problems like a seasoned specialist rather than a generic bot.
- **`project-architect`**: The Planner. Turns your rough ideas into concrete, step-by-step technical blueprints (PRDs), prioritizing Minimum Viable Complexity.
- **`backend-orchestrator`**: The Engine Builder. Handles databases, server infrastructure, data pipelines, caching layers, and system performance.
- **`frontend-experience`**: The UI/UX Polisher. Ensures the application looks beautiful, is user-friendly, and has zero visual layout bugs.
- **`integrity-sentinel`**: The Quality Assurance Inspector. Hunts for security vulnerabilities, performs system audits, and finds bugs before the app goes public.
- **`saas-strategist`**: The Business Advisor. Helps integrate payment gateways (like Stripe), subscription models, and strategies to grow your user base.
- **`data-logic`**: The Data Manager. Handles complex state management, data pipelines, and ensures data remains predictable and immutable.
- **`project-operator`**: The DevOps Engineer. Manages code releases, cleans up technical debt, and handles complicated repository deployments.
- **`api-contract`**: The Bouncer. Defines strict data contracts (like Zod schemas) so that no malformed or dangerous data ever reaches your business logic.
- **`meta-agent-admin`**: The Librarian. Manages the `.agents` ecosystem itself, defining new rules and maintaining the AI's own documentation.
- **`ui-finish`**: The Visual Engineer. Applies premium Liquid Glass aesthetics, animations, and handles loading/error states gracefully.
- **`qmd`**: The Knowledge Retriever. Searches markdown knowledge bases, notes, and documentation using QMD semantic search.
- **`cost-optimizer`**: The Efficiency Manager. Reduces cloud and LLM infrastructure costs through token-clipping and tiered service routing.
- **`caveman`**: The Token Saver. Compresses communication into ultra-terse "caveman" mode to save context tokens.
- **`caveman-compress`**: The File Compressor. Compresses natural language memory files into caveman format to save input tokens.
- **`index-project`**: The Indexer. Automates the indexing of the current project into the QMD semantic search engine.

## 🔄 WORKFLOWS (`workflows/`)
**Standard Operating Procedures (SOPs)**

These are step-by-step guidebooks that prevent the AI from doing things randomly. They provide a structured routine for common software development cycles:
- **Project Setup** (`project-init.md`): Explains exactly how to start a brand new project from scratch, including scaffolding the initial directories and creating roadmaps.
- **Development Loops** (`strict-tdd.md`, `app-builder.md`, `flutter-debug.md`): Logical sequences for test-driven development (forcing the AI to write tests before building features) or rapidly scaffolding components.
- **Maintenance & Release** (`prod-deploy.md`, `context-prune.md`): Safe, checklist-driven procedures for releasing the application to live servers and cleaning up the AI's temporary memory to save on API token costs.

## ⚙️ MECHANICAL TOOLING (SCRIPTS, TEMPLATES & EVALS)
**The Essential Utilities**

These are additional tools and templates used behind the scenes to make the AI's daily work easier, faster, and more consistent:
- **`scripts/`**: Small automated Python utilities used to compress the AI's memory, synchronize the workspace, index the project into QMD, and check overall system health.
- **`templates/`**: Standardized molds (like project blueprints or architecture plans) ensuring that every document generated by the AI has a clean, identical, and professional format.
- **`evals/` & `docs/`**: Measurement tools to benchmark how smart and compliant the AI is over time, alongside human-readable deployment manuals for developers.

---

## Changelog

| Version | Date | Notes |
| :--- | :--- | :--- |
| **1.3.0** | 2026-04-18 | Modernize foundation: adopt RTK, QMD, and Caveman. Remove obsolete manual catalogs. |
| **1.2.0** | 2026-03-26 | Integrate 10 Prompt Patterns, Root GEMINI.md, and evals/docs folders |
| **1.1.0** | 2026-03-20 | Unified Logic: Established a clear 4-pillar structure and the 82-file SaaS mapping protocol. |
| **1.0.0** | 2026-03-19 | Clean Reset to V1.0.0 |
| **0.9.0** | 2026-03-15 | Initial baseline |
