# Wiki Schema & Operations Manual

## 1. Autonomy Configuration
`autonomy_level: balanced`
- **balanced**: Auto-commit non-destructive writes. Pause on contradictions.
- **high**: Attempt auto-resolution of all conflicts except Canon violations.
- **strict**: Emit a Triage Report for EVERY change.

## 2. Source Classification & Confidence
| Category | Source Path | Confidence |
|----------|-------------|------------|
| `canon` | `.agents/canons/` | canonical |
| `rule` | `.agents/rules/` | authoritative |
| `context` | `context/` | authoritative |
| `memory` | `MEMORY.md`, `HANDOFF.md` | episodic |

## 3. Frontmatter Standard
All generated pages MUST use:
```yaml
---
type: concept
source-category: rule
sources: [path/to/source.md]
source_sha256: [hash]
pillar: [strategy|product|creative|tech]
confidence: authoritative
---
```

## 4. Typed Relationships
Do not use raw `[[page]]`. Use:
- `[[page|extends]]`
- `[[page|contradicts]]`
- `[[page|implements]]`
