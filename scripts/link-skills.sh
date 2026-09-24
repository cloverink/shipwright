#!/usr/bin/env bash
set -euo pipefail

# Links every skill to ~/.claude/skills/ and every agent to ~/.claude/agents/

REPO="$(cd "$(dirname "$0")/.." && pwd)"

guard_dest() {
  local dest="$1"
  if [ -L "$dest" ]; then
    local resolved
    resolved="$(readlink -f "$dest")"
    case "$resolved" in
      "$REPO"|"$REPO"/*)
        echo "error: $dest is a symlink into this repo ($resolved)." >&2
        echo "Remove it (rm \"$dest\") and re-run." >&2
        exit 1
        ;;
    esac
  fi
  mkdir -p "$dest"
}

link() {
  local src="$1" target="$2" name
  name="$(basename "$target")"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "SKIP $name: $target already exists (not a symlink). Remove it manually to link."
    return
  fi
  ln -sfn "$src" "$target"
  echo "linked $name -> $src"
}

SKILLS_DEST="$HOME/.claude/skills"
guard_dest "$SKILLS_DEST"
find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -print0 |
while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  link "$src" "$SKILLS_DEST/$(basename "$src")"
done

AGENTS_DEST="$HOME/.claude/agents"
guard_dest "$AGENTS_DEST"
find "$REPO/agents" -maxdepth 1 -name '*.md' -print0 |
while IFS= read -r -d '' agent_md; do
  link "$agent_md" "$AGENTS_DEST/$(basename "$agent_md")"
done
