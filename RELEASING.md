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

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable release branch. All releases are tagged from here. **Protected** (see below). |
| `dev` | Integration branch. PRs merge here first. |
| `feat/*` | Feature branches for new skills or changes. |

### `main` branch protection

`main` is **generated** from `dev` by `scripts/sync-main.sh` (a clean `git archive` that
strips `export-ignore`d internal paths). It must be branch-protected so nothing bypasses
the sync + the `no-internal-content` CI guard. Required settings (configure via the GitHub
repo UI, or the `gh` command below):

- **Require status checks to pass** before merge, including at minimum:
  `no-internal-content`, `license-check`, `schema-validation`, `package-content`, `unit-tests`,
  `cli-tests`.
- **Restrict who can push** to `main` (maintainers only); require PR review for everyone else.
- **Block force-pushes** except via the sanctioned `sync-main.sh` flow (a maintainer may
  force-push a freshly-generated `main` after running the script; this is the only sanctioned
  direct-write path).

```bash
# Example: require the no-internal-content check on main (run once, admin).
gh api -X PUT repos/Votee-AI/magic-agent-skills/branches/main/protection \
  -F required_status_checks[strict]=true \
  -F required_status_checks[contexts][]=no-internal-content \
  -F required_status_checks[contexts][]=license-check \
  -F enforce_admins=false \
  -F restrictions= \
  -F required_pull_request_reviews=
```

> Branch protection is a **GitHub repo-admin action** (not a file in the repo). The above is
> the documented target state for maintainers; the guards themselves live in
> `scripts/sync-main.sh` and `.github/workflows/ci.yml` (the `no-internal-content` job checks
> for `openspec/ | .omc/ | ref/ | features/ | CLAUDE.local.md`).

## Checklist Before Release

- [ ] All CI jobs pass on `main`
- [ ] Schema validation passes for all 30 skills
- [ ] CLI tests pass
- [ ] Marketplace.json paths all resolve
- [ ] Version bumped in `cli/package.json` and `.claude-plugin/marketplace.json`
- [ ] CHANGELOG updated (if maintained)

## Dual-Repo Sync

This repository (`votee/magic-agent-skills`, `origin`) is the private development repo. Public
releases are pushed to `Votee-AI/magic-agent-skills` (`public`). `main` is **generated** from
`dev` — never `git merge dev` into `main`. The only sanctioned way to update `main` is:

```bash
# Regenerate a clean main from dev (strips export-ignored internal paths via git archive).
scripts/sync-main.sh        # commits a clean main from dev
git show --stat HEAD        # review the generated tree
git push origin main        # then, when ready:
git push public main
```

Internal planning content (`openspec/`, `.omc/`, `ref/`, `features/`, `CLAUDE.local.md`) is
excluded from `main` via `.gitattributes` `export-ignore` (read by `git archive` inside
`sync-main.sh`). **Verify cleanliness after every sync**:

```bash
git ls-files | grep -E '^(openspec/|\.omc/|ref/|features/|CLAUDE\.local\.md)'   # expect no output
```
