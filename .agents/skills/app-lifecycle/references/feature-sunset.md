---
name: feature-sunset
description: 4-Phase deprecation, expand-contract transition, and dead code sunsetting protocol.
---

# 🌅 WORKFLOW: PHASED DEPRECATION & SUNSETTING (`/feature-sunset`)

> **The Liability Law**: Code is a liability, not an asset. Unused, duplicate, or obsolete implementations carry perpetual maintenance, security patching, and mental drag. Deprecation is the discipline of actively retiring code that no longer earns its keep.

Execute these four phases sequentially when replacing an architecture, API, or sunsetting a feature:

## Phase 1: Replacement Construction & Parity Validation
1. **Zero Deprecation Without Replacement**: Never announce or trigger deprecation before the replacement implementation is verified in production.
2. **Feature & Edge-Case Parity**: Ensure the replacement satisfies 100% of critical paths and error handling handled by the legacy system.
3. **Migration Verification Command**: Provide an automated verification script or command confirming the new implementation behaves identically on current data.

## Phase 2: Advisory Notice & Telemetry Instrumentation
1. **Telemetry Audit**: Instrument usage counters or log warnings on the legacy entry points to quantify remaining active callers.
2. **Structured Deprecation Notice**: Mark the legacy interface with explicit docstrings, `@deprecated` annotations, or HTTP warning headers:
   ```markdown
   **Status**: DEPRECATED as of YYYY-MM-DD
   **Target Removal Date**: YYYY-MM-DD
   **Replacement**: [Module/API Identifier]
   **Migration Guide**: [Link to ADR or documentation]
   ```
3. **Migration Documentation**: Provide an exact, line-by-line migration example showing before/after diffs.

## Phase 3: Dual-Write & Expand-Contract Transition
1. **Data Layer Expand-Contract**: For database schemas or persistent state:
   - *Expand*: Add new columns/tables without removing existing ones.
   - *Dual-Write*: Application writes to both old and new stores while reading from the old.
   - *Backfill*: Migrate historical records into the new schema.
   - *Switch Read*: Flip reads to the new store while maintaining writes to both.
   - *Contract*: Cease writes to the old store; safely drop legacy columns/tables.
2. **Incremental Consumer Migration**: Migrate downstream callers one service/module at a time. Run regression tests after each migration step.

## Phase 4: Compulsory Sunset & Dead Code Purge
1. **Hard Deletion Gate**: Once telemetry confirms 0 active calls remain (or hard migration deadline expires), remove all legacy code.
2. **Zero Dead Code Residue**: Delete obsolete endpoints, unused DTO schemas, fallback branches, and dead dependencies.
3. **Archive & ADR Update**: Update the corresponding ADR status to `Deprecated` or `Superseded`.
