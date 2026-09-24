# A→R→D→S Pipeline

The core pattern behind `/ship`. Four phases, each with a gate that must pass before the next phase runs.
Audit and Review share a first round, so the slowest part of the pipeline runs in parallel.

## The Phases

```
A+R (Audit + Review)  → one parallel batch of read-only Opus lenses → union findings → fix → commit
R   (Review rounds)   → same reviewers re-check the fixes until the gates pass
D   (Docs)            → sync documentation with the code that is about to ship
S   (Ship)            → push branch + open PR
```

## Why this order?

**Audit and Review together, then Review alone.** Audit (dead code, magic values, slow tests) and Review
(correctness, security, UX) both read the same diff and neither writes. Running them one after the other doubled
the wall-clock for no gain, so round 1 is **one batch**: every lens is spawned in the same tool-call block, the
findings are unioned, and one commit fixes them all. Rounds 2+ are review-only.

**Review before Docs.** Review may change code. Do not write docs for code that is about to change.

**Docs before Ship.** Docs are part of the deliverable. A PR without updated docs is incomplete.

**Ship last.** Everything else must pass before the work leaves your machine.

## Gate Enforcement

Each phase has a gate. If the gate fails, the pipeline **stops and reports**. It never silently skips a failed phase.

| Phase | Gate | What blocks |
|---|---|---|
| A+R round 1 | Every lens reported | A lens that crashed or was skipped means that dimension was never reviewed: re-run it, never report green |
| R | Code ≥ 9.5, UX = 10/10 | Still failing after round 4 (the fresh escalation reviewer) |
| D | Docs accurate (binary) | Dead links, stale stats after 2 rounds |
| S | Clean working tree | Uncommitted changes |

## Who does what

| Role | Who | Writes files? |
|---|---|---|
| Orchestrator | the **main session** running `/ship` | commits only |
| Reviewers / auditors | `code-reviewer` agent (Opus), one per lens | never |
| Fixer | the main session (or one Sonnet worker per file) | yes, one writer per file |

The main session drives the pipeline directly. It does **not** hand the whole pipeline to one subagent: that shape is
serial, reviews its own fixes, and cannot keep a reviewer alive across rounds. See
[Reviewer Continuity](reviewer-continuity.md).

## Per-Phase Commits

```
refactor(api): audit + review fixes (A/R round 1)
fix(api): review fixes (round 2)
docs(api): sync documentation
```

Each round gets its own commit so the re-review prompt can point at a SHA, and `git log` stays readable. A phase
that came back clean gets no empty commit; the PR body says "Phase X came back clean" instead.

## Adapting the Pipeline

- **No frontend?** The UX lens is skipped automatically when no frontend path changed
- **No docs?** Remove Phase D
- **Custom audit?** Point the audit lens at your own checklist
- **Different thresholds?** Adjust the score gates (see [Score Gates](score-gates.md))

The phases are conventions, not constraints. Use what works for your project.
