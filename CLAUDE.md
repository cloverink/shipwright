# Shipwright: Contributor Rules

Conventions for adding or editing skills in this repo.

## Layout

All skills live flat under `skills/<skill-name>/SKILL.md`. No bucket grouping: this matches Claude Code's skill-discovery convention and keeps every skill discoverable at one level.

Agents live under `agents/<name>.md`. The one shipped agent, `code-reviewer` (Opus, read-only), is the only
reviewer skills should spawn: skills pass it a lens instead of defining their own reviewer.

## Required References

Every skill must have:

1. A row in the top-level [`README.md`](README.md) skills table
2. An entry in [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) skills list

Every agent must be listed in `plugin.json` `agents` and keep read-only tools if it reviews.

## SKILL.md Frontmatter

Use shorthand model names (`opus`, `sonnet`, `haiku`), not full IDs.

```yaml
---
name: my-skill
description: One-line summary used for skill discovery
model: sonnet
---
```

## Patterns Reference

Reusable design patterns live in [`patterns/`](patterns/). When introducing a new skill, check if an existing pattern applies: link to it from the skill's SKILL.md instead of re-explaining.
