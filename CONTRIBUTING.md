# Contributing to shipwright

Thanks for your interest. Here's how to add a new skill or improve an existing one.

## Quick start

1. Fork the repo and clone your fork
2. Create a feature branch: `git checkout -b feat/your-change`
3. Make changes (see conventions below)
4. Test locally: `./scripts/link-skills.sh` then invoke skills in Claude Code
5. Validate: GitHub Actions will run automatically on your PR
6. Open a PR using the template

## Adding a new skill

Create `skills/<your-skill>/SKILL.md`:

```yaml
---
name: your-skill
description: One-line summary used for skill discovery
model: opus | sonnet | haiku
---

# /your-skill

[Core instructions — what to do, how, when to stop]
```

Then update three places:

1. Add `./skills/your-skill` to `.claude-plugin/plugin.json` `skills` array
2. Add a row to the Skills table in `README.md` (sorted by pipeline order)
3. Add an entry to `CHANGELOG.md` under `[Unreleased]`

For deeper guidance, see [`/skill-creator`](skills/skill-creator/SKILL.md).

## Conventions

| Convention | Rule |
|------------|------|
| **Model field** | shorthand — `opus`, `sonnet`, `haiku` — NOT full IDs |
| **CONFIGURE markers** | every project-specific value gets `<!-- CONFIGURE: ... -->` |
| **Cross-references** | use bare skill names (`/audit-full`) not file paths |
| **Commit format** | Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`) |
| **Scope in commits** | per-package scope when relevant (`fix(api):`, `docs(www):`) |
| **Layout** | skills live FLAT under `skills/<name>/` — no bucket folders |

## Using existing patterns

Four patterns are documented in [`patterns/`](patterns/):

- A→R→D→S Pipeline
- Score Gates
- Branch-Aware Mode
- Phase Bundling

If your skill uses one, link to the pattern doc instead of re-explaining. If you introduce a NEW pattern, add `patterns/<your-pattern>.md` and link from skills that use it.

## Quality bar

`shipwright` ships strict skills. Match the bar:

- SKILL.md is **actionable** — Claude can execute it, not just understand it
- Has clear **exit conditions** — when does the skill report "done"?
- Adheres to **score gates** — `>9` for code, `10/10` for UX, binary for docs
- Has tested **bundling behavior** — sub-skills should suppress commits when called from `/ship`

## Templates

- 🐛 Found a bug? → [bug template](.github/ISSUE_TEMPLATE/bug.md)
- 💡 New skill idea? → [skill request](.github/ISSUE_TEMPLATE/skill-request.md)
- 📝 Opening a PR? → [PR template](.github/PULL_REQUEST_TEMPLATE.md)

## Code of conduct

Be excellent to each other. Disagree on technical merit, not on people.
