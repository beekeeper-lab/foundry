#!/usr/bin/env bash
# kit-contribute.sh — Contribute a kit change upstream via branch + PR.
#
# The submodule publish path (claude-publish.sh) requires push rights to
# beekeeper-lab/claude-kit and is Foundry-maintainer-only. This script is
# the downstream path (ADR-016): it takes committed or uncommitted changes
# in .claude/shared/, puts them on a fresh branch off origin/main, pushes
# (forking via gh when you lack push rights), and opens a PR.
#
# Usage:
#   scripts/kit-contribute.sh "<branch-suffix>" ["<PR title>"]
# Example:
#   scripts/kit-contribute.sh fix-telemetry-race "Fix telemetry checkpoint race"
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
KIT_DIR="$REPO_ROOT/.claude/shared"
UPSTREAM_REPO="beekeeper-lab/claude-kit"

SUFFIX="${1:?usage: kit-contribute.sh <branch-suffix> [pr-title]}"
TITLE="${2:-Kit contribution: $SUFFIX}"
BRANCH="contrib/$SUFFIX"

if ! command -v gh >/dev/null 2>&1; then
    echo "ERROR: gh CLI is required (https://cli.github.com)." >&2
    exit 1
fi
if [ ! -e "$KIT_DIR/.git" ]; then
    echo "ERROR: $KIT_DIR is not a git submodule checkout." >&2
    exit 1
fi

cd "$KIT_DIR"
git fetch origin main

# Capture work: uncommitted changes are stashed and replayed onto the new
# branch; committed-but-unpushed work is carried by branching from HEAD.
STASHED=0
if [ -n "$(git status --porcelain)" ]; then
    git stash push -u -m "kit-contribute: $SUFFIX"
    STASHED=1
fi

START_POINT="HEAD"
# On a pristine detached HEAD at origin/main, branch from origin/main so the
# PR diff is exactly this contribution.
if [ -z "$(git branch --show-current)" ] && \
   [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then
    START_POINT="origin/main"
fi

git checkout -b "$BRANCH" "$START_POINT"
if [ "$STASHED" = 1 ]; then
    git stash pop
    git add -A
    git commit -m "$TITLE"
fi

if [ -z "$(git log origin/main..HEAD --oneline)" ]; then
    echo "ERROR: no commits to contribute (nothing ahead of origin/main)." >&2
    exit 1
fi

# Push directly when permitted; otherwise fork and push there.
if git push -u origin "$BRANCH" 2>/dev/null; then
    HEAD_REF="$BRANCH"
else
    echo "No push rights to $UPSTREAM_REPO — forking."
    gh repo fork "$UPSTREAM_REPO" --remote --remote-name fork
    git push -u fork "$BRANCH"
    HEAD_REF="$(gh api user --jq .login):$BRANCH"
fi

gh pr create \
    --repo "$UPSTREAM_REPO" \
    --head "$HEAD_REF" \
    --title "$TITLE" \
    --body "Contributed from $(basename "$REPO_ROOT") via kit-contribute.sh (ADR-016)."

echo "PR opened. Once merged, consuming repos pick it up via scripts/claude-sync.sh after a submodule bump."
