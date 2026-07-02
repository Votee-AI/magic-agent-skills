#!/usr/bin/env bash
#
# sync-main.sh — regenerate the clean `main` branch from `dev`.
#
# Internal artifacts (openspec/, .omc/, ref/, CLAUDE.local.md) live ONLY on the
# private `dev` branch. They are marked `export-ignore` in .gitattributes, so
# `git archive` omits them. This script exports dev's tree minus those paths and
# commits the result to `main`, guaranteeing `main` is free of internal content.
#
# NEVER update main with `git merge dev` — that would carry tracked internal
# files across. Always use this script.
#
# Usage:  scripts/sync-main.sh [source-ref]      (default source-ref: dev)
#
set -euo pipefail

SRC="${1:-dev}"

# Must be run from the repo root with a clean working tree.
cd "$(git rev-parse --show-toplevel)"
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: working tree is dirty. Commit or stash first." >&2
  exit 1
fi
git rev-parse --verify "$SRC" >/dev/null

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Export source tree WITHOUT export-ignored (internal) paths.
git archive "$SRC" | tar -x -C "$TMP"

git checkout main
# Replace tracked content with the clean export (removes files deleted on dev too).
git rm -rfq . >/dev/null 2>&1 || true
cp -R "$TMP"/. .
git add -A

if git diff --cached --quiet; then
  echo "main already in sync with '$SRC'. Nothing to commit."
  exit 0
fi

git commit -m "release: sync main from $SRC (clean export, internal content stripped)"
echo
echo "main synced from '$SRC'. Review:   git show --stat HEAD"
echo "Verify clean:  git ls-files | grep -E '^(openspec/|\\.omc/|ref/|features/|CLAUDE\\.local\\.md)'  # expect no output"
echo "Publish:       git push origin main && git push public main"
