---
name: review-code-fix
description: Automated code review → fix → re-review loop. Runs until score >9 or max 3 rounds. Fixes Critical/Major/Warnings only — Suggestions are deferred.
model: opus
---

# /review-code-fix

Iterative review-fix loop that keeps going until your code passes the quality bar.

> **When to use:** Code-only review when you want to skip auto-scope-detection (backend-only PR, library code).
> **Use [`/review-full`](../review-full/SKILL.md) instead if:** your diff has frontend changes — it'll dispatch to UX review too.
> **Called by:** [`/review-full`](../review-full/SKILL.md) (auto-dispatched on code diffs — `/ship` Phase R reaches this transitively).

## How it works

```
Round 1: Review → list issues → fix Critical/Major/Warning → re-review
Round 2: Review again → fix remaining → re-review
Round 3: Final attempt → fix → final review
         If still failing → report to user with remaining issues
```

## Score Gate

The pass threshold is **strictly greater than 9**:

| Score | Result |
|-------|--------|
| 10 | Pass |
| 9.5 | Pass |
| 9.0 | **Fail** |
| 8.5 | Fail |

A 9.0 means at least one Major issue or two Warnings remain. That's not ship-ready.

<!-- CONFIGURE: Adjust the threshold to match your quality bar -->

## Severity Levels

| Severity | Score impact | Auto-fixed? |
|----------|-------------|-------------|
| Critical (-3) | Security, data loss, broken build | Yes |
| Major (-1) | Bug, perf regression, missing tests | Yes |
| Warning (-0.5, max -2) | Convention violations | Yes |
| Suggestion (0) | Style preference, naming nits | **No** |

## Fix Strategy

Fixes are applied by scope to avoid conflicts:
1. Group issues by file/directory
2. Fix each group
3. Run lint + typecheck after each batch
4. Re-review only after all fixes pass

<!-- CONFIGURE: Replace with your lint/typecheck commands -->

## Review Focus

1. **Type safety** — no `any`, proper null handling, explicit returns
2. **Security** — no secrets, input validation, injection prevention
3. **Performance** — N+1 queries, missing indexes, bundle size
4. **Testing** — coverage on changed code paths
5. **Conventions** — naming, imports, file organization

<!-- CONFIGURE: Add project-specific review items -->

## Output Format

```
Summary: 1-3 sentences
Issues:
  - [Critical] [file:line] description
  - [Major] [file:line] description
  - [Warning] [file:line] description
  - [Suggestion] [file:line] description (not auto-fixed)
Score: X/10
```
