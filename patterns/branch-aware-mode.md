# Branch-Aware Mode

Skills that change behavior based on your current git branch.

## The Pattern

```
if (current branch == main) {
  // Standalone mode — whole-project scope
} else {
  // In-ticket mode — scoped to diff vs main
}
```

The skill detects your branch automatically. No flags, no configuration.

## Why?

The same skill serves two different needs:

**On `main`** — you're doing a project-wide health check. You want broad coverage, a comprehensive report, and probably a tracking issue.

**On a feature branch** — you're working on a specific ticket. You want focused feedback on what you changed, auto-fixes applied, and changes staged for your next commit.

Forcing the user to choose between these modes is unnecessary friction. The branch already tells you.

## How `/audit-full` uses this

| Branch | Scope | Output | Commit behavior |
|--------|-------|--------|-----------------|
| `main` | Entire project | Opens GitHub issue with all findings | No changes made |
| `feat/*` | `git diff origin/main...HEAD` only | Auto-fixes P0-P2, stages changes | Stages only (no commit) |

`/audit-full` is currently the only skill that implements this pattern. Other skills (e.g., `/review-full`) always scope to the current diff regardless of branch.

## Implementing in Your Skills

```markdown
## Branch Detection

1. Check current branch: `git branch --show-current`
2. If `main` (or `master`): run in standalone mode
3. Otherwise: run in in-ticket mode, scoped to `git diff origin/main...HEAD`
```

The detection is simple. The value is in designing two distinct behaviors for the same skill, so the user never has to think about which mode they need.
