# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
