---
name: skill-creator
description: Meta-skill that teaches how to create effective Claude Code skills. Covers anatomy, progressive disclosure, validation, and packaging.
model: sonnet
---

# /skill-creator

A skill for creating skills. Use this when building new skills or improving existing ones.

## Skill Anatomy

```
my-skill/
├── SKILL.md              # Main skill file (YAML frontmatter + instructions)
├── references/           # Supporting docs loaded on demand
│   ├── patterns.md
│   └── examples.md
└── scripts/              # Optional automation scripts
    └── validate.sh
```

### SKILL.md Structure

```yaml
---
name: my-skill
description: One-line description used for skill discovery and relevance matching
model: opus               # Optional: opus, sonnet, or haiku
---

# /my-skill

[Core instructions: what to do, how to do it, when to stop]
```

## Design Principles

### 1. Progressive Disclosure

Don't dump everything into SKILL.md. Layer information:

| Layer | Where | When loaded |
|-------|-------|-------------|
| Discovery | `name` + `description` in frontmatter | Always (~20 tokens) |
| Core instructions | SKILL.md body | When skill is invoked (~500-2000 tokens) |
| Deep reference | `references/*.md` | On demand, when needed |

### 2. Degrees of Freedom

Match the skill's rigidity to its purpose:

- **Rigid skills** (debugging, TDD): Follow exactly. Steps are a discipline, not suggestions.
- **Flexible skills** (design, architecture): Adapt principles to context. Steps are guidelines.

State which type your skill is. Ambiguity leads to shortcuts.

### 3. Actionable Instructions

Write instructions that Claude can execute, not descriptions of what a human would do.

```
# Bad: describes, doesn't instruct
"The review process involves examining code for quality issues."

# Good: actionable
"Read every changed file end-to-end. For each file, check:
1. Type safety: no `any`, explicit return types
2. Security: no secrets, input validation
List issues as [severity] [file:line] description."
```

### 4. Exit Conditions

Every skill must define when it's done:

```
# Bad: no exit condition
"Review the code and fix issues."

# Good: clear exit
"Review → fix → re-review. Exit when score > 9 or after 3 rounds."
```

## Creation Process

1. **Define the trigger**: when should this skill activate? Be specific.
2. **Write the happy path**: what does the skill do when everything works?
3. **Add failure modes**: what happens when things go wrong? When does it stop and ask the user?
4. **Add configuration points**: mark project-specific values with `<!-- CONFIGURE -->` comments.
5. **Test with real tasks**: invoke the skill on actual work. Does it produce good results?
6. **Iterate**: skills improve with use. Update based on what works.

## Validation Checklist

Before publishing a skill:

- [ ] Frontmatter has `name` and `description`
- [ ] Description is specific enough for relevance matching
- [ ] Instructions are actionable (Claude can execute them)
- [ ] Exit conditions are defined
- [ ] Configuration points are marked
- [ ] No hardcoded project-specific values in the main instructions
- [ ] Tested on at least one real task

## Packaging for Distribution

If publishing skills for others to use:

1. Add skill path to `.claude-plugin/plugin.json`
2. Mark all project-specific values with `<!-- CONFIGURE -->` and document defaults
3. Include a `references/` folder for deep-dive docs
4. Add the skill to the README with a one-line description
