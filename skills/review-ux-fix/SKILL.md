---
name: review-ux-fix
description: Automated UX review → fix → re-review loop. Target is perfection (10/10). Fixes ALL severities including Suggestions — because UX polish compounds.
model: opus
---

# /review-ux-fix

Iterative UX review-fix loop targeting perfection. Unlike `/review-code-fix`, this fixes **every** issue including Suggestions.

> **When to use:** UX-only polish (CSS, spacing, micro-interactions) with no code logic changes.
> **Use [`/review-full`](../review-full/SKILL.md) instead if:** your diff has logic/API changes too — it'll run code review alongside.
> **Called by:** [`/review-full`](../review-full/SKILL.md) (auto-dispatched on frontend diffs — `/ship` Phase R reaches this transitively).

## How it works

```
Round 1: UX review → list issues → fix ALL severities → re-review
Round 2: Review again → fix remaining → re-review
Round 3: Final attempt → fix → final review
         If still failing → report to user
```

## Score Gate

Target is **exactly 10/10**. Any issue at any severity fails the gate.

Why perfection? UX issues compound. A slightly off button, a missing loading state, and a wonky mobile layout individually seem minor — together they make the product feel unpolished.

## Why fix Suggestions too?

Code Suggestions are style preferences — reasonable people disagree. UX Suggestions are polish items — spacing, alignment, micro-interactions — that users *feel*. Fix them all.

## Review Categories

1. **Design system compliance** — tokens, typography, spacing
2. **Visual polish** — alignment, consistency, whitespace rhythm
3. **Responsive behavior** — mobile, tablet, desktop
4. **Loading states** — skeleton/shimmer for async content
5. **Error states** — user-friendly messages, retry options
6. **Empty states** — helpful messaging when no data exists

<!-- CONFIGURE: Add your design system rules and component library -->

## Relationship to /review-code-fix

Complementary, not overlapping:
- `/review-code-fix` — correctness (types, security, performance, tests)
- `/review-ux-fix` — experience (design, responsiveness, states, polish)
