---
activation: model_decision
description: Standardized Git workflow, commit messages, and branching strategy.

version: 2.4.0
last_updated: 2026-05-20
---

# Git Workflow & Conventional Commits

## 1. Commit Message Format
`<type>(<scope>): <description>`

## 2. Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semi-colons, etc.
- `refactor`: Refactoring production code
- `test`: Adding missing tests, refactoring tests
- `chore`: Updating build tasks, package manager configs, etc.

## 3. Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes

## 4. Worktree Isolation (Parallel Development)
- **Concept**: For parallel sub-tasks or large feature refactors, use `git worktree add ../feature-branch feature-branch` to create a physically isolated workspace.
- **Benefit**: This prevents file locking issues and allows the AI to work on different parts of the project simultaneously without cross-contamination.
- **Cleanup**: Always use `git worktree remove` after the task is merged to maintain disk hygiene.

## 5. Rules
- Always pull before pushing.
- Rebase `develop` into your feature branch frequently.
- Keep commits atomic and descriptive.