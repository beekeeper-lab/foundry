#!/usr/bin/env bash
# claude-link.sh — Rebuild .claude/ assembly symlinks from kit + local.
# Kit content lives at .claude/kit/.claude/shared/{agents,commands,skills,hooks,settings.json}.
# Local overrides live at .claude/local/{agents,commands,skills}.
# Assembly symlinks go in .claude/{agents,commands,skills,hooks,settings.json}.
# Local assets win on name collision with kit assets.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
CLAUDE_DIR="$REPO_ROOT/.claude"
KIT_SHARED="$CLAUDE_DIR/kit/.claude/shared"
LOCAL_DIR="$CLAUDE_DIR/local"

# Relative paths from .claude/ (for top-level symlinks like hooks, settings, shared)
REL_KIT="kit/.claude/shared"
# Relative paths from .claude/<subdir>/ (for symlinks inside commands/, skills/, agents/)
REL_KIT_UP="../kit/.claude/shared"
REL_LOCAL_UP="../local"

if [ ! -d "$KIT_SHARED" ]; then
    echo "[claude-link] ERROR: Kit content not found at $KIT_SHARED"
    echo "[claude-link] Run: git submodule update --init --recursive"
    exit 1
fi

# --- Commands ---
mkdir -p "$CLAUDE_DIR/commands"
find "$CLAUDE_DIR/commands" -maxdepth 1 -type l -delete 2>/dev/null || true

for f in "$KIT_SHARED/commands/"*.md; do
    [ -f "$f" ] || continue
    ln -sfn "$REL_KIT_UP/commands/$(basename "$f")" "$CLAUDE_DIR/commands/$(basename "$f")"
done

if [ -d "$KIT_SHARED/commands/internal" ]; then
    ln -sfn "$REL_KIT_UP/commands/internal" "$CLAUDE_DIR/commands/internal"
fi

if [ -d "$LOCAL_DIR/commands" ]; then
    for f in "$LOCAL_DIR/commands/"*.md; do
        [ -f "$f" ] || continue
        ln -sfn "$REL_LOCAL_UP/commands/$(basename "$f")" "$CLAUDE_DIR/commands/$(basename "$f")"
    done
fi

# --- Skills ---
mkdir -p "$CLAUDE_DIR/skills"
find "$CLAUDE_DIR/skills" -maxdepth 1 -type l -delete 2>/dev/null || true

for d in "$KIT_SHARED/skills"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    [ "$name" = "internal" ] && continue
    ln -sfn "$REL_KIT_UP/skills/$name" "$CLAUDE_DIR/skills/$name"
done

if [ -d "$KIT_SHARED/skills/internal" ]; then
    ln -sfn "$REL_KIT_UP/skills/internal" "$CLAUDE_DIR/skills/internal"
fi

if [ -d "$LOCAL_DIR/skills" ]; then
    for d in "$LOCAL_DIR/skills"/*/; do
        [ -d "$d" ] || continue
        name=$(basename "$d")
        ln -sfn "$REL_LOCAL_UP/skills/$name" "$CLAUDE_DIR/skills/$name"
    done
fi

# --- Agents ---
mkdir -p "$CLAUDE_DIR/agents"
find "$CLAUDE_DIR/agents" -maxdepth 1 -type l -delete 2>/dev/null || true

for f in "$KIT_SHARED/agents/"*.md; do
    [ -f "$f" ] || continue
    ln -sfn "$REL_KIT_UP/agents/$(basename "$f")" "$CLAUDE_DIR/agents/$(basename "$f")"
done

if [ -d "$LOCAL_DIR/agents" ]; then
    for f in "$LOCAL_DIR/agents/"*.md; do
        [ -f "$f" ] || continue
        ln -sfn "$REL_LOCAL_UP/agents/$(basename "$f")" "$CLAUDE_DIR/agents/$(basename "$f")"
    done
fi

# --- Shared (bridge symlink so kit's internal paths resolve) ---
# The kit's settings.json references .claude/shared/hooks/telemetry-stamp.py.
# This symlink makes .claude/shared → .claude/kit/.claude/shared so those paths work.
rm -f "$CLAUDE_DIR/shared" 2>/dev/null || true
ln -sfn "$REL_KIT" "$CLAUDE_DIR/shared"

# --- Hooks (direct symlink to kit hooks directory) ---
rm -f "$CLAUDE_DIR/hooks" 2>/dev/null || true
ln -sfn "$REL_KIT/hooks" "$CLAUDE_DIR/hooks"

# --- Settings (direct symlink to kit settings.json) ---
rm -f "$CLAUDE_DIR/settings.json" 2>/dev/null || true
ln -sfn "$REL_KIT/settings.json" "$CLAUDE_DIR/settings.json"

echo "[claude-link] Assembly symlinks rebuilt."
echo "[claude-link]   commands: $(find "$CLAUDE_DIR/commands" -maxdepth 1 -type l | wc -l) links"
echo "[claude-link]   skills:   $(find "$CLAUDE_DIR/skills" -maxdepth 1 -type l | wc -l) links"
echo "[claude-link]   agents:   $(find "$CLAUDE_DIR/agents" -maxdepth 1 -type l | wc -l) links"
echo "[claude-link]   hooks:    symlink → $REL_KIT/hooks"
echo "[claude-link]   settings: symlink → $REL_KIT/settings.json"
