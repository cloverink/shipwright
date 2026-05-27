# Shipwright — Contributor Rules

Conventions for adding or editing skills in this repo.

## Layout

All skills live flat under `skills/<skill-name>/SKILL.md`. No bucket grouping — this matches Claude Code's skill-discovery convention and keeps every skill discoverable at one level.

## Required References

Every skill must have:

1. A row in the top-level [`README.md`](README.md) skills table
2. An entry in [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) skills list

## SKILL.md Frontmatter

Use shorthand model names — `opus`, `sonnet`, `haiku` — not full IDs.

```yaml
---
name: my-skill
description: One-line summary used for skill discovery
model: sonnet
---
```

## Patterns Reference

Reusable design patterns live in [`patterns/`](patterns/). When introducing a new skill, check if an existing pattern applies — link to it from the skill's SKILL.md instead of re-explaining.
