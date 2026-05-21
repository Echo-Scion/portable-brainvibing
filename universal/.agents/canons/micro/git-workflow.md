# Micro-Canon: Git Workflow (≤50 lines — Budget Model Cheat Sheet)

## COMMIT FORMAT (Conventional Commits — MANDATORY)
- SYNTAX: `<type>(<scope>): <subject>` — subject ≤72 chars, imperative mood
- Types: `feat` | `fix` | `refactor` | `perf` | `test` | `docs` | `chore` | `ci`
- DO: `feat(auth): add Google OAuth sign-in flow`
- DO: `fix(profile): prevent null crash when avatar_url is empty`
- DONT: `"fixed stuff"` / `"WIP"` / `"update"` — no context, useless in `git log`
- DONT: Mix feat + fix in one commit — split them

## BRANCH STRATEGY
- `main` — production only, never commit directly
- `develop` — integration branch
- `feat/<ticket-id>-short-description` — feature branches
- `fix/<ticket-id>-short-description` — bug fix branches
- DO: Branch from `develop`, PR back to `develop`
- DONT: Long-lived feature branches >1 week — rebase frequently

## PRE-COMMIT CHECKLIST (run before every `git commit`)
```bash
# 1. Secrets scan (see security-guardrails.md §1)
grep -rE "(sk-|SERVICE_KEY|BEGIN PRIVATE)" --include="*.dart" --include="*.ts" .

# 2. Lint check
dart analyze          # Flutter
npx tsc --noEmit      # TypeScript

# 3. Tests pass
flutter test          # Flutter
npm test              # Node
```
**If any step fails → DO NOT COMMIT. Fix first.**

## MERGE & REBASE
- DO: `git rebase develop` before opening PR — keep linear history
- DO: Squash WIP commits before PR: `git rebase -i HEAD~N`
- DONT: `git merge develop` into feature branch — creates merge commit noise
- DONT: Force-push to `main` or `develop` — coordinate first

## HOTFIX PROTOCOL
- Branch from `main`: `git checkout -b fix/critical-bug main`
- After fix: PR to `main` AND cherry-pick to `develop`
- Tag after merge: `git tag v1.0.1 -m "fix: critical-bug description"`

## DESTRUCTIVE GIT COMMANDS (REQUIRE EXPLICIT CONFIRMATION)
- `git reset --hard` → irreversible local changes loss
- `git push --force` → overwrites remote history
- `git branch -D` → deletes local branch permanently
Output `[DESTRUCTIVE GIT OP]: {command}` and wait for `[DO: YES]` before executing.
