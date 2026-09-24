---
name: update-docs
description: Sync documentation with code changes. Auto-detects scope from git diff, updates tier 1-4 docs (core, architecture, journey, config), verifies stats. Phase D of /ship pipeline.
model: sonnet
---

# /update-docs

Keep documentation in sync with code. Detects what changed, updates the right tiers, leaves changes staged for review.

## How it works

```
1. Detect changes  → git diff vs the merge base with origin/main
2. Classify        → categorize files into doc tiers
3. Update          → edit relevant docs per tier
4. Verify stats    → run stats tools, refresh counts
5. Stage           → git add (no commit, the parent commits per phase)
```

## Bundling behavior

When called from `/ship` (Phase D):
- Apply doc updates
- Stage changes (`git add`)
- Do NOT commit; `/ship` commits as `docs(<scope>): sync documentation`
- Cover everything that ships: the original work **and** every A/R fix round
- Return summary of what was updated

When called standalone:
- Apply doc updates
- Commit as `docs: update documentation`

## Phase 1: Detect Changes

```bash
BRANCH=$(git branch --show-current)
BASE=$(git merge-base origin/main HEAD) || { echo "cannot resolve origin/main, git fetch first"; exit 1; }   # never guess a base
git diff --name-only $BASE..HEAD
git diff --name-only HEAD  # also include unstaged
```

<!-- CONFIGURE: Adjust exclude patterns for your project (e.g., lockfiles, generated files) -->

## Phase 2: Documentation Tiers

| Tier | Files | Trigger |
|------|-------|---------|
| 1 Core | `README.md`, `CLAUDE.md`, top-level package READMEs | Any significant change |
| 2 Architecture | `docs/architecture.md`, `docs/database-schema.md` | Structural changes |
| 3 Journey | `docs/journey/*.md` (user flows) | Business logic changes |
| 4 Claude Config | `.claude/rules/*.md`, `.claude/skills/**/references/*.md` | Tool/workflow changes |

<!-- CONFIGURE: Replace tier paths to match your project's doc layout. Remove tiers you don't use. -->

## Phase 3: Stats Verification

If your project has a stats sync tool, run it first: it's the single source of truth for counts in README/CLAUDE.md.

```bash
# Example: replace with your project's tool
bun run tools/stats-sync.ts --update    # writes diffs into core docs
bun run tools/stats-sync.ts             # check-only mode for CI
```

<!-- CONFIGURE: Replace with your stats sync command, or remove if you don't track counts in docs -->

If no automated tool, verify common counts manually:

```bash
# Components, endpoints, tests: adjust globs to your structure
find src/components -name "*.tsx" | wc -l
grep -rcE "@(Get|Post|Patch|Delete|Put)\(" --include="*.ts" src/api/
```

## Phase 4: Per-Change Update Checklist

| Change type | Update |
|-------------|--------|
| New feature | README features list, relevant journey doc, CLAUDE.md if it affects how AI agents work |
| New API endpoint | API doc / journey doc with endpoint table, CLAUDE.md endpoint count |
| New component | Component README, design system doc if it introduces a pattern |
| Database change | `docs/database-schema.md`, migration notes, related journey docs |
| Config change | Doc that explains the config option, rule files that reference it |
| Refactor | Update file paths in any doc that linked to moved/renamed files |
| Dependency upgrade | CHANGELOG, README if version is documented |

<!-- CONFIGURE: Add change types specific to your project -->

## Phase 5: Stage & Report

```bash
git add README.md CLAUDE.md docs/ .claude/
```

Report format:

```
Documentation Update Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scope: <auto-detected files>
Updated:   path/to/doc.md: what changed
Verified:  Components: X | Tests: X | Endpoints: X
Skipped:   path/to/doc.md: already up to date
Manual:    path/to/doc.md: needs human review (reason)
```

## Guidelines

- **Concise**: lead with the answer, not the context
- **Scannable**: tables, bullet lists, headers
- **Cross-reference, don't duplicate**: link to related docs
- **Match code reality**: every code example, path, count must match the current code
- **Stage everything, commit nothing** when called from `/ship`

## Exit conditions

- All affected tiers updated, OR
- Reported as "no doc-worthy changes" if diff is purely internal (formatting, comments, test-only)
- Manual-review items flagged with reason
