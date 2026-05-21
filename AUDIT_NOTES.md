Deep Audit Notes.

Python Scripts.
Logic: MyPy types broken. `deploy_foundation.py` `selected_ais=None`. Unused imports in `deploy_foundation.py`, `preflight_check.py`, `qmd_wiki_graph.py`. Dead code: `has_markers`.
Performance: Scripts OK.
Security: Low risk: `subprocess` calls without `shell=False`. High risk: Weak MD5 hash in `verify_agents.py`. Blind exceptions (`pass`) in `ingest_wiki.py`, `token_audit.py`, `verify_agents.py`. Must log errors.
Concurrency: OK.

Markdown Rules.
Logic: Redundancy in `security-guardrails.md` and `web.md`. `GEMINI.md` mandates Caveman. `code-review.md` requires PR empathy. Hallucination gap. `app-builder.md` missing TIER gate.
Performance: `context-standards.md` blocks long files. Good. But `offensive-audit.md` (5.5k) and `context-standards.md` (11.3k) too big. Token waste.
Security: `offensive-audit-protocol.md` mandates `invoke_subagent`. If absent, AI crashes. `wiki-ops.md` assumes wiki ingestion works. If script fails silently, AI hallucinates context.
Concurrency: OK.
