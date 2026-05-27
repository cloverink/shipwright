# Phase Bundling

How sub-skills suppress commits when called from an orchestrator.

## The Problem

`/ship` calls `/audit-full`, `/review-code-fix`, and other skills sequentially. If each skill auto-commits its changes, you get:

```
abc1234 refactor(api): audit — dead code
def5678 refactor(api): audit — naming convention
ghi9012 fix(www): review — error boundary
jkl3456 fix(www): review — responsive layout
mno7890 docs(api): update API docs
```

Five commits for what should be three (one per phase).

## The Solution

Sub-skills detect when they're called as part of a pipeline and **suppress commits**, leaving changes staged instead.

```
When called standalone:  fix → commit → done
When called from /ship:  fix → stage → return (let parent commit)
```

The parent (`/ship`) then creates one commit per phase:

```
abc1234 refactor(api): audit fixes — dead code + naming
def5678 fix(www): review fixes — error boundary + responsive
ghi9012 docs(api): sync documentation
```

## How to Implement

In your skill's SKILL.md, add a section:

```markdown
## Bundling Behavior

When invoked as part of a pipeline (e.g., `/ship`):
- Apply all fixes
- Stage changes (`git add`)
- Do NOT commit
- Return list of what was fixed

When invoked standalone:
- Apply fixes
- Commit with conventional format
```

The orchestrating skill (`/ship`) passes context that tells the sub-skill which mode it's in. This can be as simple as a flag in the invocation or detecting that a parent pipeline is active.

## Why This Matters

1. **Clean git history** — one commit per phase, not one per file
2. **Atomic phases** — if Phase R fails, Phase A's commit is already clean
3. **Readable `git log`** — each commit explains a phase, not a micro-fix
4. **Easy revert** — revert one phase without touching others
