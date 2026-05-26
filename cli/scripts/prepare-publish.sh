#!/bin/bash
# Bundles skills and commands into the CLI package for npm publishing.
# Run automatically via prepublishOnly in package.json.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$CLI_DIR/.." && pwd)"

echo "Bundling skills and commands into CLI package..."

# Copy skills
rm -rf "$CLI_DIR/skills"
cp -r "$REPO_ROOT/skills" "$CLI_DIR/skills"

# Remove eval artifacts, test data, and cache from npm bundle
find "$CLI_DIR/skills" -type d -name "evals" -exec rm -rf {} + 2>/dev/null || true
find "$CLI_DIR/skills" -type d -name "test-workspace" -exec rm -rf {} + 2>/dev/null || true
find "$CLI_DIR/skills" -type d -name ".cache" -exec rm -rf {} + 2>/dev/null || true
find "$CLI_DIR/skills" -type d -name ".omc" -exec rm -rf {} + 2>/dev/null || true
find "$CLI_DIR/skills" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Copy commands (from workspace if commands/ at root doesn't exist yet)
rm -rf "$CLI_DIR/commands"
mkdir -p "$CLI_DIR/commands/magic"

if [ -d "$REPO_ROOT/commands/magic" ]; then
  cp "$REPO_ROOT/commands/magic/"*.md "$CLI_DIR/commands/magic/"
elif [ -d "$REPO_ROOT/workspace/.claude/commands/magic" ]; then
  cp "$REPO_ROOT/workspace/.claude/commands/magic/"*.md "$CLI_DIR/commands/magic/"
else
  echo "ERROR: No command files found" >&2
  exit 1
fi

SKILL_COUNT=$(ls -d "$CLI_DIR/skills/magic-"* 2>/dev/null | wc -l | tr -d ' ')
CMD_COUNT=$(ls "$CLI_DIR/commands/magic/"*.md 2>/dev/null | wc -l | tr -d ' ')

echo "Bundled $SKILL_COUNT skills, $CMD_COUNT commands"
