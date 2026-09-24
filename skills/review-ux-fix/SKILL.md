---
name: review-ux-fix
description: UX review → fix → re-review loop targeting 10/10. Fixes every severity, Suggestions included. One Opus reviewer is kept across rounds 1-3 (continued via SendMessage), a fresh Opus reviewer runs round 4 as escalation, then stop. Use for /review-ux-fix, or when asked to polish and auto-fix UX issues.
model: sonnet
---

# /review-ux-fix

UX review → fix **everything** → re-review until **10/10**.

> **When to use:** UX-only polish (CSS, spacing, states, micro-interactions) with no logic changes.
> **Use [`/review-full`](../review-full/SKILL.md) instead if:** the diff has logic or API changes too.
> **Called by:** `/review-full`. `/ship` does not call it, but uses §Review categories as its `ux` lens checklist.

## Execution: runs in the MAIN session

Same contract as [`/review-code-fix`](../review-code-fix/SKILL.md): this session owns **one** read-only
[`code-reviewer`](../../agents/code-reviewer.md) (Opus), named `reviewer-ux`, for the whole gate, and applies the
fixes itself. UX findings are the most subjective in the pipeline, which is exactly where a fresh reviewer every round
makes the score oscillate. See [Reviewer Continuity](../../patterns/reviewer-continuity.md).

## Step 0: Dev server + screenshot precheck (before round 1)

The reviewer looks at the running app by screenshotting it with Playwright and reading the PNGs (see the agent's
§Seeing the app). Without screenshots it caps the UX score at 8, so a 10/10 gate would fail by construction and burn
every round. Check both before spawning:

```bash
curl -sf -o /dev/null http://localhost:3000 && echo up || echo down            # <!-- CONFIGURE: dev URL(s) -->
npx --yes playwright screenshot http://localhost:3000 "${TMPDIR:-/tmp}/ux-precheck.png" && echo screenshots-ok
```

Server down → start it (`<!-- CONFIGURE: npm run dev -->`) and re-check. Screenshots fail → `npx playwright install
chromium` once. Still failing → **STOP**: "UX gate blocked: cannot see the app". Never spawn a reviewer whose ceiling
is below the gate. Pass the dev URL(s) in the spawn prompt, with the checklist as an absolute path:
`<SKILLS_DIR>/review-ux-fix/SKILL.md §Review categories`.

## Algorithm

```
MAX_ROUNDS = 4                       // 1-3 same reviewer, 4 = fresh escalation   <!-- CONFIGURE -->
round = 1
reviewer = spawn code-reviewer, name "reviewer-ux", lens "ux"

loop:
  report = round == 1 ? reviewer's findings file
         : round <= 3 ? SendMessage("reviewer-ux", RE_REVIEW_PROMPT)   // re-read every changed file; re-screenshot affected pages
         : round == 4 ? (release reviewer; spawn FRESH reviewer with round-3 table + fix SHA)

  if score == 10 AND no open finding of any severity AND reviewer read the current tree:
      release reviewer (stop messaging it) → report → stop
  if round == MAX_ROUNDS:
      release reviewer (stop messaging it) → report remaining findings → stop (FAIL)

  show round table → fix ALL findings (every severity) → lint → commit → round += 1
```

The re-review prompt and its evidence rule (quoted post-fix lines, re-read list, regression-hunt note) are identical
to `/review-code-fix` §Step 2.

## Score gate

Target is **exactly 10/10** with zero open findings. A Suggestion costs only -0.1, so a 9.9 still fails.

Why perfection? UX issues compound. A slightly off button, a missing loading state and a wonky mobile layout each
seem minor. Together they make the product feel unpolished. UX Suggestions are polish users *feel*, so they get fixed
too (unlike code Suggestions, which only get fixed when the code gate fails).

<!-- CONFIGURE: 9/10 for internal tools -->

## Review categories

The `ux` lens checklist. The reviewer loads this section.

1. **Design system**: tokens only (no raw hex, no magic px), typography scale, spacing scale
2. **Visual polish**: alignment, consistency with sibling screens, whitespace rhythm
3. **Responsive**: mobile, tablet, desktop; no horizontal scroll; touch targets ≥ 44px
4. **Loading states**: skeleton or shimmer for async content, no layout shift
5. **Error states**: user-friendly message, a way to retry, no raw error text
6. **Empty states**: helpful copy and a next action when there is no data
7. **Accessibility**: contrast, focus order, keyboard reachability, labels on inputs and icon buttons

<!-- CONFIGURE: add your design system rules and component library -->

## Commits

Every round commits (`fix(<scope>): UX fixes (round N)`), standalone or under `/review-full`, so the same reviewer
can be pointed at the SHA. `/ship` does not call this skill; it runs its own loop.

## Relationship to /review-code-fix

- `/review-code-fix`: correctness (types, security, performance, tests)
- `/review-ux-fix`: experience (design, responsiveness, states, polish)
