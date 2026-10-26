---
description: Obsidian interoperability contract for authored context, Orion persistence, and generated vault projections.
activation: triggered during brain export-vault and Obsidian graph projection workflows.
version: 0.0.2
last_updated: 2026-10-15
---

# Obsidian Interoperability Contract

## Ownership

- `context/` and `.agents/` remain authored sources.
- `.orion/orion.db` remains the canonical computed graph and search store.
- `.orion/vault/` is a generated Obsidian-compatible projection.
- Obsidian and Graph View are visualization and navigation clients, not persistence authorities.

## Wikilinks

- Use `[[wikilinks]]` for internal Markdown-note relationships.
- Preserve typed graph relations in Orion edges; wikilinks do not replace `page|implements`, `page|extends`, or `page|contradicts` relationships.
- Generated vault notes may contain inbound and outbound wikilinks, frontmatter, tags, and community indexes.

## Export Boundary

Run:

```powershell
python .agents/scripts/orion.py brain export-vault
```

The command reads `.orion/orion.db` and writes only `.orion/vault/`. It MUST NOT overwrite authored notes under `context/`, `.agents/`, or any other source directory.

## Optional Formats

- `.canvas` and `.base` files are optional human-facing projections.
- Obsidian CLI, Defuddle, and Knap remain optional adapters; no external package is required for core graph persistence.
