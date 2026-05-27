# A→R→D→S Pipeline

The core pattern behind `/ship`. Four sequential phases, each with a gate that must pass before the next phase runs.

## The Phases

```
A (Audit)    → Find and auto-fix code quality issues
R (Review)   → Code review + UX review with fix loops
D (Docs)     → Sync documentation with code changes
S (Ship)     → Push branch + open PR
```

## Why this order?

**Audit before Review** — Audit catches mechanical issues (dead code, convention violations, missing imports) that would clutter a code review. Fix them first so the reviewer focuses on logic, architecture, and design.

**Review before Docs** — Review may change code. Don't write docs for code that's about to change.

**Docs before Ship** — Docs are part of the deliverable. A PR without updated docs is incomplete.

**Ship last** — Everything else must pass before the work leaves your machine.

## Gate Enforcement

Each phase has a gate. If the gate fails, the pipeline **stops and reports**. It never silently skips a failed phase.

| Phase | Gate | What blocks |
|-------|------|-------------|
| A | Auto-fixes applied cleanly | Unfixable Critical issues |
| R | Code >9, UX 10/10 | Score below threshold after 3 rounds |
| D | No stale references | Dead links, outdated stats |
| S | Clean working tree | Uncommitted changes |

## Per-Phase Commits

Each phase produces its own commit. This keeps `git log` readable:

```
refactor(backend): audit fixes — remove dead code, fix N+1 query
fix(frontend): review fixes — add error boundary, fix responsive layout
docs(api): sync module documentation
```

The alternative — one giant commit — makes it impossible to understand what changed and why.

## Subagent Strategy

`/ship` spawns a subagent for the A→R→D→S work. Why?

1. **Context freshness** — the subagent starts with a clean context, not polluted by hours of coding
2. **Isolation** — if the pipeline fails midway, the main session's context isn't consumed
3. **Resumability** — the main session can report status and re-run if needed

## Adapting the Pipeline

The pipeline is modular. Common adaptations:

- **No frontend?** Remove UX review from Phase R
- **No docs?** Remove Phase D entirely
- **Custom audit?** Replace Phase A with your own audit skill
- **Different thresholds?** Adjust the score gates in each skill

The phases are conventions, not constraints. Use what works for your project.
