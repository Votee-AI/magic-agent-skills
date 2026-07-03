<!--
Thank you for contributing to MAGIC Agent Skills! By submitting this PR you agree your
contribution is licensed under Apache-2.0 (inbound=outbound). See CONTRIBUTING.md.
Recommended: sign off commits with `git commit -s` (DCO).
-->

## Summary

<!-- What does this PR change, and why? Link the issue(s): Fixes #123 -->

## Type

<!-- Check one: -->
- [ ] `type: bug`
- [ ] `type: feature`
- [ ] `type: docs`
- [ ] `type: refactor`
- [ ] `type: test`
- [ ] `type: chore`
- [ ] `type: skill-proposal`

## Checklist — please verify before requesting review

These mirror the CI jobs in `.github/workflows/ci.yml`. Tick what you've done.

- [ ] **No internal content** — I did not add anything under `openspec/`, `.omc/`, `ref/`, `features/`, or `CLAUDE.local.md` (these are private and never ship).
- [ ] **License-clean** — no GPL / AGPL / SSPL / BUSL / Commons-Clause dependencies added.
- [ ] **Schema-valid** — any changed `SKILL.md` frontmatter validates against `schema/SKILL.schema.json` (`ajv` / `python -c` frontmatter parse).
- [ ] **Thin CLI** — the published package stays thin: no `skills/` or `commands/` bundled into `cli/` (the CLI fetches at install time).
- [ ] **Tests** — ran the relevant suite:
  - Skills: `MPLBACKEND=Agg python -m pytest tests/shared tests/data-agent tests/linguistic`
  - CLI: `cd cli && npm ci && npm run build && npm test`
- [ ] **Docs updated** — README / per-skill README / ENV_VARS / ROADMAP updated if behavior changed.

## Notes for reviewers

<!-- Anything special? Breaking changes? Migration steps? -->
