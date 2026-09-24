---
name: ship
description: One-command pipeline from "done coding" to "PR ready for review". Runs audit + review as one parallel batch of Opus reviewers, keeps the same reviewers across fix rounds, syncs docs, then pushes and opens a PR. Use when the user says /ship, "ship it", or asks to run the full A→R→D→S pipeline. Does NOT deploy or merge.
model: sonnet
---

# /ship

Takes finished work through quality gates and opens a PR: **A+R → D → S**.

- **Opus judges, Sonnet builds.** Every review and audit lens is the read-only `code-reviewer` agent (Opus). This
  session (Sonnet) orchestrates, applies fixes and commits.
- **One batch, not two phases.** Audit and review round 1 run in parallel over the same diff.
- **Same reviewer re-checks the fixes.** Rounds 2-3 continue the round-1 reviewers via `SendMessage` (no cold start),
  round 4 is a fresh escalation, then stop. See [Reviewer Continuity](../../patterns/reviewer-continuity.md).

## Execution: runs in the MAIN session

Do **not** wrap the pipeline in a single subagent. That shape is serial, reviews its own fixes, and cannot keep a
reviewer alive across rounds. This session spawns the reviewers, continues them, fixes, and commits.

## Step 0: Pre-flight

```bash
BRANCH=$(git branch --show-current)
git fetch origin main --quiet
BASE=$(git merge-base origin/main HEAD) || { echo "cannot resolve origin/main"; exit 1; }   # never guess a base
CHANGED=$(git diff --name-only "$BASE"; git ls-files --others --exclude-standard)
FE_CHANGED=$(printf '%s\n' "$CHANGED" | grep -E '^(src/components|src/pages)/|\.(tsx|css)$' | head -1)
RUN_DIR="${TMPDIR:-/tmp}/shipwright/$(printf '%s' "$BRANCH" | tr / -)-$(date +%s)"
mkdir -p "$RUN_DIR"
```

<!-- CONFIGURE: frontend path globs, main branch name -->

- On `main` → **block**: "Create a feature branch first."
- Nothing uncommitted and nothing ahead of `BASE` → **block**: "Nothing to ship."
- Lint + typecheck must pass (`<!-- CONFIGURE: npm run lint && npm run typecheck -->`). Fix before spawning anyone.
- Commit leftover work: `git add <relevant files>` (never `-A` blindly) → `<type>(<scope>): <description>`.
- Carry `BASE`, `CHANGED`, `frontendTouched`, `RUN_DIR` into every step below.

## Step 1: A/R batch (round 1, parallel)

Create one findings file per lens, then spawn **every lens in ONE tool-call block**:

```bash
for lens in audit code ux; do printf 'STATUS: RUNNING\n' > "$RUN_DIR/$lens.md"; done   # skip ux if !frontendTouched
```

| Name | Agent | Lens | When |
|---|---|---|---|
| `auditor` | `code-reviewer` | `audit` (checklist: `/audit-full` §Audit checks) | always |
| `reviewer-code` | `code-reviewer` | `code` (checklist: `/review-code-fix` §Review focus) | always |
| `reviewer-ux` | `code-reviewer` | `ux` (checklist: `/review-ux-fix` §Review categories) | frontend touched |

Each prompt carries: the lens, `CHANGED`, `BASE`, `frontendTouched`, the **absolute** findings-file path, and
"append your report to that file, flip line 1 to `STATUS: DONE`, and reply with only the path plus a one-line
verdict". Plugin install exposes the agent as `shipwright:code-reviewer`.

If frontend is touched, run the dev-server precheck from `/review-ux-fix` Step 0 **before** the batch.

Wait for all lenses. Read each findings file (not the reply). A lens whose file is still `RUNNING` or missing
**was never reviewed**: nudge it once, then respawn it. Never report a green gate over a skipped lens.

## Step 2: Fix round 1 + commit

