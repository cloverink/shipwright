---
name: ship
description: Full pipeline — audit, review+fix, docs, push PR. One command to go from "done coding" to "PR ready for review." Does NOT deploy — your CI/CD handles that after merge.
model: opus
---

# /ship

One-command pipeline that takes your finished work through quality gates and opens a PR.

## Pipeline

```
Phase A (Audit)   → find issues → auto-fix Critical/Major → verify fixes
Phase R (Review)  → code review + UX review → fix until gates pass
Phase D (Docs)    → sync documentation → verify accuracy
Phase S (Ship)    → push branch + open PR with full description
```

## Execution Strategy

1. **Pre-flight check** — verify there are actual changes to ship (staged, unstaged, or commits ahead of main)
2. **Spawn a subagent** for the heavy lifting (keeps main context clean for long pipelines)
3. **Run phases A → R → D → S sequentially** — each phase gates the next
4. **Report back** with PR URL when done

## Pre-flight Gates

Before running, verify:
- Not on `main` branch
- Has changes to ship (diff or commits ahead of main)
- Lint + typecheck pass

## Phase Gates

| Phase | Gate | Fails when |
|-------|------|-----------|
| A (Audit) | Auto-fix succeeds | Critical issues can't be auto-fixed |
| R (Review) | Code >9, UX 10/10 | Score below threshold after 3 fix rounds |
| D (Docs) | No stale references | Dead links or missing doc updates |
| S (Ship) | Clean working tree | Uncommitted changes after phases A-D |

<!-- CONFIGURE: Adjust score thresholds to match your project's quality bar -->

## Commit Strategy

Each phase gets its own commit:
```
Phase A: refactor(<scope>): audit fixes — <summary>
Phase R: fix(<scope>): review fixes — <summary>
Phase D: docs(<scope>): sync documentation
Phase S: (no commit — push + open PR)
```

<!-- CONFIGURE: Adjust commit format to match your project's conventions -->

## What it does NOT do

- **Does not deploy** — it opens a PR. Your CI/CD deploys after merge.
- **Does not merge** — the PR is opened for human review. Use `/merge-pr` after approval.
- **Does not auto-approve** — even though automated review passes, a human should still look at the PR.

## Dependencies

This skill orchestrates other skills in the pipeline:
- Phase A: `/audit-full`
- Phase R: `/review-full` (dispatches to `/review-code-fix` + `/review-ux-fix` based on diff scope)
- Phase D: `/update-docs` + `/review-docs`
- Phase S: `/push`

Phases are modular — remove or replace any phase that doesn't apply to your project.
