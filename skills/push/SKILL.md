---
name: push
description: Smart commit + push + auto-create PR. Blocks push to main. When called from /ship (bundled mode), verifies the ship gates and only opens the PR.
model: sonnet
---

# /push

Safe push with guard rails. Commits, pushes, and opens a PR if one doesn't exist.

## Workflow

1. **Safety check**: refuse if on `main` branch
2. **Stage changes**: `git add` relevant files (never `-A` blindly)
3. **Commit**: conventional commit format, auto-detect type from diff
4. **Rebase**: `git pull --rebase origin main` to stay current
5. **Push**: `git push -u origin <branch>`
6. **PR**: if no open PR exists, create one with template

## Conventional Commits

```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, perf, test, chore
```

<!-- CONFIGURE: Adjust scopes to match your project (e.g., www, api, docs) -->

## Bundling behavior (called from /ship)

`/ship` Phase S has already committed, rebased and pushed. In bundled mode `/push`:

- skips steps 2-5 (no stage, commit, rebase or push)
- verifies the gates below, then only runs step 6 with the PR body `/ship` hands over
- if a PR already exists for the branch, updates its body instead (`gh pr edit --body-file`)

## Pre-flight Gates (bundled mode)

Before opening the PR, `/push` verifies:

| Gate | Requirement |
|------|-------------|
| Code review | Score ≥ 9.5 (Opus `code-reviewer`) |
| UX review | Score = 10/10 (if frontend changed) |
| Working tree | Clean (no uncommitted changes) |

<!-- CONFIGURE: Adjust gate thresholds or remove gates you don't need -->

## PR Template

Auto-generated PR body includes:
- Summary (1-3 bullet points from commits)
- Test plan checklist
- Round table from `/ship`: per round, which reviewer ran (continued or fresh), the score, and what was fixed
- Leftover Suggestions the gates allowed through, for the human reviewer
- Phases that came back clean (instead of empty commits)

## Safety Rules

- **Never pushes to main**: always feature branches
- **Never force pushes**: always regular push
- **Never skips hooks**: if pre-push hook fails, fix the issue
