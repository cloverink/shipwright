---
name: review-docs
description: Verify Phase D doc updates are accurate. Binary pass/fail gate judged by an Opus reviewer (stats, links, code-doc sync, completeness), same reviewer for both rounds. Runs after /update-docs.
model: sonnet
---

# /review-docs

Quality gate for documentation. Catches stale stats, dead links, and drift between code and docs.

> **When to use:** Verify doc accuracy after [`/update-docs`](../update-docs/SKILL.md), or as a standalone doc audit.
> **Use [`/review-full`](../review-full/SKILL.md) instead if:** your diff is mixed (code + docs): it'll detect scope and dispatch.
> **Called by:** `/ship` Phase D (after [`/update-docs`](../update-docs/SKILL.md)), [`/review-full`](../review-full/SKILL.md) (docs-only diffs).

## Execution: Opus judges, this session fixes

Docs are a trust surface. Sonnet misses cross-file inconsistencies (README says "30 modules" but `modules/` has 32
files), so the verdict comes from the read-only [`code-reviewer`](../../agents/code-reviewer.md) agent (Opus), lens
`docs`, named `reviewer-docs`. This session runs the automated checks, applies fixes and re-stages.

Round 2 continues the **same** reviewer via `SendMessage` with the evidence rule from
[Reviewer Continuity](../../patterns/reviewer-continuity.md). No round 3: still failing → stop and report.

<!-- CONFIGURE: skip the reviewer spawn and rely on Step 3 tools alone if your docs are simple -->

## When to run

```
Phase D pipeline:
  /update-docs  → stage doc changes
  /review-docs  → verify them    ← you are here
  (if fail)     → fix in-place, re-stage, same reviewer re-checks (max 2 rounds)
  (if pass)     → continue to Phase S (ship)
```

Always run after `/update-docs`, even if it reports "came back clean". Verify the claim with Step 3's tools; spawn
the reviewer only when there is a staged doc diff or a tool reports drift.

## Bundling behavior

When called from `/ship`:
- Read-only review of staged doc changes
- If issues found: fix in-place, re-stage, re-review
- Do NOT commit: `/ship` commits per phase

## Step 1: Gather doc changes

```bash
git diff --cached --stat -- '*.md'
git diff --cached -- '*.md'
```

If no staged doc changes AND `/update-docs` reported "clean" → report "Phase D clean: no doc changes to review" and pass.

## Step 2: Review focus areas

| Risk | What to check |
|------|---------------|
| **Stat accuracy** | Counts (components, endpoints, tests, modules) match reality |
| **File path validity** | All `[link](path)` references point to files that exist |
| **Code-doc sync** | Function names, prop signatures, route paths match source |
| **Frontmatter** | Updated docs have valid title/description metadata |
| **Completeness** | All relevant tiers updated (core, arch, journey, config) |
| **Stale dates** | Dates that should have been updated are current |

<!-- CONFIGURE: Add project-specific risks (e.g., versioned API docs, i18n strings) -->

## Step 3: Automated checks

Run any doc-drift tools your project has:

```bash
# Example: replace with your project's tools
bun run tools/doc-drift.ts        # dead file refs + stale dates
bun run tools/stats-sync.ts       # stat accuracy (check-only mode)
```

<!-- CONFIGURE: Replace with your tools, or remove if you don't have them -->

Any non-zero output = automatic fail.

If you don't have tools, manually spot-check (assumes repo-root-relative links; relative paths like `../foo.md` will need adjustment):

```bash
# Find dead doc links (root-relative only)
grep -roE '\[.*\]\([^)]+\.md\)' --include='*.md' . | \
  awk -F'[()]' '{print $2}' | sort -u | \
  while read f; do [ -f "$f" ] || echo "DEAD: $f"; done
```

## Step 4: Scoring

Binary pass/fail. No numeric score.

| Result | Meaning |
|--------|---------|
| Pass | All docs accurate, no stale references, stats match reality |
| Fail | One or more issues found: list per issue with file path |

Why binary? Either docs are accurate or they're not. "Mostly accurate" docs are a trap: users trust them, then hit the inaccurate part.

## Step 5: Report

```markdown
## Review Docs Report

Files reviewed: X docs changed
Tiers covered: 1 (core) / 2 (arch) / 3 (journey) / 4 (config)

| Check | Status |
|-------|--------|
| Stat accuracy | pass / fail |
| File path validity | pass / fail |
| Code-doc sync | pass / fail |
| Frontmatter | pass / fail |
| Completeness | pass / fail |

Issues: (if any, with file path + description)

Result: PASS / FAIL
Ready for Phase S: Yes / No
```

## Guidelines

- **Binary pass/fail**: no numeric score
- **Scope to doc diff only**: don't review impl code (that's Phase R's job)
- **Fix in-place**: if issues found, fix immediately, re-stage, re-review
- **Reviewer is read-only**: the agent reports, this session edits
- **Max 2 rounds, same reviewer**: still failing after round 2 → flag to user

## Exit conditions

- PASS → return "Ready for Phase S", OR
- FAIL after 2 fix rounds → return remaining issues, stop pipeline
