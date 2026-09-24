# Reviewer Continuity

One reviewer per gate, not one per round. The same Opus reviewer that found the issues is the one that checks
the fixes.

## The Problem

The naive fix loop spawns a **fresh** reviewer every round:

```
round 1: spawn reviewer A → 6 findings → fix
round 2: spawn reviewer B → 4 findings (3 new nits A never raised) → fix
round 3: spawn reviewer C → 5 findings (a different 3 new nits) → fix
...
```

Each new reviewer cold-starts (re-reads the rules and every changed file), has no memory of what was flagged,
and samples a **new set of nits**. The gate oscillates instead of converging. We saw a UX gate go
9 → 8 → 9 → 7 → 10 across five fresh reviewers on the same diff.

## The Solution

```
round 1   spawn reviewer (named, Opus)          → findings → fix → commit
round 2   SendMessage(same reviewer, re-review) → findings → fix → commit
round 3   SendMessage(same reviewer, re-review) → findings → fix → commit
round 4   spawn FRESH reviewer (escalation)     → one independent verdict
          still failing → STOP and report
```

- **Rounds 1-3: continuity.** The reviewer already holds the rules, the files and its own findings. A re-review is a
  diff check, not a cold start, so it is faster and it holds **one stable bar**.
- **Round 4: escalation.** If the same reviewer still fails the gate after three rounds, something is off (an
  unfixable finding, a reviewer that fixated). A fresh reviewer gets the round-3 findings table and the fix SHA and
  gives one independent verdict. Still failing → the pipeline stops and reports. It never loops forever.

<!-- CONFIGURE: raise MAX_ROUNDS in /review-code-fix and /review-ux-fix if you prefer more escalation rounds -->

## Keeping continuity honest: the evidence rule

A continued reviewer can get lazy: its context holds the **pre-fix** files, so it may "confirm" fixes from memory.
Every continued round must therefore show:

1. **Quoted post-fix lines** for each finding it marks resolved
2. **A re-read list**: every changed file re-read this round, with line counts
3. **A regression-hunt artifact**: at least one thing checked that was not a prior finding
4. **A fresh score** computed from the rubric, not carried forward

A continued-round report missing any of these is **not a pass**. Ask the reviewer to redo it; if it cannot, spawn a
fresh one. The evidenced re-read is what makes a continued reviewer as rigorous as a fresh one.

## Mechanics

**Spawn named.** Give the reviewer a stable name so every round addresses the same agent without juggling IDs.
`SendMessage` may be a deferred tool: load it (ToolSearch `select:SendMessage`) before round 2.

```
Agent({ subagent_type: "code-reviewer",            // "shipwright:code-reviewer" when installed as a plugin
        name: "reviewer-code", prompt: "..." })
...
SendMessage({ to: "reviewer-code", message: "<re-review prompt>" })
```

If the reviewer is unreachable (exited, or no reply after one nudge), spawn a fresh one, hand it the previous findings
table plus the fix SHA, and record `round N ran fresh` in the round table.

**Checklist by absolute path.** The reviewer has no Skill tool and, on a plugin install, the skills live in the
plugin cache rather than the project. The orchestrator passes the checklist as an absolute path plus section
(`<SKILLS_DIR>/review-code-fix/SKILL.md §Review focus`), where `SKILLS_DIR` is the parent of the running skill's base
directory.

**Findings file, not reply.** Subagent replies sometimes do not arrive. Before spawning, the orchestrator creates a
run-unique file with `STATUS: RUNNING` on line 1 and passes its absolute path. The reviewer appends its report and
flips line 1 to `STATUS: DONE`; its reply is only the path plus a one-line verdict.

```bash
RUN_DIR="${TMPDIR:-/tmp}/shipwright/$(git branch --show-current | tr / -)-$(date +%s)"
mkdir -p "$RUN_DIR" && printf 'STATUS: RUNNING\n' > "$RUN_DIR/code.md"
```

**Read the tree that ships.** If anything edited the files after the reviewer read them (for example audit-lens fixes
landing in the same batch), a round-1 pass does not close the gate. Run one verification round with the same
reviewer first.

**Reviewers never write.** The reviewer is read-only (`tools: Read, Grep, Glob, Bash`). The orchestrating session
applies fixes and commits. A reviewer that fixes its own findings is grading its own homework.

**Release the reviewer when the gate closes** (stop messaging it), not after each round.

## Which skills use it

| Skill | Named reviewer |
|---|---|
| [`/review-code-fix`](../skills/review-code-fix/SKILL.md) | `reviewer-code` |
| [`/review-ux-fix`](../skills/review-ux-fix/SKILL.md) | `reviewer-ux` |
| [`/review-docs`](../skills/review-docs/SKILL.md) | `reviewer-docs` (2 rounds, same reviewer) |
| [`/ship`](../skills/ship/SKILL.md) Phase A/R | spawns `reviewer-code`, `reviewer-ux`, `auditor` in one batch |
