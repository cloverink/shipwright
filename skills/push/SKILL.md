---
name: push
description: Smart commit + push + auto-create PR. Blocks push to main. Runs pre-flight gate checks before pushing.
model: sonnet
---

# /push

Safe push with guard rails. Commits, pushes, and opens a PR if one doesn't exist.

## Workflow

1. **Safety check** — refuse if on `main` branch
2. **Stage changes** — `git add` relevant files (never `-A` blindly)
3. **Commit** — conventional commit format, auto-detect type from diff
4. **Rebase** — `git pull --rebase origin main` to stay current
5. **Push** — `git push -u origin <branch>`
6. **PR** — if no open PR exists, create one with template

## Conventional Commits

```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, perf, test, chore
```

<!-- CONFIGURE: Adjust scopes to match your project (e.g., www, api, docs) -->

## Pre-flight Gates (when called from /ship)

When `/push` runs as Phase S of `/ship`, it verifies gates before pushing:

| Gate | Requirement |
|------|-------------|
| Code review | Score > 9 |
| UX review | Score = 10/10 (if frontend changed) |
| Working tree | Clean (no uncommitted changes) |

<!-- CONFIGURE: Adjust gate thresholds or remove gates you don't need -->

## PR Template

Auto-generated PR body includes:
- Summary (1-3 bullet points from commits)
- Test plan checklist
- Phase-by-phase changelog (when called from `/ship`)

## Safety Rules

- **Never pushes to main** — always feature branches
- **Never force pushes** — always regular push
- **Never skips hooks** — if pre-push hook fails, fix the issue
