# Publishing @votee-ai/magic-agent-skills to npm

## Architecture

The npm package is a **thin CLI installer** (~50KB). It does NOT bundle skills — skills are fetched from GitHub at runtime when users run `init` or `update`. This means skill updates don't require a new npm publish.

## Prerequisites

1. **npm account** with access to the `@votee-ai` scope
2. **Register the `@votee-ai` scope** on npmjs.com (one-time):
   - Go to https://www.npmjs.com/org/create → create the "votee-ai" organization
   - Or if it already exists, ensure your account is a member

3. **Login to npm**:
   ```bash
   npm login
   ```

## First Publish

```bash
cd cli

# 1. Build TypeScript
npm run build

# 2. Verify package contents (should be thin — bin + dist only, no skills)
npm pack --dry-run

# 3. Publish (public scoped package)
npm publish --access public
```

After publishing, anyone can install with:
```bash
# One-shot (no global install needed)
npx @votee-ai/magic-agent-skills init --tools claude,cursor

# Or install globally
npm install -g @votee-ai/magic-agent-skills
magic-agent-skills init --tools claude,cursor
```

## Updating (New Versions)

```bash
cd cli

# 1. Bump version
npm version patch   # 0.1.0 → 0.1.1
# or: npm version minor  # 0.1.0 → 0.2.0
# or: npm version major  # 0.1.0 → 1.0.0

# 2. Publish
npm publish

# 3. Tag the release in git
git tag v$(node -p "require('./package.json').version")
git push --tags
```

## Verifying a Published Version

```bash
# Check what's on npm
npm info @votee-ai/magic-agent-skills

# Test the npx experience (uses published package)
cd /tmp && mkdir test-dir && cd test-dir
npx @votee-ai/magic-agent-skills init --tools claude
```

## Local Development

While developing, use `npm link` so changes are reflected immediately:

```bash
cd cli
npm run build          # rebuild after source changes
npm link               # one-time: creates global symlink
magic-agent-skills init --tools claude  # uses local build
```

To unlink:
```bash
npm unlink -g @votee-ai/magic-agent-skills
```

## Note on copy-skills.sh

`scripts/copy-skills.sh` is used by CI only (for testing the skill bundle structure). It is NOT used for npm publishing — the published package contains only the CLI tool, not skills.
