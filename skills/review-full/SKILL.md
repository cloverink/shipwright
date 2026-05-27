---
name: review-full
description: Smart review dispatcher. Auto-detects scope from diff (frontend/backend/docs/both), runs the right fix loops until all gates pass. Used as Phase R entry point in /ship.
model: sonnet
---

# /review-full

Smart review dispatcher. Detects what changed, picks the right reviewers, runs fix loops until quality gates pass.

> **When to use:** Default entry point for any review work — don't know what to use? Use this.
> **Use a worker directly only if:** you want to skip auto-detection (e.g., review code on a frontend-only diff).
> **Called by:** `/ship` Phase R, or standalone for ad-hoc review.
> **Dispatches to:** [`/review-code-fix`](../review-code-fix/SKILL.md) · [`/review-ux-fix`](../review-ux-fix/SKILL.md) · [`/review-docs`](../review-docs/SKILL.md)

## Scope Detection

Reads the diff and categorizes changes:

<!-- CONFIGURE: Replace glob patterns with your project's paths -->
```
Frontend files: src/components/**, src/pages/**, *.tsx, *.css
Backend files:  src/api/**, src/services/**, *.service.ts, *.controller.ts
Docs only:      docs/**, *.md
```

| Detected scope | Runs |
|---------------|------|
| Frontend + Backend | `/review-code-fix` + `/review-ux-fix` |
| Frontend only | `/review-code-fix` + `/review-ux-fix` |
| Backend only | `/review-code-fix` (skip UX) |
| Docs only | `/review-docs` only (skip code + UX) |

## Gate Thresholds

| Review type | Gate |
|-------------|------|
| Code | Score > 9 (9.5+ passes) |
| UX | Score = 10/10 |
| Docs | Binary pass/fail |

<!-- CONFIGURE: Adjust thresholds to your quality bar -->

All detected gates must pass for `/review-full` to report success.

## Flags

```
/review-full              # Full pipeline based on auto-detected scope
/review-full --code-only  # Run code review only (skip UX, even on frontend changes)
/review-full --ux-only    # Run UX review only (skip code review)
```
