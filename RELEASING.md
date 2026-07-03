# Releasing

## Versioning Policy

This repository uses **2-tier semantic versioning**:

### Repo Version (npm package)

The npm package `@votee-ai/magic-agent-skills` follows [semver](https://semver.org/):

- **MAJOR** — Breaking changes to skill schema, CLI interface, or removed skills
- **MINOR** — New skills added, new metadata fields, CLI features
- **PATCH** — Skill content updates, bug fixes, documentation

### Skill Version

Each skill has its own `metadata.version` in SKILL.md frontmatter. Skill versions are informational and track content changes independently of the repo version.

## Release Process

Releases are triggered by git tags:

```bash
# 1. Update version in cli/package.json
# 2. Update version in .claude-plugin/marketplace.json metadata
# 3. Commit and tag
git tag v1.0.0
git push origin v1.0.0
```

The `release.yml` workflow automatically:

1. Runs the full CI suite (8 jobs)
2. Builds the CLI (`npm run build`)
3. Verifies tag version matches `cli/package.json` version
4. Publishes the thin CLI to npm with `--provenance`
5. Creates a GitHub Release with install instructions

Note: The npm package is a thin installer — skills are fetched from GitHub at runtime, not bundled.

## Branch Protection

`main` is the protected release branch — all releases are tagged from it. Branch protection
requires the CI suite to pass before changes land, and changes are reviewed via pull request
before merge.

## Checklist Before Release

- [ ] All CI jobs pass on `main`
- [ ] Schema validation passes for all 30 skills
- [ ] CLI tests pass
- [ ] Marketplace.json paths all resolve
- [ ] Version bumped in `cli/package.json` and `.claude-plugin/marketplace.json`
- [ ] CHANGELOG updated (if maintained)
