# Score Gates

How shipwright skills enforce quality thresholds.

## Scoring

Every Opus reviewer starts at **10** and deducts per finding:

| Severity | Deduction | Cap |
|---|---|---|
| Critical | -3 | none |
| Major | -1 | none |
| Warning | -0.5 | -2 total |
| Suggestion | -0.1 | -0.5 total |

## The Code Review Gate: > 9 (not ≥ 9)

| Score | Verdict | What it means |
|---|---|---|
| 10.0 | Pass | truly clean |
| 9.5 – 9.9 | Pass | at most one Warning, or only Suggestions |
| 9.0 – 9.4 | **Fail** | a Major, two Warnings, or a Warning plus nits |
| < 9 | Fail | |

Why not ≥ 9? A 9.0 means a Major issue (-1) or two Warnings are still open. That is not "basically clean", it is
"has known issues".

## Why Suggestions cost 0.1

Suggestions used to cost nothing, which meant a 10/10 could still hide a pile of nits. At -0.1 each with a -0.5 cap:

- **Suggestions alone can never fail the gate.** Ten nits still leave 9.5.
- **A 10 means clean.** The score stops lying.
- **They tip a borderline diff.** One Warning (9.5) plus one nit is 9.4, a fail. The loop fixes both, which is cheap
  because the same reviewer re-checks them.

-0.05 was considered and rejected: it takes ten nits to move the score by half a point, so it adds false precision
without changing any outcome.

**Fix policy:** when the gate fails, the loop fixes **every** open finding of that lens, Suggestions included. When
the gate passes, the loop stops and fixes nothing more: the leftovers (at most one Warning, plus Suggestions) are
listed in the PR body for the human reviewer. `/ship`, `/review-full` and `/review-code-fix` all follow this rule.

## The UX Review Gate: 10/10

Any Critical, Major or Warning fails the UX gate, and so do Suggestions: the UX loop fixes all of them.

UX issues compound. One misaligned button is invisible. Two is noticeable. Three and the product feels sloppy.

## Binary Pass/Fail Gates

- **Doc review**: either docs are accurate or they are not
- **Audit lens**: its findings feed the A/R round-1 fix batch; its "gate" is simply that it reported

## Rounds

| Gate | Rounds | Reviewer |
|---|---|---|
| Code, UX | 1-3 | same Opus reviewer, continued via `SendMessage` |
| Code, UX | 4 | fresh Opus reviewer, one escalation round, then stop |
| Docs | 1-2 | same reviewer, then stop |

See [Reviewer Continuity](reviewer-continuity.md) for why the reviewer is kept across rounds.

## Configuring Thresholds

All thresholds are marked with `<!-- CONFIGURE -->` in the skill files.

| Project type | Code gate | UX gate |
|---|---|---|
| Production app | > 9 (default) | 10/10 (default) |
| Internal tool | > 8 | 9/10 |
| Prototype/MVP | > 7 | 8/10 |
| Open source library | > 9 | N/A (no UX) |
