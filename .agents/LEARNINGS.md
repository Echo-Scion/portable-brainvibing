# Persistent Learnings & Post-Mortems

This file serves as the collective memory for AI agents working in this infrastructure. It documents systemic failures, complex bug fixes, and architectural "gotchas" to prevent repetition of errors.

## 0. Log Template
> **[DATE]** | **[TASK_ID]** | **[TIER]**
> - **Issue**: Brief description of what went wrong or the complexity faced.
> - **Root Cause**: The foundational reason for the failure.
> - **Solution**: The specific pattern or fix that worked.
> - **Debt/Warning**: Future considerations or brittle areas discovered.

---

> **2026-05-20** | **QMD_SEMANTIC_SEARCH_FAILURE** | **STANDARD**
> - **Issue**: Failed to execute `npx @tobilu/qmd query` and subsequently crashed on `node qmd.js query`.
> - **Root Cause**: 
>   1. Path Resolution: `npx` failed to resolve inside the PowerShell/CMD environment when intercepted by RTK/Hook.
>   2. VRAM OOM: When bypassing `npx` and using direct node execution, the `node-llama-cpp` module failed to allocate 633MB of VRAM on Vulkan (`vk::Device::allocateMemory: ErrorOutOfDeviceMemory`) during the reranking phase.
> - **Solution**: Acknowledge hardware limits. Semantic query on this specific Windows machine will fail if the local LLM reranker attempts to load into a saturated GPU. 
> - **Debt/Warning**: The QMD integration script might need a `--no-rerank` flag or a CPU-only fallback for machines with low/saturated VRAM. Until then, rely on `grep_search` if QMD fails with OOM.
