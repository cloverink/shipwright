---
name: parallel-builder
description: Build multiple files/pages in parallel using subagents. Handles task division, shared file coordination, and build verification. Conflict-free by design.
model: sonnet
---

# /parallel-builder

Orchestrate building many files at once without merge conflicts.

## When to use

- Building 3+ independent components/pages
- Migrating many files to a new pattern
- Generating boilerplate across a feature

## How it works

1. **Divide** — split work into independent batches (no shared file edits within a batch)
2. **Register shared files** — identify files that multiple batches might touch
3. **Spawn subagents** — one per batch, working on independent files
4. **Coordinate** — main agent handles shared files after all subagents complete
5. **Verify** — build + typecheck to catch integration issues

## Shared File Registry

Before spawning agents, identify files that appear in multiple batches:

```
Shared files (main agent handles these AFTER subagents finish):
- Router config (e.g., routes.tsx, app.module.ts)
- Barrel exports (e.g., index.ts)
- Shared types (e.g., types.ts)
```

<!-- CONFIGURE: List your project's typical shared/coordination files -->

Rule: **subagents never edit shared files**. Only the main agent does, after all parallel work completes.

## Batch Size Guidelines

| Files to build | Strategy |
|----------------|----------|
| 1-2 | Just do it sequentially — no need for parallel |
| 3-5 | 2-3 subagents |
| 6-10 | 3-4 subagents |
| 10+ | 4-5 subagents max (diminishing returns) |

## Pre-flight Checklist

Before spawning:
- [ ] All target directories exist
- [ ] Shared files identified and excluded from subagent scope
- [ ] Each batch's files are truly independent
- [ ] Build passes before starting (clean baseline)

## Post-flight Checklist

After all subagents complete:
- [ ] Update shared files (routes, exports, types)
- [ ] Run build + typecheck
- [ ] Verify no duplicate exports or circular imports
- [ ] Spot-check a sample of generated files
