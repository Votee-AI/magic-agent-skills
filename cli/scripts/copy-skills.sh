#!/usr/bin/env bash
set -e
CLI_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$CLI_DIR/.." && pwd)"

echo "Copying skills from repo root into CLI package..."
rm -rf "$CLI_DIR/skills" "$CLI_DIR/commands"
cp -r "$REPO_ROOT/skills" "$CLI_DIR/skills"
cp -r "$REPO_ROOT/commands" "$CLI_DIR/commands"

# Strip build artifacts and test data
find "$CLI_DIR/skills" -name "*.pyc" -delete
find "$CLI_DIR/skills" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$CLI_DIR/skills" -name ".cache" -type d -exec rm -rf {} + 2>/dev/null || true
find "$CLI_DIR/skills" -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
find "$CLI_DIR/skills" -name "evals" -type d -exec rm -rf {} + 2>/dev/null || true

# Generate skills/manifest.json
node -e "
  const fs = require('fs');
  const path = require('path');
  const skillsDir = path.join('$CLI_DIR', 'skills');
  const dirs = fs.readdirSync(skillsDir).filter(d =>
    fs.statSync(path.join(skillsDir, d)).isDirectory() && !d.startsWith('_')
  );
  // Most-specific-first: magic-linguistic-* must be matched before the data magic-* rule.
  const lingSkills = dirs.filter(d => d.startsWith('magic-linguistic-'));
  const dataSkills = dirs.filter(d => d.startsWith('magic-') && !d.startsWith('magic-linguistic-'));
  const manifest = {
    suites: {
      data: { skills: dataSkills.sort() },
      linguistic: { skills: lingSkills.sort() }
    }
  };
  fs.writeFileSync(path.join(skillsDir, 'manifest.json'), JSON.stringify(manifest, null, 2));
  console.log('Generated manifest.json:', dataSkills.length, 'data skills,', lingSkills.length, 'linguistic skills');
"

echo "Done. CLI package ready for publish."
