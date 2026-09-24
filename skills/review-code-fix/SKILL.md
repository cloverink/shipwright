---
name: review-code-fix
description: Code review → fix → re-review loop until score > 9. One Opus reviewer is kept across rounds 1-3 (continued via SendMessage, no cold start), a fresh Opus reviewer runs round 4 as escalation, then stop. Use for /review-code-fix, or when asked to review code and auto-fix the findings.
model: sonnet
---

# /review-code-fix

Review → fix → re-review until the code passes **> 9/10**.

> **When to use:** code-only review when you want to skip scope detection (backend-only PR, library code).
> **Use [`/review-full`](../review-full/SKILL.md) instead if:** the diff touches frontend. It runs UX review alongside.
> **Called by:** `/review-full`. `/ship` does not call it, but uses §Review focus as its `code` lens checklist.

## Execution: runs in the MAIN session

This session owns **one** read-only [`code-reviewer`](../../agents/code-reviewer.md) agent (Opus) for the whole gate
and applies the fixes itself. The reviewer never fixes. Do not wrap the loop in a subagent.

Why one reviewer: a fresh reviewer every round cold-starts, forgets what it flagged, and samples new nits, so the
score oscillates. The same reviewer converges on one bar and re-checks faster. See
[Reviewer Continuity](../../patterns/reviewer-continuity.md).

## Algorithm

```
MAX_ROUNDS = 4                       // 1-3 same reviewer, 4 = fresh escalation   <!-- CONFIGURE -->
round = 1
reviewer = spawn code-reviewer, name "reviewer-code", lens "code"

loop:
  report = round == 1 ? reviewer's findings file
         : round <= 3 ? SendMessage("reviewer-code", RE_REVIEW_PROMPT)
         : round == 4 ? (shut down reviewer; spawn FRESH code-reviewer with round-3 table + fix SHA)
  score = X from "| **Overall** | **X/10** |" in the findings file

  if score > 9 AND reviewer read the current tree:
      shut down reviewer → report → stop
  if round == MAX_ROUNDS:
      shut down reviewer → report remaining findings → stop (FAIL)

  show round table to the user           // every round, before fixing
  fix ALL open findings (Critical, Major, Warning, Suggestion)
  lint + typecheck
  commit → record SHA
  round += 1
```

## Step 1: Spawn the reviewer

Compute scope once, in **one** Bash call, and pass the echoed values as literals (shell variables do not survive
between Bash calls). The reviewer must not re-derive scope.

```bash
BASE=$(git merge-base origin/main HEAD) || { echo "cannot resolve origin/main: git fetch first"; exit 1; }
CHANGED=$(git diff --name-only "$BASE"; git ls-files --others --exclude-standard)
RUN_DIR="${TMPDIR:-/tmp}/shipwright/$(git branch --show-current | tr / -)-$(date +%s)"
mkdir -p "$RUN_DIR" && printf 'STATUS: RUNNING\n' > "$RUN_DIR/code.md"
printf 'BASE=%s\nRUN_DIR=%s\nCHANGED:\n%s\n' "$BASE" "$RUN_DIR" "$CHANGED"
```

`SKILLS_DIR` is the parent of this skill's base directory (printed when the skill loads). The reviewer has no Skill
tool and, on a plugin install, the skills are not in the project, so pass the checklist as an absolute path.

```
Agent({
  subagent_type: "code-reviewer",          // "shipwright:code-reviewer" when installed as a plugin
  name: "reviewer-code",
  prompt: "Lens: code. Checklist: <SKILLS_DIR>/review-code-fix/SKILL.md §Review focus.
           Changed files (read each END-TO-END): <CHANGED>. Diff base: <BASE>.
           Findings file: <RUN_DIR>/code.md: append, flip line 1 to STATUS: DONE, reply with path + verdict only."
})
```

## Step 2: Re-review prompt (rounds 2-3)

Paste the real post-fix `git diff <BASE>..HEAD --stat`:

> Findings 1-N were addressed in commit `<sha>`; post-fix stat: `<stat>`. Your context still holds the PRE-fix files.
> Re-Read EVERY changed file end-to-end now. For each finding you mark resolved, QUOTE the post-fix line(s). List every
> file you re-read with its line count. Name at least one thing you checked that was NOT a prior finding. Re-score
> from scratch. Append to `<findings file>` as `round <N>`.

No quoted lines, no re-read list, or no regression-hunt note → **not a pass**. Ask once for a redo, else spawn fresh.
Reviewer unreachable → spawn fresh with the previous table + SHA, and mark the round "ran fresh".

## Score gate

| Score | Result |
|---|---|
| 10 | Pass, clean |
| 9.5 – 9.9 | Pass. Stop fixing; leftovers (at most one Warning, plus Suggestions) go to the PR body |
| 9.0 – 9.4 | **Fail** |
| < 9 | Fail |

<!-- CONFIGURE: threshold -->

| Severity | Deduction |
|---|---|
| Critical | -3 (security, data loss, broken build) |
| Major | -1 (bug, perf regression, missing test) |
| Warning | -0.5 each, max -2 (convention violation) |
| Suggestion | -0.1 each, max -0.5 (naming nit, readability) |

Rationale in [Score Gates](../../patterns/score-gates.md).

## Review focus

The `code` lens checklist. The reviewer loads this section.

1. **Correctness**: logic errors, off-by-one, unhandled promise, race conditions, wrong null handling
2. **Security**: secrets in code, missing input validation, injection, authz checks on every new endpoint
3. **Type safety**: no `any`, explicit return types on exports, narrowing instead of casts
4. **Performance**: N+1 queries, missing indexes, unbounded loops or payloads, bundle size
5. **Testing**: every changed code path has a test; edge cases (empty, error, boundary)
6. **Conventions**: naming, imports, file organization, error messages that help the user

<!-- CONFIGURE: add project-specific review items or point at your rules file -->

## Round table (show every round)

```markdown
## Round 2 · 8.5/10 · fixing 3

| # | Severity | File:Line | Issue | Fix plan |
|---|---|---|---|---|
| 1 | Major | src/api/users.ts:42 | ... | ... |
```

## Final report

```markdown
## Code Review Fix Report

| Round | Reviewer | Score | Fixed |
|---|---|---|---|
| 1 | reviewer-code | 7.5 | 1 major, 3 warnings |
| 2 | reviewer-code (continued) | 9.5 | 1 warning |

Result: ✅ passes > 9 · or · ❌ still failing after round 4, remaining findings below
```

## Commits

Every round commits, standalone or under `/review-full`: `fix(<scope>): review fixes (round N)`. The re-review prompt
points the same reviewer at that SHA, so a round without a commit cannot be re-reviewed. (`/ship` does not call this
skill; it runs its own loop and only borrows §Review focus as the `code` lens checklist.)

## Guidelines

- **Never push.** Run `/push` or `/ship` afterwards.
- **Never auto-fix DB migrations.** Flag them: "Schema change required, fix manually".
- **Same finding two rounds running** → mark it "requires manual fix" instead of looping on it.
