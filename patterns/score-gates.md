# Score Gates

How shipwright skills enforce quality thresholds.

## The Code Review Gate: >9 (not >=9)

The code review threshold is **strictly greater than 9**. This means:

| Score | Verdict |
|-------|---------|
| 10.0 | Pass |
| 9.5 | Pass |
| 9.0 | **Fail** |
| 8.0 | Fail |

Why not >=9? Because scoring works like this:

- Start at 10
- Critical: -3 each
- Major: -1 each
- Warning: -0.5 each (max -2 total)

A score of exactly 9.0 means there's still one Major issue (-1) or two Warnings (-0.5 each). That's not "basically clean" — it's "has known issues."

## The UX Review Gate: 10/10

UX review targets perfection. Any issue at any severity — including Suggestions — fails the gate.

Why stricter than code review?

UX issues compound. One misaligned button is invisible. Two is noticeable. Three and the product feels sloppy. Code can have style trade-offs where reasonable people disagree. UX polish either exists or it doesn't.

## Binary Pass/Fail Gates

Some reviews use binary pass/fail instead of numeric scores:

- **Doc review** — either docs are accurate or they're not
- **Audit review** — either the audit fixes are correct or they introduced regressions

Binary gates have a max of 2 fix rounds before escalating to the user. No infinite loops.

## Configuring Thresholds

All thresholds are marked with `<!-- CONFIGURE -->` in the skill files. Common adjustments:

| Project type | Code gate | UX gate |
|-------------|-----------|---------|
| Production app | >9 (default) | 10/10 (default) |
| Internal tool | >8 | 9/10 |
| Prototype/MVP | >7 | 8/10 |
| Open source library | >9 | N/A (no UX) |

Choose thresholds that match your project's quality needs. The defaults are for production applications where quality matters.