1. Union all findings, group by file, **one writer per file** (this session, or one Sonnet worker per file group).
2. Fix every Critical, Major, Warning. Suggestions: fixed when that lens's gate failed, otherwise carried to the PR body.
3. Run lint + typecheck. Fix new warnings.
4. Show the user a round table before moving on:

   ```markdown
   ## A/R round 1 · code 8.5/10 · UX 9/10 · audit 4 findings · fixing 9
   | # | Lens | Severity | File:Line | Issue | Fix |
   ```

5. Commit: `refactor(<scope>): audit + review fixes (A/R round 1)`. Record the SHA.

Skip-when-clean: all lenses clean and gates pass → no commit, note "A/R came back clean".

## Step 3: Review rounds 2-4 (the gate loop)

```
round = 2
loop:
  gate passes when:  code > 9  AND  (ux == 10 OR !frontendTouched)
                     AND the reviewers read the tree that ships (no edits after their last read)
  if gate passes → shut down reviewers → break
  if round <= 3:
      SendMessage(reviewer-code / reviewer-ux, RE_REVIEW_PROMPT)   // same agents, in parallel
  elif round == 4:
      shut down both; spawn FRESH code-reviewer(s) with the round-3 findings + fix SHA   // escalation
  else:
      STOP → report remaining findings → do NOT continue to D or S
  fix → lint → commit "fix(<scope>): review fixes (round {round})" → round += 1
```

Round 1's audit fixes landed **after** the review lenses read the tree, so a round-1 pass with any audit edits
still needs round 2 as a verification round.

`RE_REVIEW_PROMPT` (paste the real `git diff $BASE..HEAD --stat`):

> Findings 1-N were addressed in commit `<sha>`; post-fix stat: `<stat>`. Your context still holds the PRE-fix files.
> Re-Read EVERY changed file end-to-end now. For each finding you mark resolved, QUOTE the post-fix line(s). List every
> file you re-read with its line count. Name at least one thing you checked that was NOT a prior finding. Re-score
> from scratch. Append to `<findings file>` as `round <N>`, same format.

A continued report with no quoted lines, no re-read list, or no regression-hunt note is **not a pass**: ask once for a
redo, else spawn fresh.

<!-- CONFIGURE: MAX_ROUNDS (default 4 = three continued rounds + one escalation) -->

## Step 4: Phase D (docs)

1. `/update-docs` in bundled mode against everything that shipped (original work + fix rounds). It stages, no commit.
2. `/review-docs` gate (binary). Nothing staged and `/update-docs` reported clean → pass without spawning.
3. Commit: `docs(<scope>): sync documentation`. Skip-when-clean.

## Step 5: Phase S (ship, serial)

1. Working tree clean.
2. `git pull --rebase origin main` → `git push -u origin <branch>`. Never force-push.
3. `gh pr create` via `/push` in bundled mode. The body carries: summary, the round table, leftover Suggestions,
   phases that came back clean, test plan.
4. Report the PR URL.

## Final report

```
Ship pipeline done 🚀

A/R:  ✅ audit 4 fixed · code 8.5 → 9.5 · UX 9 → 10   (rounds: 2, reviewer continued)
D:    ✅ 3 docs updated
S:    ✅ PR #123 <url>
```

## Commit strategy

```
refactor(<scope>): audit + review fixes (A/R round 1)
fix(<scope>): review fixes (round 2)
fix(<scope>): review fixes (round 4, fresh reviewer)
docs(<scope>): sync documentation
```

<!-- CONFIGURE: commit format -->

## What it does NOT do

- **Does not deploy.** It opens a PR. Your CI/CD deploys after merge.
- **Does not merge.** A human reviews the PR, then runs `/merge-pr`.
- **Does not loop forever.** Round 4 is the last one.

## Dependencies

- Agent: [`code-reviewer`](../../agents/code-reviewer.md) (Opus, read-only)
- Checklists: `/audit-full` (audit lens), `/review-code-fix` (code lens), `/review-ux-fix` (UX lens)
- Phase D: `/update-docs` + `/review-docs`
- Phase S: `/push`
- Patterns: [A→R→D→S](../../patterns/ards-pipeline.md) · [Reviewer Continuity](../../patterns/reviewer-continuity.md) · [Score Gates](../../patterns/score-gates.md) · [Phase Bundling](../../patterns/phase-bundling.md)
