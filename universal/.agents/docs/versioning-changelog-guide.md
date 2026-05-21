# Versioning & Changelog Management Guide

## Overview

The `.agents` ecosystem uses **semantic versioning** with an automated publication pipeline that synchronizes changes from `_foundation/.agents` (master) to `portable brainvibing/` (distribution) while maintaining version history and changelog entries.

---

## 1. Semantic Versioning (SemVer)

### Format
```
MAJOR.MINOR.PATCH

Example: 1.2.23
  ↓      ↓   ↓
  |      |   └─ Patch: Bug fixes, internal improvements (backward compatible)
  |      └────── Minor: New features, non-breaking additions
  └───────────── Major: Breaking changes, major refactors
```

### Version File
- **Location**: `portable brainvibing/VERSION`
- **Content**: Plain text, single line with version number

---

## 2. Changelog Structure

### Location
`portable brainvibing/CHANGELOG.md`

### Format
Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) standard:

```markdown
# Changelog

All notable changes documented here. Project adheres to [Semantic Versioning](https://semver.org/).

## [1.2.23] - 2026-03-29
### Changed
- Updated skills routing for decoupled discovery

### Added
- New security audit features

## [1.2.22] - 2026-03-28
### Changed
- Ecosystem refactor to 11 core skills
```

### Entry Types
- **Added**: New features
- **Changed**: Changes to existing features
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

---

## 3. Automated Update Pipeline

### Command
```bash
```

### Version Types
| Type | Behavior | Example |
| `patch` | Increment patch only | 1.2.22 → 1.2.23 |
| `minor` | Increment minor, reset patch | 1.2.22 → 1.3.0 |
| `major` | Increment major, reset minor+patch | 1.2.22 → 2.0.0 |
| `auto` | Auto-detect from message keywords | See below |

### Auto-Detection Keywords
- Contains "break" or "breaking" → `major`
- Contains "feature" or "add" → `minor`
- Default → `patch`

---

### Publication Workflow (/update-sync)

### Pre-Flight (Verification)
```bash
# Step 0: Verify Binary Oratory compliance
@core-guardrails.md

# Step 1: Run local verification loop
/verify-loop
```

### Sanitization & Sync
```bash
# Step 2: Publish with version bump
```

**What happens automatically**:
1. ✅ Sanitizes content (removes secrets, local paths, temp files)
2. ✅ Strips blacklisted files (audit scripts, local workflows, personal data)
3. ✅ Syncs `.agents/` folder → `portable brainvibing/.agents/`
4. ✅ Updates `VERSION` file (1.2.22 → 1.2.23)
5. ✅ Inserts CHANGELOG.md entry with today's date
6. ✅ Updates README.md & AGENTS.md version markers
7. ✅ Extracts 5 most recent MAJOR.MINOR releases for documentation

### Verification (Post-Sync)
```bash
# Step 3: Verify portable version integrity
python portable\ brainvibing/.agents/scripts/verify_agents.py
```

### Finalization
```bash
# Step 4: Commit and push
cd portable\ brainvibing
git add .
git commit -m "v1.2.23: Decoupled SKILL.md routers"
git push origin main
```

---

## 5. File Updates During Publication

### 1. VERSION File
**Before**:
```
1.2.22
```

**After** (with `patch` increment):
```
1.2.23
```

### 2. CHANGELOG.md
**Before**:
```markdown
# Changelog

All notable changes...

## [1.2.22] - 2026-03-28
```

**After**:
```markdown
# Changelog

All notable changes...

## [1.2.23] - 2026-03-29
### Changed
- Decoupled SKILL.md routers

## [1.2.22] - 2026-03-28
```

### 3. README.md
**Before**:
```markdown
**Current Version**: **1.2.22** — *"Modular Synchronization"*
```

**After**:
```markdown
**Current Version**: **1.2.23** — *"Modular Synchronization"*
```

### 4. AGENTS.md
Also updated with new version reference and recent changelog entries.

---

## 6. Sanitization & Blacklist

### Files NEVER Synced (Blacklist)
```python
BLACKLIST = {
    # Local/Personal
    "knowledge_graph.json",

    # Maintenance Scripts

    # Local Workflows

    # Local Skills
    "repo-auditor"
}
```

### Content Sanitization
Replaces in all synced files:
- Local paths: `C:\Users\USER\...` → `<ROOT>`
- Project references: `LoggerApp`, `User` → generic names
- Hardcoded paths in `.md`, `.py`, `.json`

### Protected Files (Never Deleted)
```python
PROTECTED_FILES = {
    "README.md",
    "CHANGELOG.md",
    "VERSION",
    "LICENSE",
    ".git", ".gitignore"
}
```

---

## 7. Example: Complete Flow

### Scenario


### Execution
```bash
# From _foundation/ root:

# 1. Update project indexing
@index-project
# Output: Updated catalog.json with 11 skills

# 2. Publish changes
# Output:
# - Sanitized 45 files
# - Updated portable brainvibing/.agents/skills/...
# - Version: 1.2.22 → 1.3.0
# - Updated CHANGELOG.md
# - Updated README.md version marker

# 3. Verify
python portable\ brainvibing/.agents/scripts/verify_agents.py
# Output: All 245 links verified ✓

# 4. Push
cd portable\ brainvibing
git add .

git push
```

### Result in portable brainvibing/
- `VERSION`: `1.3.0`
- `CHANGELOG.md`: New entry for 1.3.0 with commit message
- `README.md`: Shows "**Current Version**: **1.3.0**"


---

## 8. Troubleshooting

### Issue: Version didn't update

### Issue: CHANGELOG entry missing
**Check**: Is `CHANGELOG.md` in `portable brainvibing/` root? Script creates if missing.

### Issue: README version marker not updated
**Check**: Script looks for pattern `## 🏷️ Version` or `## Version`. Ensure marker exists in README.

### Issue: Sensitive files leaked to portable

---

## 9. Best Practices

1. **One feature per version**: Don't batch multiple unrelated changes
2. **Clear commit messages**: Use active voice ("Added", "Fixed", "Updated")
3. **Document breaking changes**: Major version bumps require explicit BREAKING CHANGE note
5. **Run verify-loop before publish**: Prevents broken links in distribution
6. **Sync weekly or per-milestone**: Keep portable brainvibing in sync with foundation

---

*Last updated: 2026-03-29 | Applies to .agents v1.2.22+*