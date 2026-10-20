---
name: lessword-compress
description: >
  Compress natural language memory files (CLAUDE.md, todos, preferences) into lessword format
  to save input tokens. Preserves all technical substance, code, URLs, and structure.
  Compressed version overwrites the original file. Human-readable backup saved as FILE.original.md.
  Trigger: /lessword-compress FILEPATH or "compress memory file"
---

# Lessword Compress

## Purpose

Compress natural language files (CLAUDE.md, todos, preferences) into lessword format to reduce input tokens. Compressed version overwrites original. Human-readable backup saved as `<filename>.original.md`.

## Trigger

`/lessword-compress <filepath>` or when user asks to compress a memory file.


## Process & Tooling

To compress a target file using the Native Orion Compactor (unified with chat intensity levels):
```bash
# 3 Unified Compression Tiers:
python .agents/scripts/orion.py compact lite <filepath>         # ~15% reduction: Lossless cleanup & whitespace normalization
python .agents/scripts/orion.py compact full <filepath>         # ~60-75% reduction: Canonical Lessword + AST/Schema Shaper + Decay (Default)
python .agents/scripts/orion.py compact ultra <filepath>        # ~75-85% reduction: Shannon Surprisal + Telegraphic Abbrev

# Project-wide episodic memory compaction (default full):
python .agents/scripts/orion.py compress
```

### Mechanical Invariants & Protections:
1. **Frontmatter Isolation (`split_frontmatter`)**:
   - YAML headers delimited by `---` are detached before compression.
   - Prepend back verbatim upon output write to eliminate LLM header stripping.
2. **Secrets & Sensitive File Hard-Refusal**:
   - Hard refuse files matching: `.env*`, `credentials*`, `secrets*`, `passwords*`, `id_rsa*`, `.ssh/`, `.aws/`, `.gnupg/`, `*.pem`, `*.key`.
   - Never stream secrets to token reduction processors.
3. **Format Sniffing & Skip Whitelist**:
   - **Compressible**: `.md`, `.mdc`, `.txt`, `.markdown`, `.rst`, `.typ`, `.typst`, `.tex`, and extensionless prose files.
   - **Skip (Never Compress)**: Code and configs (`.py`, `.js`, `.ts`, `.json`, `.yaml`, `.yml`, `.toml`, `.lock`, `.css`, `.sql`, `.sh`), and known build targets (`Dockerfile`, `Makefile`, `CMakeLists.txt`).
4. **Deterministic Backup**:
   - Original file is backed up to `<filepath>.original.md` before overwriting.
   - `<filepath>.original.md` is immune to subsequent compression.
5. **SyntaxAnchorGuard (Verbatim Isolation)**:
   - Stashes fenced code blocks, inline backticks, URLs, wikilinks, file paths with line numbers, `$ENV` vars, and uppercase constants into collision-free slot tokens (`\x00__orion_anchor_{seq}__\x00`).
   - Unlocks anchors verbatim post-compression to guarantee zero code corruption.
6. **PayloadStreamShaper (Structural AST & Schema Awareness)**:
   - Automatically hollows code implementations to skeleton signatures (`shrink_ast_python` / `shrink_ast_generic`).
   - Folds large JSON arrays into representative schema samples (`shrink_json` / `shrink_csv`).
   - Condenses error traces to header + first 10 frames + 3 root cause frames.
7. **ChronologicalSectionDecay (Document & Memory Decay)**:
   - Preserves newest 2 markdown sections verbatim (`##`).
   - Compacts intermediate sections using `full` mode.
   - Decays older historical sections into 1-line bullet summaries.
   - Never touches sacred anchor sections (`Resume Point`, `Anti-Goals`, `Fractal Shorthand`).
8. **SafetyBoundaryEscape (Auto-Clarity Protection)**:
   - Automatically halts sentence stripping and emits full clear English prose when detecting irreversible destructive operations (`DROP TABLE`, `DELETE FROM`, `rm -rf`, `reset --hard`, `force push`, CVE advisories).

## Compression Rules

### Remove
- Articles: a, an, the
- Filler: just, really, basically, actually, simply, essentially, generally
- Pleasantries: "sure", "certainly", "of course", "happy to", "I'd recommend"
- Hedging: "it might be worth", "you could consider", "it would be good to"
- Redundant phrasing: "in order to" → "to", "make sure to" → "ensure", "the reason is because" → "because"
- Connective fluff: "however", "furthermore", "additionally", "in addition"

### Preserve EXACTLY (never modify)
- Code blocks (fenced ``` and indented)
- Inline code (`backtick content`)
- URLs and links (full URLs, markdown links)
- File paths (`/src/components/...`, `./config.yaml`)
- Commands (`npm install`, `git commit`, `docker build`)
- Technical terms (library names, API names, protocols, algorithms)
- Proper nouns (project names, people, companies)
- Dates, version numbers, numeric values
- Mathematical ratios (`60:30:10`, `16:9`, `1:1`)
- Physical bounds, comparison operators, and units (`<= 8px`, `>= 16000`, `100%`, `300 lines`, `30s`)
- Closed enumeration sets and categorized taxonomies (e.g., Triad vectors, architectural archetypes, dial ranges 1–10)
- Deterministic verification gates and assertion commands (`Exit Code 0`, `reproduction test > 0`)
- Environment variables (`$HOME`, `NODE_ENV`)

### Preserve Structure
- All markdown headings (keep exact heading text, compress body below)
- Bullet point hierarchy (keep nesting level)
- Numbered lists (keep numbering)
- Tables (compress cell text, keep structure)
- Frontmatter/YAML headers in markdown files

### Compress
- Use short synonyms: "big" not "extensive", "fix" not "implement a solution for", "use" not "utilize"
- Fragments OK: "Run tests before commit" not "You should always run tests before committing"
- Drop "you should", "make sure to", "remember to" — just state the action
- Merge redundant bullets that say the same thing differently
- Keep one example where multiple examples show the same pattern

CRITICAL RULE:
Anything inside ``` ... ``` must be copied EXACTLY.
Do not:
- remove comments
- remove spacing
- reorder lines
- shorten commands
- simplify anything

Inline code (`...`) must be preserved EXACTLY.
Do not modify anything inside backticks.

If file contains code blocks:
- Treat code blocks as read-only regions
- Only compress text outside them
- Do not merge sections around code

## Pattern

Original:
> You should always make sure to run the test suite before pushing any changes to the main branch. This is important because it helps catch bugs early and prevents broken builds from being deployed to production.

Compressed:
> Run tests before push to main. Catch bugs early, prevent broken prod deploys.

Original:
> The application uses a microservices architecture with the following components. The API gateway handles all incoming requests and routes them to the appropriate service. The authentication service is responsible for managing user sessions and JWT tokens.

Compressed:
> Microservices architecture. API gateway route all requests to services. Auth service manage user sessions + JWT tokens.

## Boundaries

- ONLY compress natural language files (.md, .txt, .typ, .typst, .tex, extensionless)
- NEVER modify: .py, .js, .ts, .json, .yaml, .yml, .toml, .env, .lock, .css, .html, .xml, .sql, .sh
- If file has mixed content (prose + code), compress ONLY the prose sections
- If unsure whether something is code or prose, leave it unchanged
- Original file is backed up as FILE.original.md before overwriting
- Never compress FILE.original.md (skip it)
