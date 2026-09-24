---
name: audit-full
description: Branch-aware audit. On main, scans the whole project and opens one tracker issue. On a feature branch, audits the diff with an Opus auditor, auto-fixes, and stages. Inside /ship it is the audit lens of the parallel A/R batch.
model: sonnet
---

# /audit-full

Audit that changes behavior based on where you are. See [Branch-Aware Mode](../../patterns/branch-aware-mode.md).

## Modes

| Where | Mode | Behavior |
|---|---|---|
| `main` | Standalone | Scan the whole project → open ONE consolidated GitHub issue |
| feature branch | In-ticket | Audit the diff vs main → auto-fix → stage (no commit) |
| inside `/ship` | Lens | `/ship` spawns the auditor next to the reviewers; this file is only the checklist |

## Execution

The audit itself is judged by the read-only [`code-reviewer`](../../agents/code-reviewer.md) agent (Opus) with lens
`audit`, named `auditor`, writing to a findings file. This session applies the fixes. The auditor never edits.

Large project on `main`? Split by top-level area and spawn one auditor per area **in one tool-call block**.

Spawn (standalone modes). Run the setup as **one** Bash call and paste the echoed values as literals, since shell
variables do not survive between Bash calls:

```bash
RUN_DIR="${TMPDIR:-/tmp}/shipwright/$(git branch --show-current | tr / -)-$(date +%s)"
mkdir -p "$RUN_DIR" && printf 'STATUS: RUNNING\n' > "$RUN_DIR/audit.md" && echo "RUN_DIR=$RUN_DIR"
```

```
Agent({
  subagent_type: "code-reviewer",          // "shipwright:code-reviewer" when installed as a plugin
  name: "auditor",
  prompt: "Lens: audit. Checklist: <SKILLS_DIR>/audit-full/SKILL.md §Audit checks.
           Scope: <whole project | changed files vs BASE>. Findings file: <RUN_DIR>/audit.md.
           Append, flip line 1 to STATUS: DONE, reply with path + verdict only."
})
```

`SKILLS_DIR` is the parent of this skill's base directory. The agent has no Skill tool, so the checklist path must be
absolute. One auditor per area → one findings file per area (`audit-<area>.md`).

## Audit checks

The `audit` lens checklist. The auditor loads this section.

1. **Config** (only if config files changed): scripts that point nowhere, duplicate or conflicting settings,
   secrets in config, CI steps that no longer match the code
2. **Code**: dead code, unused exports, magic values, duplicated logic, functions over ~50 lines, nesting over 3,
   accidental O(n²) on unbounded input
3. **Tests**: slow tests, inline mocks that should be shared fixtures, missing edge cases (empty, error, boundary),
   tests that assert nothing

<!-- CONFIGURE: add your own audit checks or remove passes you don't need -->

## Priorities

| Priority | Meaning | Auto-fixed in-ticket? |
|---|---|---|
| P0 Critical | security, data loss | yes |
| P1 Major | bug, perf regression | yes |
| P2 Warning | convention violation | yes |
| P3 Suggestion | style, naming nit | no, listed in the report (inside `/ship`: in the PR body) |

## Standalone (on main)

1. Spawn auditor(s) over the whole project
2. Group findings by module
3. Open ONE GitHub issue: `Audit: <date> · <N> findings across <M> areas`

One issue, not twenty: one consolidated tracker is easier to triage and does not spam the repo.

## In-ticket (feature branch)

1. `BASE=$(git merge-base origin/main HEAD)` → changed files only
2. Spawn the auditor over them
3. Fix P0-P2 → lint → `git add` (no commit)
4. Report fixed vs needs-manual-attention

No commit: whoever called this commits per phase. See [Phase Bundling](../../patterns/phase-bundling.md).

## Usage

```
/audit-full              # mode detected from the current branch
```
