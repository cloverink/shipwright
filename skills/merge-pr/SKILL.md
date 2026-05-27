---
name: merge-pr
description: Merge current PR after CI passes. Waits for all checks, squash merges, deletes branch, switches to main.
model: haiku
---

# /merge-pr

Wait for CI, then merge cleanly.

## Workflow

1. **Get current PR** — `gh pr view` on current branch
2. **Wait for CI** — poll every 15s until all checks pass
3. **Squash merge** — `gh pr merge --squash --delete-branch`
4. **Switch to main** — `git checkout main && git pull --rebase`
5. **Report** — confirm merge succeeded

## Rules

<!-- CONFIGURE: Change merge strategy (--squash, --merge, --rebase) and branch cleanup to match your workflow -->
- **Never merges with failing CI** — if checks fail, report which ones and stop
- **Always squash merge** — keeps main history clean (change to `--merge` or `--rebase` if preferred)
- **Always deletes branch** — no stale branches (remove `--delete-branch` if you want to keep them)
- **Never merges to non-default branch** — PR must target `main` (or your default branch)

## Usage

```
/merge-pr          # Merge current branch's PR
```
