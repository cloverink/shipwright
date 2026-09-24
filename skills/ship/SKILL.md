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

Run this as **one** Bash call. Shell variables do not survive between Bash calls, so echo the resolved values and
paste them as **literals** into every later command and spawn prompt. Never recompute `RUN_DIR` (its timestamp would
change).

```bash
BRANCH=$(git branch --show-current)
git fetch origin main --quiet
BASE=$(git merge-base origin/main HEAD) || { echo "cannot resolve origin/main"; exit 1; }   # never guess a base
CHANGED=$(git diff --name-only "$BASE"; git ls-files --others --exclude-standard)
FRONTEND_TOUCHED=$(printf '%s\n' "$CHANGED" | grep -qE '^(src/components|src/pages)/|\.(tsx|css)$' && echo yes || echo no)
RUN_DIR="${TMPDIR:-/tmp}/shipwright/$(printf '%s' "$BRANCH" | tr / -)-$(date +%s)"
mkdir -p "$RUN_DIR"
for lens in audit code; do printf 'STATUS: RUNNING\n' > "$RUN_DIR/$lens.md"; done
[ "$FRONTEND_TOUCHED" = yes ] && printf 'STATUS: RUNNING\n' > "$RUN_DIR/ux.md"
printf 'BRANCH=%s\nBASE=%s\nFRONTEND_TOUCHED=%s\nRUN_DIR=%s\nCHANGED:\n%s\n' "$BRANCH" "$BASE" "$FRONTEND_TOUCHED" "$RUN_DIR" "$CHANGED"
```

<!-- CONFIGURE: frontend path globs, main branch name -->

- On `main` → **block**: "Create a feature branch first."
- Nothing uncommitted and nothing ahead of `BASE` → **block**: "Nothing to ship."
- Lint + typecheck must pass (`<!-- CONFIGURE: npm run lint && npm run typecheck -->`). Fix before spawning anyone.
- Commit leftover work: `git add <relevant files>` (never `-A` blindly) → `<type>(<scope>): <description>`.
- **Checklist paths.** This skill's base directory is printed when it loads ("Base directory for this skill: …").
  Its parent is `SKILLS_DIR`. The reviewer agent has no Skill tool and, on a plugin install, the skills live in the
  plugin cache, so always pass it an **absolute** checklist path such as `<SKILLS_DIR>/review-code-fix/SKILL.md`.

## Step 1: A/R batch (round 1, parallel)

Spawn **every lens in ONE tool-call block**:

| Name | Agent | Lens | Checklist (absolute path + section) | When |
|---|---|---|---|---|
| `auditor` | `code-reviewer` | `audit` | `<SKILLS_DIR>/audit-full/SKILL.md` §Audit checks | always |
| `reviewer-code` | `code-reviewer` | `code` | `<SKILLS_DIR>/review-code-fix/SKILL.md` §Review focus | always |
| `reviewer-ux` | `code-reviewer` | `ux` | `<SKILLS_DIR>/review-ux-fix/SKILL.md` §Review categories | `FRONTEND_TOUCHED=yes` |

Each prompt carries: the lens, the checklist path, `CHANGED`, `BASE`, `FRONTEND_TOUCHED`, the **absolute**
findings-file path (`<RUN_DIR>/<lens>.md`), and "append your report to that file, flip line 1 to `STATUS: DONE`,
and reply with only the path plus a one-line verdict". The UX prompt also carries the dev URL. On a plugin install
the agent type is `shipwright:code-reviewer` (see [Reviewer Continuity](../../patterns/reviewer-continuity.md) §Mechanics).

If `FRONTEND_TOUCHED=yes`, run `/review-ux-fix` Step 0 (dev server + screenshot precheck) **before** the batch.

Wait for all lenses. Read each findings file (not the reply). A lens whose file is still `RUNNING` or missing
**was never reviewed**: nudge it once, then respawn it. Never report a green gate over a skipped lens.

## Step 2: Fix round 1 + commit

1. Union all findings, group by file, **one writer per file** (this session, or one Sonnet worker per file group).
2. What to fix, per lens:
   - **code / ux lens failed its gate** → fix every open finding of that lens, Suggestions included.
   - **code / ux lens passed** → fix nothing of that lens; its leftovers go to the PR body.
   - **audit lens** (no gate) → fix P0-P2; P3 goes to the PR body.
3. Run lint + typecheck. Fix new warnings.
4. Show the user a round table before moving on:

   ```markdown
   ## A/R round 1 · code 8.5/10 · UX 9/10 · audit 4 findings · fixing 9
   | # | Lens | Severity | File:Line | Issue | Fix |
   ```

5. Commit: `refactor(<scope>): audit + review fixes (A/R round 1)`. Record the SHA.
6. The `auditor` is done after round 1: stop messaging it.

Skip-when-clean: all lenses clean and gates pass → no commit, note "A/R came back clean".

## Step 3: Review rounds 2-4 (the gate loop)

Round 1's fixes (including audit fixes) landed **after** the reviewers read the tree, so any round-1 commit means
round 2 runs, even if round 1's scores already passed.

```
MAX_ROUNDS = 4                                   // 3 continued + 1 fresh   <!-- CONFIGURE -->
round = 2                                        // only if Step 2 committed anything; else the gate already passed
loop:
  if round <= 3:  report = SendMessage(reviewer-code / reviewer-ux, RE_REVIEW_PROMPT)      // same agents, parallel
  else:           report = spawn FRESH code-reviewer(s) with the round-3 table + fix SHA  // escalation
  gate = code >= 9.5 AND (ux == 10 with zero open findings OR FRONTEND_TOUCHED=no)
  if gate:                     stop messaging the reviewers → break → Phase D
  if round == MAX_ROUNDS:      STOP → report remaining findings → do NOT run D or S
  fix every open finding of each failing lens → lint → commit "fix(<scope>): review fixes (round {round})"
  round += 1
```

A lens that already passed is not re-run unless the fixes touched its files. A pass carries its leftovers (at most
one Warning, plus Suggestions) to the PR body; see [Score Gates](../../patterns/score-gates.md).

`RE_REVIEW_PROMPT` (paste the real `git diff <BASE>..HEAD --stat`):

> Findings 1-N were addressed in commit `<sha>`; post-fix stat: `<stat>`. Your context still holds the PRE-fix files.
> Re-Read EVERY changed file end-to-end now. For each finding you mark resolved, QUOTE the post-fix line(s). List every
> file you re-read with its line count. Name at least one thing you checked that was NOT a prior finding. Re-score
> from scratch. Append to `<findings file>` as `round <N>`, same format.

A continued report with no quoted lines, no re-read list, or no regression-hunt note is **not a pass**: ask once for a
redo, else spawn fresh.

## Step 4: Phase D (docs)

1. `/update-docs` in bundled mode against everything that shipped (original work + fix rounds). It stages, no commit.
2. `/review-docs` gate (binary). Nothing staged and `/update-docs` reported clean → pass without spawning.
3. Commit: `docs(<scope>): sync documentation`. Skip-when-clean.

## Step 5: Phase S (ship, serial)

1. Working tree clean.
2. `git pull --rebase origin main` → `git push -u origin <branch>`. Never force-push.
3. Open the PR with `/push` in **bundled mode** (it skips commit, rebase and push, and only creates the PR). The body
   carries: summary, the round table, leftovers the gates let through, phases that came back clean, test plan.
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
