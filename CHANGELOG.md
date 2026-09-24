# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Review flow rebuilt on the harness that ships real work in production: faster rounds, stable scores, Opus on every verdict.

### Added

- **`code-reviewer` agent** (`agents/code-reviewer.md`, `model: opus`, read-only tools). Every audit, code, UX and docs verdict now comes from it, loaded with a per-job lens. Registered in `plugin.json` under `agents`.
- **Reviewer Continuity pattern** (`patterns/reviewer-continuity.md`): one named reviewer per gate, continued via `SendMessage` for rounds 2-3, an evidence rule for continued rounds, a fresh escalation reviewer at round 4, then stop.
- **Findings files**: reviewers append to a `STATUS: RUNNING` file and flip it to `DONE`, so a lost reply or a crashed lens can never read as a green gate.
- `/review-full --read-only` for a scored peek with no edits.
- UX lens looks at the running app (Playwright screenshots read back as images), with a dev-server + screenshot precheck in `/review-ux-fix` so the 10/10 gate cannot fail by construction.
- Reviewers receive their checklist as an absolute path, so the agent works on a plugin install where skills live in the plugin cache.
- `/push` bundled mode: under `/ship` it only opens (or updates) the PR.
- `/audit-full` on `main` can fan out one Opus auditor per top-level area in parallel, one findings file each.
- README diagrams generated with diagram-design (`docs/diagrams/`), light + dark PNGs in `docs/assets/`.
- CI: validates agents (frontmatter, read-only tools, registration) and README image paths; the README row check now reads the skill count from `plugin.json`.

### Changed

- **`/ship` runs Audit and Review round 1 as one parallel batch** (auditor + reviewer-code + reviewer-ux in one tool call), one commit per round.
- **`/ship` runs in the main session** instead of delegating the pipeline to one subagent.
- **Fix loops keep the same reviewer** across rounds 1-3 instead of spawning a fresh one each round. Max rounds: 3 continued + 1 fresh (was 3 fresh).
- **Code gate is now `>= 9.5`** (was `> 9`): with -0.1 Suggestions, scores of 9.1-9.4 exist and now fail explicitly.
- **Suggestions now cost -0.1 each (max -0.5)** instead of 0. Suggestions alone still cannot fail the code gate; when a gate fails, every open finding is fixed.
- Orchestrating skills (`/ship`, `/review-code-fix`, `/review-ux-fix`, `/review-docs`) moved to `model: sonnet`, since the Opus judgment now lives in the agent.
- `/update-docs` and `/ship` never guess a diff base: they stop if `origin/main` cannot be resolved (was a silent `HEAD~5` fallback in `/update-docs`).
- `scripts/link-skills.sh` also links `agents/*` into `~/.claude/agents`.

## [0.1.1] — 2026-05-28

### Fixed

- `marketplace.json` schema now matches the official `claude-code-marketplace.json` spec. Previous schema caused install error "This plugin uses a source type your Claude Code version does not support."
  - `source` is now a string (`"./"`) instead of an object with `type`/`repo` keys
  - Description moved from `metadata.description` to top-level (no `metadata` wrapper)
  - Added `$schema` reference, per-plugin `author`, `homepage`, `repository`, `license`, `keywords`, `category` for discoverability

## [0.1.0] — 2026-05-27

Initial release.

### Added

**12 skills (flat layout under `skills/`):**

- `/ship` — A→R→D→S pipeline orchestrator (Opus)
- `/audit-full` — Phase A, branch-aware audit (Sonnet)
- `/review-full` — Phase R dispatcher (Sonnet)
- `/review-code-fix` — code review + fix loop, gate >9/10 (Opus)
- `/review-ux-fix` — UX review + fix loop, gate 10/10 (Opus)
- `/update-docs` — Phase D, tier 1–4 doc sync (Sonnet)
- `/review-docs` — Phase D gate, binary pass/fail (Opus)
- `/push` — Phase S, smart commit + PR (Sonnet)
- `/merge-pr` — post-merge, wait CI + squash (Haiku)
- `/parallel-builder` — conflict-free parallel builds (Sonnet)
- `/frontend-design` — distinctive UI design (Opus)
- `/skill-creator` — meta guide for new skills (Sonnet)

**4 design patterns (`patterns/`):**

- A→R→D→S Pipeline — sequential phases with gate enforcement
- Score Gates — strict numeric thresholds (>9, 10/10, binary)
- Branch-Aware Mode — main vs feature branch behavior
- Phase Bundling — sub-skills suppress commits under orchestrator

**Distribution:**

- `.claude-plugin/plugin.json` — 12 skills registered
- `.claude-plugin/marketplace.json` — installable via `/plugin marketplace add`
- `scripts/link-skills.sh`, `list-skills.sh` — local dev helpers

**Documentation:**

- README with Mermaid pipeline + review-family diagrams
- "Which review skill to use?" decision matrix
- `CLAUDE.md` contributor rules
- "When to use" headers on every review skill

[Unreleased]: https://github.com/cloverink/shipwright/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/cloverink/shipwright/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/cloverink/shipwright/releases/tag/v0.1.0
