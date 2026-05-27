---
name: audit-full
description: Branch-aware audit orchestrator. On main — scans whole project, opens tracker issue. On feature branch — scopes to diff, auto-fixes, stages changes.
model: sonnet
---

# /audit-full

Smart audit that changes behavior based on where you are.

## Branch-Aware Modes

| Branch | Mode | Behavior |
|--------|------|----------|
| `main` | Standalone | Scan whole project → open ONE consolidated GitHub issue |
| `feat/*`, `fix/*` | In-ticket | Scope to diff vs main → auto-fix → stage changes (no commit) |

The skill detects your branch automatically. No flags needed.

## What it audits

Orchestrates three audit passes in sequence:

1. **Config audit** — project configuration health (only runs if config files changed)
2. **Code audit** — code smells, dead code, magic values, complexity, Big-O
3. **Test audit** — slow tests, inline mocks, missing edge cases, optimization opportunities

<!-- CONFIGURE: Replace with your own audit checks or remove passes you don't need -->

## Priority System

Issues found are classified:

| Priority | Meaning | Auto-fixed? |
|----------|---------|-------------|
| P0 (Critical) | Security, data loss | Yes |
| P1 (Major) | Bugs, perf regression | Yes |
| P2 (Warning) | Convention violations | Yes |
| P3 (Suggestion) | Style, naming nits | **No** — user decides |

In-ticket mode auto-fixes P0-P2. Standalone mode reports all issues in the tracker issue for human triage.

## Standalone Mode (on main)

```
1. Scan full project
2. Group findings by module/area
3. Open ONE GitHub issue with all findings
4. Title: "Audit: <date> — <N> findings across <M> areas"
```

Why one issue? Avoid GitHub spam. One consolidated tracker is easier to triage than 20 tiny issues.

## In-Ticket Mode (on feature branch)

```
1. git diff origin/main...HEAD → changed files only
2. Run audit passes on changed files
3. Auto-fix P0-P2
4. Stage fixes (git add) — do NOT commit
5. Report what was fixed and what needs manual attention
```

No commit because `/ship` handles commits per-phase. The staged changes become part of Phase A's commit.

## Usage

```
/audit-full              # Auto-detect mode from current branch
```
