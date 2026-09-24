---
name: review-full
description: Smart review entry point. Auto-detects scope from the diff (frontend / backend / docs), spawns the right Opus reviewers in parallel, and keeps the same reviewers across fix rounds until the gates pass. --read-only for a quick scored peek with no edits. Use when unsure which review to run.
model: sonnet
---

# /review-full

Detects what changed, spawns the right reviewers **in parallel**, and runs the fix loops until the gates pass.

> **When to use:** default entry point for any review. Not sure? Use this.
> **Use a worker directly only if:** you want to skip auto-detection.
> **Called by:** you, standalone. `/ship` runs the same lenses inside its A/R batch.
> **Dispatches to:** [`/review-code-fix`](../review-code-fix/SKILL.md) · [`/review-ux-fix`](../review-ux-fix/SKILL.md) · [`/review-docs`](../review-docs/SKILL.md)

> **Naming note:** `/review` and `/code-review` are Claude Code built-ins. This skill's trigger is `/review-full`.

## Modes

| Command | Mode | What happens |
|---|---|---|
| `/review-full` | Fix loop | code + UX loops (per detected scope), fixes applied |
| `/review-full --read-only` | Peek | spawn reviewers, report scores, change nothing |
| `/review-full --code-only` | Fix loop | code only, even on a frontend diff |
| `/review-full --ux-only` | Fix loop | UX only |

## Step 1: Detect scope

```bash
BASE=$(git merge-base origin/main HEAD) || { echo "cannot resolve origin/main, git fetch first"; exit 1; }
CHANGED=$(git diff --name-only "$BASE"; git ls-files --others --exclude-standard)
```

<!-- CONFIGURE: replace globs with your project's paths -->
```
Frontend: src/components/**, src/pages/**, *.tsx, *.css
Backend:  src/api/**, src/services/**, *.service.ts, *.controller.ts
Docs:     docs/**, *.md
```

| Detected | Runs |
|---|---|
| Frontend (with or without backend) | code + UX |
| Backend only | code |
| Docs only | `/review-docs` |
| Nothing | "no diff, nothing to review" |

## Step 2: Spawn reviewers in ONE tool-call block

Both reviewers read the same diff and neither writes, so they never wait for each other:

- `reviewer-code`: `code-reviewer` (Opus), lens `code`, checklist `<SKILLS_DIR>/review-code-fix/SKILL.md §Review focus`
- `reviewer-ux`: `code-reviewer` (Opus), lens `ux`, checklist `<SKILLS_DIR>/review-ux-fix/SKILL.md §Review categories`
  (frontend only; run the `/review-ux-fix` Step 0 precheck first)

`SKILLS_DIR` is the parent of this skill's base directory. Pass absolute paths: the agent has no Skill tool.

Each gets its own findings file (see [Reviewer Continuity](../../patterns/reviewer-continuity.md) §Mechanics).

## Step 3: Fix loop (skipped with --read-only)

This session runs both loops from `/review-code-fix` and `/review-ux-fix`:

1. Union the findings, group by file, one writer per file, fix, lint.
2. One commit per round covering both lenses, so the re-review can cite the SHA.
3. Continue **the same reviewers** with `SendMessage` for rounds 2-3, in parallel. Round 4 = fresh escalation.
   A lens that already passed is not re-run unless the fixes touched its files.

## Gates

| Review | Gate |
|---|---|
| Code | ≥ 9.5 (9.0-9.4 fails) |
| UX | = 10/10, zero open findings |
| Docs | binary pass/fail |

<!-- CONFIGURE: thresholds -->

All detected gates must pass.

## Report

```markdown
## Review Report

Scope: frontend + backend · Mode: fix

| Review | Rounds | Score | Bar | Status |
|---|---|---|---|---|
| Code | 2 (continued) | 9.5 | ≥ 9.5 | ✅ |
| UX | 3 (continued) | 10 | = 10 | ✅ |
```

## Guidelines

- Never run `/update-docs` here. Docs are Phase D.
- `--read-only` never commits, stages, or edits.
- Never push or merge.
