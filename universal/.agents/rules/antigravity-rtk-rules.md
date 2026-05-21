---
description: Token-optimized CLI proxy rules and decision tree for Google Antigravity.
activation: when using shell commands

version: 3.0.0
last_updated: 2026-05-20
---
# RTK - Rust Token Killer (Google Antigravity)

**Usage**: Token-optimized CLI proxy for shell commands. RTK filters and compresses command output before it reaches the LLM context, saving 60-90% tokens.

## 1. RTK Decision Tree (MANDATORY)

Before running any terminal command, consult this tree:

```
Q1. Does the command output a large text stream? (e.g., git log, find, grep, docker ps, cargo test, npm audit)
    ├── YES -> Use `rtk <cmd>`
    └── NO -> Proceed to Q2

Q2. Is the command interactive or does it require raw unfiltered JSON output? (e.g., interactive prompts, JSON API responses needed for exact parsing)
    ├── YES -> Use RAW command (NO rtk)
    └── NO -> Use `rtk <cmd>` as default
```

## 2. Execution Syntax

Always prefix shell commands with `rtk` unless it hits the "NO" branch above.

✅ **DO:**
```bash
rtk git status
rtk cargo test
rtk grep "pattern" src/
rtk find "*.rs" .
rtk docker ps
rtk npm audit
```

❌ **DONT:** (Never use raw commands for verbose output)
```bash
git log --all # Bad: Will flood token context. Use: rtk git log
```

## 3. Meta Commands

If RTK compression breaks output legibility or hides an error you need to see, use proxy commands:

```bash
rtk gain              # Show token savings
rtk gain --history    # Command history with savings
rtk proxy <cmd>       # Run raw (no filtering, for debugging)
```